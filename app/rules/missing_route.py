import ipaddress
import re
from typing import Dict, Any, List
from app.rules.base import BaseRule
from app.schemas.rule_finding import RuleFinding

class MissingRouteRule(BaseRule):
    rule_id = "missing_route"
    rule_name = "Missing Route in Routing Table Check"
    description = "Verifies that routers possess valid routes (connected, static, dynamic, or default) to reach destination subnets."

    def evaluate(
        self,
        topology: Dict[str, Any],
        addressing: List[Dict[str, Any]],
        show_outputs: Dict[str, Any]
    ) -> RuleFinding:
        violations = []
        affected_devices = set()
        affected_interfaces = set()

        # Collect target networks from addressing
        target_networks = set()
        for item in addressing:
            ip_str = item.get("ip_address")
            mask_str = item.get("subnet_mask")
            if not ip_str:
                continue
            try:
                if "/" in ip_str:
                    net = ipaddress.IPv4Interface(ip_str).network
                elif mask_str:
                    net = ipaddress.IPv4Interface(f"{ip_str}/{mask_str}").network
                else:
                    net = ipaddress.IPv4Interface(f"{ip_str}/24").network
                target_networks.add(net)
            except ValueError:
                pass

        # Parse routing tables per router
        for dev, outputs in show_outputs.items():
            if not isinstance(outputs, dict):
                continue
            routes: List[ipaddress.IPv4Network] = []
            has_default_route = False

            for cmd, text in outputs.items():
                if "ip_route" in cmd.lower() or "ip route" in cmd.lower():
                    lines = str(text).splitlines()
                    for line in lines:
                        # Detect default route
                        if "0.0.0.0/0" in line or "default" in line.lower() or "gateway of last resort" in line.lower():
                            if "not set" not in line.lower():
                                has_default_route = True

                        # Find subnets like 192.168.1.0/24 or 10.0.0.0/8
                        match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:/\d{1,2})?)", line)
                        if match:
                            candidate = match.group(1)
                            try:
                                if "/" in candidate:
                                    r_net = ipaddress.IPv4Network(candidate, strict=False)
                                else:
                                    r_net = ipaddress.IPv4Network(f"{candidate}/24", strict=False)
                                if r_net.prefixlen == 0:
                                    has_default_route = True
                                else:
                                    routes.append(r_net)
                            except ValueError:
                                pass

            # Only check routers that have a routing table in show_outputs
            if routes or has_default_route:
                for target_net in target_networks:
                    # Check if target_net is covered by any route or default route
                    is_covered = has_default_route or any(
                        target_net.subnet_of(r) or r.subnet_of(target_net) or target_net == r
                        for r in routes
                    )
                    if not is_covered:
                        violations.append(
                            f"Router {dev} has no routing table entry or default route for destination network {target_net}"
                        )
                        affected_devices.add(dev)

        if violations:
            unique_v = sorted(list(set(violations)))
            return RuleFinding(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=False,
                severity="high",
                details=f"Missing routing table entries detected: {'; '.join(unique_v)}.",
                affected_devices=sorted(list(affected_devices)),
                affected_interfaces=[],
                evidence={"violations": unique_v}
            )

        return RuleFinding(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=True,
            severity="info",
            details="All destination subnets have valid routes in routing tables.",
            affected_devices=[],
            affected_interfaces=[],
            evidence=None
        )
