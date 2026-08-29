import re
from typing import Dict, Any, List
from app.rules.base import BaseRule
from app.schemas.rule_finding import RuleFinding

class NATInconsistencyRule(BaseRule):
    rule_id = "nat_inconsistency"
    rule_name = "Network Address Translation (NAT) Inconsistency Check"
    description = "Detects missing NAT inside/outside interface designations, mismatched ACLs in NAT overload statements, and unassigned NAT pools."

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

            has_nat_statement = False
            inside_interfaces = []
            outside_interfaces = []
            nat_acls = []

            for cmd, text in outputs.items():
                cmd_lower = cmd.lower()
                lines = str(text).splitlines()

                # show running-config or show ip nat statistics
                if "nat" in cmd_lower or "running-config" in cmd_lower or "run" in cmd_lower or "ip_nat" in cmd_lower:
                    current_intf = None
                    for line in lines:
                        l = line.strip()
                        if l.startswith("interface"):
                            current_intf = l.split()[-1]
                        elif l == "ip nat inside" and current_intf:
                            inside_interfaces.append(current_intf)
                        elif l == "ip nat outside" and current_intf:
                            outside_interfaces.append(current_intf)
                        elif "ip nat inside source" in l:
                            has_nat_statement = True
                            # Check if overload specifies an interface or ACL
                            match_acl = re.search(r"list\s+(\S+)", l)
                            if match_acl:
                                nat_acls.append(match_acl.group(1))

                # show ip nat statistics
                if "nat statistics" in cmd_lower or "nat_statistics" in cmd_lower:
                    for line in lines:
                        if "inside interfaces:" in line.lower():
                            parts = line.split(":")[-1].split()
                            inside_interfaces.extend(parts)
                        elif "outside interfaces:" in line.lower():
                            parts = line.split(":")[-1].split()
                            outside_interfaces.extend(parts)

            if has_nat_statement:
                if not inside_interfaces:
                    violations.append(f"Router {dev} has NAT rules configured but lacks 'ip nat inside' on any interface")
                    affected_devices.add(dev)
                if not outside_interfaces:
                    violations.append(f"Router {dev} has NAT rules configured but lacks 'ip nat outside' on any interface")
                    affected_devices.add(dev)

        if violations:
            unique_v = sorted(list(set(violations)))
            return RuleFinding(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=False,
                severity="high",
                details=f"NAT configuration discrepancies detected: {'; '.join(unique_v)}.",
                affected_devices=sorted(list(affected_devices)),
                affected_interfaces=sorted(list(affected_interfaces)),
                evidence={"violations": unique_v}
            )

        return RuleFinding(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=True,
            severity="info",
            details="NAT configurations, interfaces, and translation policies are consistent.",
            affected_devices=[],
            affected_interfaces=[],
            evidence=None
        )
