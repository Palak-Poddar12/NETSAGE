import re
from typing import Dict, Any, List, Set
from app.rules.base import BaseRule
from app.schemas.rule_finding import RuleFinding

class MissingVLANRule(BaseRule):
    rule_id = "missing_vlan"
    rule_name = "Missing or Inactive VLAN Check"
    description = "Detects access ports or hosts configured for VLANs that do not exist or are suspended in the switch VLAN database."

    def evaluate(
        self,
        topology: Dict[str, Any],
        addressing: List[Dict[str, Any]],
        show_outputs: Dict[str, Any]
    ) -> RuleFinding:
        violations = []
        affected_devices = set()
        affected_interfaces = set()

        # Parse VLAN databases per switch from show_vlan_brief / show_vlan
        switch_vlans: Dict[str, Set[int]] = {}
        for dev, outputs in show_outputs.items():
            if not isinstance(outputs, dict):
                continue
            active_vlans = set()
            for cmd, text in outputs.items():
                if "vlan" in cmd.lower() and "trunk" not in cmd.lower():
                    for line in str(text).splitlines():
                        match = re.match(r"^(\d+)\s+(\S+)\s+(active|act/unsup|suspend)", line.strip(), re.IGNORECASE)
                        if match:
                            vlan_id = int(match.group(1))
                            status = match.group(3).lower()
                            if status == "active":
                                active_vlans.add(vlan_id)
            if active_vlans:
                switch_vlans[dev] = active_vlans

        # If switch_vlans parsed, verify access ports from show_interfaces_status
        for dev, outputs in show_outputs.items():
            if not isinstance(outputs, dict) or dev not in switch_vlans:
                continue
            known_active = switch_vlans[dev]
            for cmd, text in outputs.items():
                if "interfaces_status" in cmd.lower() or "interface status" in cmd.lower():
                    for line in str(text).splitlines():
                        parts = line.strip().split()
                        # e.g.: Gi0/1 connected 10 a-full a-1000
                        if len(parts) >= 3 and parts[2].isdigit():
                            port = parts[0]
                            vlan_id = int(parts[2])
                            if vlan_id not in known_active:
                                violations.append(
                                    f"Switch {dev} port {port} assigned to VLAN {vlan_id}, but VLAN {vlan_id} does not exist in the VLAN database"
                                )
                                affected_devices.add(dev)
                                affected_interfaces.add(f"{dev}:{port}")

        # Also check addressing table against switch VLANs if host is connected to switch
        for item in addressing:
            vlan_val = item.get("vlan")
            if vlan_val is None:
                continue
            try:
                vlan_id = int(vlan_val)
            except ValueError:
                continue

            dev = item.get("device", "Unknown")
            intf = item.get("interface", "Unknown")

            # Check if any switch that this host connects to is missing this VLAN
            for sw_name, active_vlans in switch_vlans.items():
                # If host connected to sw_name via links in topology
                links = topology.get("links", [])
                is_connected = any(
                    (l.get("source") == dev and l.get("target") == sw_name) or
                    (l.get("target") == dev and l.get("source") == sw_name)
                    for l in links
                )
                if is_connected and vlan_id not in active_vlans:
                    violations.append(
                        f"Host {dev}:{intf} is configured on VLAN {vlan_id}, but connected switch {sw_name} lacks VLAN {vlan_id} in active database"
                    )
                    affected_devices.add(sw_name)
                    affected_devices.add(dev)
                    affected_interfaces.add(f"{dev}:{intf}")

        if violations:
            unique_v = sorted(list(set(violations)))
            return RuleFinding(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=False,
                severity="high",
                details=f"Missing VLAN configuration issues detected: {'; '.join(unique_v)}.",
                affected_devices=sorted(list(affected_devices)),
                affected_interfaces=sorted(list(affected_interfaces)),
                evidence={"violations": unique_v}
            )

        return RuleFinding(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=True,
            severity="info",
            details="All assigned VLANs are present and active in the switch database.",
            affected_devices=[],
            affected_interfaces=[],
            evidence=None
        )
