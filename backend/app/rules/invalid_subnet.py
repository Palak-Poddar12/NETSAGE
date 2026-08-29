import ipaddress
from typing import Dict, Any, List
from app.rules.base import BaseRule
from app.schemas.rule_finding import RuleFinding

class InvalidSubnetRule(BaseRule):
    rule_id = "invalid_subnet"
    rule_name = "Invalid Subnet / Host Boundary Check"
    description = "Validates subnet masks and checks if host IP addresses are assigned to network or broadcast boundaries."

    def evaluate(
        self,
        topology: Dict[str, Any],
        addressing: List[Dict[str, Any]],
        show_outputs: Dict[str, Any]
    ) -> RuleFinding:
        violations = []
        affected_devices = set()
        affected_interfaces = set()

        for item in addressing:
            dev = item.get("device", "Unknown")
            intf = item.get("interface", "Unknown")
            ip_str = item.get("ip_address")
            mask_str = item.get("subnet_mask")

            if not ip_str:
                continue

            try:
                # Handle CIDR or dotted decimal mask
                if "/" in ip_str:
                    interface_obj = ipaddress.IPv4Interface(ip_str)
                elif mask_str:
                    interface_obj = ipaddress.IPv4Interface(f"{ip_str}/{mask_str}")
                else:
                    # Default /24 if neither provided
                    interface_obj = ipaddress.IPv4Interface(f"{ip_str}/24")

                network = interface_obj.network
                ip_addr = interface_obj.ip

                # Check if mask prefix is invalid
                if network.prefixlen > 30 and network.prefixlen < 32:
                    # /31 point-to-point is RFC 3021, but let's check standard /32 or invalid host
                    pass

                # Check if host IP is network address on subnets <= /30
                if network.prefixlen <= 30 and ip_addr == network.network_address:
                    violations.append(
                        f"{dev}:{intf} has IP {ip_addr} which matches the subnet network address ({network.network_address}/{network.prefixlen})"
                    )
                    affected_devices.add(dev)
                    affected_interfaces.add(f"{dev}:{intf}")

                # Check if host IP is broadcast address on subnets <= /30
                elif network.prefixlen <= 30 and ip_addr == network.broadcast_address:
                    violations.append(
                        f"{dev}:{intf} has IP {ip_addr} which matches the subnet broadcast address ({network.broadcast_address}/{network.prefixlen})"
                    )
                    affected_devices.add(dev)
                    affected_interfaces.add(f"{dev}:{intf}")

            except ValueError as e:
                violations.append(f"{dev}:{intf} has an invalid IP/mask configuration ({ip_str}, {mask_str}): {str(e)}")
                affected_devices.add(dev)
                affected_interfaces.add(f"{dev}:{intf}")

        if violations:
            return RuleFinding(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=False,
                severity="high",
                details=f"Subnet configuration errors found: {'; '.join(violations)}.",
                affected_devices=sorted(list(affected_devices)),
                affected_interfaces=sorted(list(affected_interfaces)),
                evidence={"violations": violations}
            )

        return RuleFinding(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=True,
            severity="info",
            details="All host IP addresses and subnet masks are valid.",
            affected_devices=[],
            affected_interfaces=[],
            evidence=None
        )
