import re
from typing import Dict, Any, List, Set, Tuple
from app.rules.base import BaseRule
from app.schemas.rule_finding import RuleFinding

def parse_vlan_ranges(vlan_str: str) -> Set[int]:
    """Expands VLAN strings like '1-5,10,20-22' into a set of integers."""
    result = set()
    if not vlan_str or vlan_str.strip().lower() in ("none", "none.", "-"):
        return result
    for part in vlan_str.split(","):
        part = part.strip()
        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
                result.update(range(start, end + 1))
            except ValueError:
                pass
        elif part.isdigit():
            result.add(int(part))
    return result

class TrunkVLANMismatchRule(BaseRule):
    rule_id = "trunk_vlan_mismatch"
    rule_name = "Trunk Link Native & Allowed VLAN Mismatch Check"
    description = "Detects native VLAN discrepancies or asymmetric allowed VLAN lists across interconnected trunk interfaces."

    def evaluate(
        self,
        topology: Dict[str, Any],
        addressing: List[Dict[str, Any]],
        show_outputs: Dict[str, Any]
    ) -> RuleFinding:
        violations = []
        affected_devices = set()
        affected_interfaces = set()

        # Parse trunk info per switch: {dev: {intf: {"native": int, "allowed": Set[int]}}}
        trunks: Dict[str, Dict[str, Dict[str, Any]]] = {}

        for dev, outputs in show_outputs.items():
            if not isinstance(outputs, dict):
                continue
            dev_trunks = {}
            for cmd, text in outputs.items():
                if "trunk" in cmd.lower():
                    lines = str(text).splitlines()
                    for line in lines:
                        # Parsing standard show interfaces trunk outputs
                        # Format example 1: Port Mode Encapsulation Status Native_vlan
                        # Format example 2: Gi0/24 10,20,30
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            intf = parts[0]
                            # Check if line specifies native vlan
                            if any(w in line.lower() for w in ["802.1q", "isl", "trunking"]):
                                try:
                                    native_v = int(parts[-1])
                                    dev_trunks.setdefault(intf, {})["native"] = native_v
                                except (ValueError, IndexError):
                                    pass
                            # Check if line specifies allowed vlans (e.g. 1-1005 or 10,20,30)
                            elif re.search(r"\d+([-,]\d+)*", parts[1]):
                                allowed = parse_vlan_ranges(parts[1])
                                if allowed:
                                    dev_trunks.setdefault(intf, {})["allowed"] = allowed

            if dev_trunks:
                trunks[dev] = dev_trunks

        # Compare trunk links across topology links
        links = topology.get("links", [])
        for link in links:
            s_dev = link.get("source")
            s_intf = link.get("source_interface")
            t_dev = link.get("target")
            t_intf = link.get("target_interface")

            s_trunk = trunks.get(s_dev, {}).get(s_intf)
            t_trunk = trunks.get(t_dev, {}).get(t_intf)

            if s_trunk and t_trunk:
                # Check Native VLAN
                s_nat = s_trunk.get("native")
                t_nat = t_trunk.get("native")
                if s_nat and t_nat and s_nat != t_nat:
                    violations.append(
                        f"Native VLAN mismatch between {s_dev}:{s_intf} (VLAN {s_nat}) and {t_dev}:{t_intf} (VLAN {t_nat})"
                    )
                    affected_devices.update([s_dev, t_dev])
                    affected_interfaces.update([f"{s_dev}:{s_intf}", f"{t_dev}:{t_intf}"])

                # Check Allowed VLANs
                s_allow = s_trunk.get("allowed")
                t_allow = t_trunk.get("allowed")
                if s_allow is not None and t_allow is not None:
                    diff = s_allow.symmetric_difference(t_allow)
                    if diff:
                        violations.append(
                            f"Trunk allowed VLAN mismatch on link {s_dev}:{s_intf} <-> {t_dev}:{t_intf} (discrepancy on VLANs: {sorted(list(diff))})"
                        )
                        affected_devices.update([s_dev, t_dev])
                        affected_interfaces.update([f"{s_dev}:{s_intf}", f"{t_dev}:{t_intf}"])

        # Also check if host VLAN in addressing is pruned from trunk ports
        for item in addressing:
            vlan_id = item.get("vlan")
            if vlan_id is None:
                continue
            try:
                vlan_int = int(vlan_id)
            except ValueError:
                continue

            for dev, dev_trunks in trunks.items():
                for intf, tinfo in dev_trunks.items():
                    allowed = tinfo.get("allowed")
                    if allowed is not None and len(allowed) > 0 and vlan_int not in allowed:
                        # Check if this switch connects towards the core router
                        violations.append(
                            f"Switch {dev}:{intf} trunk does not allow required VLAN {vlan_int} used by {item.get('device')}"
                        )
                        affected_devices.add(dev)
                        affected_interfaces.add(f"{dev}:{intf}")

        if violations:
            unique_v = sorted(list(set(violations)))
            return RuleFinding(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=False,
                severity="high",
                details=f"Trunk VLAN inconsistencies found: {'; '.join(unique_v)}.",
                affected_devices=sorted(list(affected_devices)),
                affected_interfaces=sorted(list(affected_interfaces)),
                evidence={"violations": unique_v}
            )

        return RuleFinding(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=True,
            severity="info",
            details="Trunk native VLANs and allowed VLAN configurations are consistent.",
            affected_devices=[],
            affected_interfaces=[],
            evidence=None
        )
