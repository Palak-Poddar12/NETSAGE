from typing import Dict, Any, List
from app.schemas.rule_finding import RuleFinding
from app.rules.duplicate_ip import DuplicateIPRule
from app.rules.invalid_subnet import InvalidSubnetRule
from app.rules.gateway_mismatch import GatewayMismatchRule
from app.rules.interface_down import InterfaceDownRule
from app.rules.missing_vlan import MissingVLANRule
from app.rules.trunk_vlan_mismatch import TrunkVLANMismatchRule
from app.rules.missing_route import MissingRouteRule
from app.rules.acl_deny import ACLDenyRule
from app.rules.dhcp_inconsistency import DHCPInconsistencyRule
from app.rules.nat_inconsistency import NATInconsistencyRule

class NetworkingRuleEngine:
    def __init__(self):
        self.rules = [
            DuplicateIPRule(),
            InvalidSubnetRule(),
            GatewayMismatchRule(),
            InterfaceDownRule(),
            MissingVLANRule(),
            TrunkVLANMismatchRule(),
            MissingRouteRule(),
            ACLDenyRule(),
            DHCPInconsistencyRule(),
            NATInconsistencyRule(),
        ]

    def run_all(
        self,
        topology: Dict[str, Any],
        addressing: List[Dict[str, Any]],
        show_outputs: Dict[str, Any]
    ) -> List[RuleFinding]:
        """
        Executes all 10 deterministic network rules and returns structured findings.
        Never invokes LLMs for deterministic calculations.
        """
        findings: List[RuleFinding] = []
        for rule in self.rules:
            try:
                finding = rule.evaluate(topology, addressing, show_outputs)
                findings.append(finding)
            except Exception as e:
                # Fallback safeguard in case of unexpected malformed data
                findings.append(
                    RuleFinding(
                        rule_id=rule.rule_id,
                        rule_name=rule.rule_name,
                        passed=False,
                        severity="medium",
                        details=f"Rule evaluation encountered error: {str(e)}",
                        affected_devices=[],
                        affected_interfaces=[]
                    )
                )
        return findings

rule_engine = NetworkingRuleEngine()
