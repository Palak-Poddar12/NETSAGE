import re
from typing import Dict, Any, List
from app.rules.base import BaseRule
from app.schemas.rule_finding import RuleFinding

class ACLDenyRule(BaseRule):
    rule_id = "acl_deny"
    rule_name = "Access Control List (ACL) Traffic Drop Check"
    description = "Detects packet drops caused by explicit or implicit ACL deny statements and active match hit counters."

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
                if "access-list" in cmd_lower or "access_list" in cmd_lower or "acl" in cmd_lower:
                    lines = str(text).splitlines()
                    current_acl = "ACL"
                    for line in lines:
                        line_str = line.strip()
                        if line_str.lower().startswith("extended ip access list") or line_str.lower().startswith("standard ip access list") or line_str.lower().startswith("ip access-list"):
                            current_acl = line_str.split()[-1]
                        elif "deny" in line_str.lower():
                            # Check if matches counter is present e.g. (142 matches)
                            match_count = re.search(r"\((\d+)\s+matches?\)", line_str, re.IGNORECASE)
                            if match_count and int(match_count.group(1)) > 0:
                                violations.append(
                                    f"Device {dev} ACL '{current_acl}' active deny rule: '{line_str}' ({match_count.group(1)} packets dropped)"
                                )
                                affected_devices.add(dev)
                            elif "matches" not in line_str and ("deny ip any any" in line_str.lower() or "deny any" in line_str.lower() or "deny tcp" in line_str.lower() or "deny udp" in line_str.lower()):
                                # If there's an explicit deny rule filtering traffic
                                violations.append(
                                    f"Device {dev} ACL '{current_acl}' contains blocking deny rule: '{line_str}'"
                                )
                                affected_devices.add(dev)

        if violations:
            unique_v = sorted(list(set(violations)))
            return RuleFinding(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=False,
                severity="high",
                details=f"ACL packet filtering drops detected: {'; '.join(unique_v)}.",
                affected_devices=sorted(list(affected_devices)),
                affected_interfaces=sorted(list(affected_interfaces)),
                evidence={"violations": unique_v}
            )

        return RuleFinding(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=True,
            severity="info",
            details="No ACL deny drops or restrictive access-list conflicts detected.",
            affected_devices=[],
            affected_interfaces=[],
            evidence=None
        )
