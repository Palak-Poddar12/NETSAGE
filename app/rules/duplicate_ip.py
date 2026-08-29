import ipaddress
import re
from typing import Dict, Any, List
from app.rules.base import BaseRule
from app.schemas.rule_finding import RuleFinding

def canonical_intf(name: str) -> str:
    if not name:
        return ""
    n = name.strip()
    match = re.match(r"^([A-Za-z\-]+)\s*([\d\/\.\:]+)?$", n)
    if not match:
        return n.lower()
    prefix = match.group(1).lower()
    port = match.group(2) or ""

    if prefix.startswith("gi") or prefix.startswith("gig"):
        p = "gig"
    elif prefix.startswith("fa") or prefix.startswith("fast"):
        p = "fa"
    elif prefix.startswith("te") or prefix.startswith("ten"):
        p = "te"
    elif prefix.startswith("twe") or prefix.startswith("twenty"):
        p = "twe"
    elif prefix.startswith("hu") or prefix.startswith("hundred"):
        p = "hu"
    elif prefix.startswith("eth") or prefix == "e":
        p = "eth"
    elif prefix.startswith("se") or prefix.startswith("ser"):
        p = "ser"
    elif prefix.startswith("lo") or prefix.startswith("loop"):
        p = "lo"
    elif prefix.startswith("vl"):
        p = "vlan"
    elif prefix.startswith("po"):
        p = "po"
    else:
        p = prefix
    return f"{p}{port}"

class DuplicateIPRule(BaseRule):
    rule_id = "duplicate_ip"
    rule_name = "Duplicate IP Address Check"
    description = "Checks for identical IPv4 addresses assigned across multiple devices or interfaces."

    def evaluate(
        self,
        topology: Dict[str, Any],
        addressing: List[Dict[str, Any]],
        show_outputs: Dict[str, Any]
    ) -> RuleFinding:
        ip_map: Dict[str, List[Dict[str, str]]] = {}
        affected_devices = set()
        affected_interfaces = set()

        # Check addressing table
        for item in addressing:
            ip_str = item.get("ip_address")
            if not ip_str:
                continue
            raw_ip = ip_str.split("/")[0].strip()
            try:
                ip_obj = ipaddress.IPv4Address(raw_ip)
                if ip_obj.is_loopback or ip_obj.is_multicast or raw_ip in ("0.0.0.0", "unassigned"):
                    continue
                dev = item.get("device", "Unknown").strip()
                intf = item.get("interface", "Unknown").strip()
                canon = canonical_intf(intf)
                entry = {"device": dev, "interface": intf, "canon": canon}
                ip_map.setdefault(raw_ip, []).append(entry)
            except ValueError:
                continue

        # Also inspect show_ip_interface_brief or show_ip_interface in show_outputs
        for dev, outputs in show_outputs.items():
            if not isinstance(outputs, dict):
                continue
            for cmd, text in outputs.items():
                if "ip_interface" in cmd or "ip int br" in cmd:
                    for line in str(text).splitlines():
                        match = re.search(r"^(\S+)\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line.strip())
                        if match:
                            intf_name = match.group(1).strip()
                            raw_ip = match.group(2).strip()
                            if raw_ip != "unassigned":
                                canon = canonical_intf(intf_name)
                                existing = ip_map.get(raw_ip, [])
                                is_duplicate_record = any(
                                    e["device"].lower() == dev.lower() and e.get("canon", "").lower() == canon.lower()
                                    for e in existing
                                )
                                if not is_duplicate_record:
                                    ip_map.setdefault(raw_ip, []).append({
                                        "device": dev,
                                        "interface": intf_name,
                                        "canon": canon
                                    })

        duplicates = {}
        for ip, locs in ip_map.items():
            unique_pairs = set((loc["device"].lower(), loc.get("canon", "").lower()) for loc in locs)
            if len(unique_pairs) > 1:
                duplicates[ip] = locs

        if duplicates:
            duplicate_details = []
            for ip, locs in duplicates.items():
                loc_strings = [f"{loc['device']}:{loc['interface']}" for loc in locs]
                for loc in locs:
                    affected_devices.add(loc["device"])
                    affected_interfaces.add(f"{loc['device']}:{loc['interface']}")
                duplicate_details.append(f"IP {ip} configured on [{', '.join(loc_strings)}]")

            return RuleFinding(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=False,
                severity="critical",
                details=f"Duplicate IP address conflict detected: {'; '.join(duplicate_details)}.",
                affected_devices=sorted(list(affected_devices)),
                affected_interfaces=sorted(list(affected_interfaces)),
                evidence={"duplicates": duplicates}
            )

        return RuleFinding(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=True,
            severity="info",
            details="No duplicate IP addresses detected across active inventory.",
            affected_devices=[],
            affected_interfaces=[],
            evidence=None
        )
