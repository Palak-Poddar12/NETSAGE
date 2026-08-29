import ipaddress
from typing import Dict, Any, List
from app.rules.base import BaseRule
from app.schemas.rule_finding import RuleFinding

class GatewayMismatchRule(BaseRule):
    rule_id = "gateway_mismatch"
    rule_name = "Default Gateway Subnet & Reachability Check"
    description = "Verifies that default gateways reside within the host's local subnet and match active router interfaces."

    def evaluate(
        self,
        topology: Dict[str, Any],
        addressing: List[Dict[str, Any]],
        show_outputs: Dict[str, Any]
    ) -> RuleFinding:
        violations = []
        affected_devices = set()
        affected_interfaces = set()

        # Collect all router / gateway interfaces in the network
        router_ips = set()
        for item in addressing:
            dev = item.get("device", "")
            ip_str = item.get("ip_address")
            if not ip_str:
                continue
            raw_ip = ip_str.split("/")[0].strip()
            # If device name contains Router / R1 / GW or has no default gateway of its own
            if any(k in dev.lower() for k in ["r1", "r2", "r3", "router", "gw", "core", "gateway"]) or item.get("default_gateway") is None:
                router_ips.add(raw_ip)

        for item in addressing:
            dev = item.get("device", "Unknown")
            intf = item.get("interface", "Unknown")
            ip_str = item.get("ip_address")
            mask_str = item.get("subnet_mask")
            gw_str = item.get("default_gateway")

            if not ip_str or not gw_str:
                continue

            try:
                if "/" in ip_str:
                    host_interface = ipaddress.IPv4Interface(ip_str)
                elif mask_str:
                    host_interface = ipaddress.IPv4Interface(f"{ip_str}/{mask_str}")
                else:
                    host_interface = ipaddress.IPv4Interface(f"{ip_str}/24")

                network = host_interface.network
                gw_ip = ipaddress.IPv4Address(gw_str.split("/")[0].strip())

                # Check 1: Is gateway in the same subnet?
                if gw_ip not in network:
                    violations.append(
                        f"{dev}:{intf} configured with gateway {gw_ip} outside local subnet {network}"
                    )
                    affected_devices.add(dev)
                    affected_interfaces.add(f"{dev}:{intf}")
                
                # Check 2: If router IPs exist in addressing, does gateway match any configured router?
                elif router_ips and str(gw_ip) not in router_ips:
                    # Gateway in subnet but no router has this IP
                    violations.append(
                        f"{dev}:{intf} default gateway {gw_ip} does not match any configured router interface IP ({', '.join(sorted(router_ips))})"
                    )
                    affected_devices.add(dev)
                    affected_interfaces.add(f"{dev}:{intf}")

            except ValueError as e:
                violations.append(f"{dev}:{intf} invalid gateway or IP specification ({gw_str}, {ip_str}): {str(e)}")
                affected_devices.add(dev)
                affected_interfaces.add(f"{dev}:{intf}")

        if violations:
            return RuleFinding(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=False,
                severity="high",
                details=f"Default gateway inconsistencies detected: {'; '.join(violations)}.",
                affected_devices=sorted(list(affected_devices)),
                affected_interfaces=sorted(list(affected_interfaces)),
                evidence={"violations": violations}
            )

        return RuleFinding(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=True,
            severity="info",
            details="All host default gateways are in valid subnets and match router interfaces.",
            affected_devices=[],
            affected_interfaces=[],
            evidence=None
        )
