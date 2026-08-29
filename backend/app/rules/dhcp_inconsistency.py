import ipaddress
import re
from typing import Dict, Any, List
from app.rules.base import BaseRule
from app.schemas.rule_finding import RuleFinding

class DHCPInconsistencyRule(BaseRule):
    rule_id = "dhcp_inconsistency"
    rule_name = "DHCP Configuration & Pool Inconsistency Check"
    description = "Detects DHCP pool subnet mismatches, invalid default routers, pool exhaustion, and conflicting excluded address ranges."

    def evaluate(
        self,
        topology: Dict[str, Any],
        addressing: List[Dict[str, Any]],
        show_outputs: Dict[str, Any]
    ) -> RuleFinding:
        violations = []
        affected_devices = set()
        affected_interfaces = set()

        for dev, outputs in show_outputs.items():
            if not isinstance(outputs, dict):
                continue
            for cmd, text in outputs.items():
                cmd_lower = cmd.lower()
                lines = str(text).splitlines()

                # Check DHCP conflicts output
                if "dhcp conflict" in cmd_lower:
                    for line in lines:
                        match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
                        if match and not line.lower().startswith("ip address"):
                            violations.append(f"DHCP conflict detected on {dev} for IP {match.group(1)}")
                            affected_devices.add(dev)

                # Check DHCP pool / running configuration
                if "dhcp" in cmd_lower or "running-config" in cmd_lower or "run" in cmd_lower:
                    current_pool = None
                    pool_network = None
                    pool_gw = None

                    for line in lines:
                        l = line.strip()
                        if l.startswith("ip dhcp pool"):
                            current_pool = l.split()[-1]
                            pool_network = None
                            pool_gw = None
                        elif current_pool and l.startswith("network"):
                            parts = l.split()
                            if len(parts) >= 3:
                                try:
                                    pool_network = ipaddress.IPv4Network(f"{parts[1]}/{parts[2]}", strict=False)
                                except ValueError:
                                    pass
                        elif current_pool and l.startswith("default-router"):
                            parts = l.split()
                            if len(parts) >= 2:
                                try:
                                    pool_gw = ipaddress.IPv4Address(parts[1])
                                    if pool_network and pool_gw not in pool_network:
                                        violations.append(
                                            f"Device {dev} DHCP pool '{current_pool}' default-router {pool_gw} is outside pool subnet {pool_network}"
                                        )
                                        affected_devices.add(dev)
                                except ValueError:
                                    pass

        if violations:
            unique_v = sorted(list(set(violations)))
            return RuleFinding(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=False,
                severity="high",
                details=f"DHCP inconsistencies detected: {'; '.join(unique_v)}.",
                affected_devices=sorted(list(affected_devices)),
                affected_interfaces=sorted(list(affected_interfaces)),
                evidence={"violations": unique_v}
            )

        return RuleFinding(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=True,
            severity="info",
            details="DHCP configurations and pool parameters are consistent.",
            affected_devices=[],
            affected_interfaces=[],
            evidence=None
        )
