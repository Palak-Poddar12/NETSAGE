import re
from typing import Dict, Any, List
from app.rules.base import BaseRule
from app.schemas.rule_finding import RuleFinding

class InterfaceDownRule(BaseRule):
    rule_id = "interface_down"
    rule_name = "Interface Operational State Check"
    description = "Detects network interfaces that are administratively down, line protocol down, err-disabled, or disconnected."

    def evaluate(
        self,
        topology: Dict[str, Any],
        addressing: List[Dict[str, Any]],
        show_outputs: Dict[str, Any]
    ) -> RuleFinding:
        down_interfaces = []
        affected_devices = set()
        affected_interfaces = set()

        for dev, outputs in show_outputs.items():
            if not isinstance(outputs, dict):
                continue
            for cmd, text in outputs.items():
                cmd_lower = cmd.lower()
                lines = str(text).splitlines()

                # show ip interface brief
                if "ip_interface" in cmd_lower or "ip int br" in cmd_lower:
                    for line in lines:
                        # e.g.: GigabitEthernet0/1 192.168.1.1 YES manual administratively down down
                        # or: GigabitEthernet0/1 192.168.1.1 YES manual up down
                        # or: GigabitEthernet0/1 192.168.1.1 YES manual down down
                        parts = line.strip().split()
                        if len(parts) >= 5 and not parts[0].lower().startswith("interface"):
                            intf = parts[0]
                            status_line = " ".join(parts[3:]).lower()
                            if "administratively down" in status_line:
                                down_interfaces.append(f"{dev}:{intf} (administratively down)")
                                affected_devices.add(dev)
                                affected_interfaces.add(f"{dev}:{intf}")
                            elif "down" in status_line:
                                down_interfaces.append(f"{dev}:{intf} (line protocol down / down)")
                                affected_devices.add(dev)
                                affected_interfaces.add(f"{dev}:{intf}")

                # show interfaces status
                elif "interface" in cmd_lower and "status" in cmd_lower:
                    for line in lines:
                        # e.g.: Gi0/1   disabled   10   auto  auto
                        # or: Gi0/2   err-disabled 10   auto  auto
                        # or: Gi0/3   notconnect   1    auto  auto
                        parts = line.strip().split()
                        if len(parts) >= 2 and not parts[0].lower().startswith("port"):
                            intf = parts[0]
                            status = parts[1].lower()
                            if status in ("disabled", "err-disabled", "notconnect", "down"):
                                down_interfaces.append(f"{dev}:{intf} ({status})")
                                affected_devices.add(dev)
                                affected_interfaces.add(f"{dev}:{intf}")

                # generic show interfaces
                elif "show_interfaces" in cmd_lower or "show int" in cmd_lower:
                    current_intf = None
                    for line in lines:
                        match = re.match(r"^(\S+)\s+is\s+(administratively\s+down|down|up),\s+line\s+protocol\s+is\s+(down|up)", line, re.IGNORECASE)
                        if match:
                            intf_name = match.group(1)
                            admin_st = match.group(2).lower()
                            proto_st = match.group(3).lower()
                            if "down" in admin_st or "down" in proto_st:
                                down_interfaces.append(f"{dev}:{intf_name} (status: {admin_st}, line protocol: {proto_st})")
                                affected_devices.add(dev)
                                affected_interfaces.add(f"{dev}:{intf_name}")

        if down_interfaces:
            # Deduplicate
            unique_down = sorted(list(set(down_interfaces)))
            return RuleFinding(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=False,
                severity="critical" if any("administratively down" in d or "down" in d for d in unique_down) else "high",
                details=f"Inactive/down interfaces detected: {'; '.join(unique_down)}.",
                affected_devices=sorted(list(affected_devices)),
                affected_interfaces=sorted(list(affected_interfaces)),
                evidence={"down_interfaces": unique_down}
            )

        return RuleFinding(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=True,
            severity="info",
            details="All monitored network interfaces are in up/up operational status.",
            affected_devices=[],
            affected_interfaces=[],
            evidence=None
        )
