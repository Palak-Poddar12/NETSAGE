import json
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
from app.config import settings
from app.schemas.ai_diagnosis import AIDiagnosisOutput
from app.schemas.rule_finding import RuleFinding

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are NetSage AI, an expert autonomous network diagnostic reasoning engine.
Your mission is to perform root-cause analysis on reported network symptoms using ONLY the supplied evidence.

STRICT OPERATING CONSTRAINTS:
1. Grounding: Use ONLY the provided topology, addressing tables, show outputs, and rule engine findings.
2. Anti-Hallucination: Never invent device names, interfaces, IP addresses, VLANs, or packet captures not present in the input.
3. Insufficient Evidence: If the provided data is insufficient to conclusively determine the root cause, set `is_insufficient_evidence: true`, state what is missing in `reasoning`, and propose an exact `next_diagnostic_command` to collect the missing data.
4. Remediation: Propose a remediation fix in `proposed_fix` ONLY if the root cause is conclusively justified by evidence.
5. Safety: Never suggest dangerous or destructive commands without caution. Never claim verification without factual evidence.
6. Structured Output: You MUST reply with valid JSON matching the schema below and nothing else.

JSON Schema:
{
  "root_cause": "string",
  "osi_layer": "Physical (Layer 1) | Data Link (Layer 2) | Network (Layer 3) | Transport (Layer 4) | Application (Layer 7)",
  "confidence": float (0.0 to 1.0),
  "reasoning": "string (step-by-step logical deduction grounded in provided evidence)",
  "evidence_used": ["string", "string"],
  "next_diagnostic_command": "string or null",
  "proposed_fix": "string or null",
  "is_insufficient_evidence": boolean
}
"""

class AIService:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def diagnose(
        self,
        symptom: str,
        topology: Dict[str, Any],
        addressing: List[Dict[str, Any]],
        show_outputs: Dict[str, Any],
        rule_findings: List[RuleFinding]
    ) -> AIDiagnosisOutput:
        """
        Executes AI diagnostic reasoning.
        Falls back seamlessly to deterministic synthesis if API key is absent or API call fails.
        """
        if not self.client or not self.api_key:
            return self._fallback_deterministic_synthesis(
                symptom, topology, addressing, show_outputs, rule_findings
            )

        user_content = {
            "symptom": symptom,
            "topology": topology,
            "addressing": addressing,
            "show_outputs": show_outputs,
            "rule_findings": [f.model_dump() for f in rule_findings]
        }

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": json.dumps(user_content, indent=2)}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=15.0
            )
            raw_text = response.choices[0].message.content
            parsed_json = json.loads(raw_text)
            return AIDiagnosisOutput.model_validate(parsed_json)

        except Exception as e:
            logger.warning(f"OpenAI API call failed ({str(e)}), triggering fallback diagnostic synthesis.")
            return self._fallback_deterministic_synthesis(
                symptom, topology, addressing, show_outputs, rule_findings
            )

    def _fallback_deterministic_synthesis(
        self,
        symptom: str,
        topology: Dict[str, Any],
        addressing: List[Dict[str, Any]],
        show_outputs: Dict[str, Any],
        rule_findings: List[RuleFinding]
    ) -> AIDiagnosisOutput:
        """
        Deterministic, grounded synthesis when running without external LLM API key.
        Synthesizes rule-engine findings and input data into compliant AIDiagnosisOutput.
        """
        failed_rules = [f for f in rule_findings if not f.passed]

        # Case 1: Empty or extremely sparse evidence
        if not topology and not addressing and not show_outputs:
            return AIDiagnosisOutput(
                root_cause="Insufficient evidence provided to perform network diagnosis.",
                osi_layer="Unknown",
                confidence=0.1,
                reasoning="The submitted case contained no topology, addressing records, or show command outputs.",
                evidence_used=[],
                next_diagnostic_command="show ip interface brief",
                proposed_fix=None,
                is_insufficient_evidence=True
            )

        # Case 2: Concrete rule failures detected
        if failed_rules:
            primary_failure = failed_rules[0]
            rule_id = primary_failure.rule_id

            layer_map = {
                "interface_down": "Physical (Layer 1)",
                "missing_vlan": "Data Link (Layer 2)",
                "trunk_vlan_mismatch": "Data Link (Layer 2)",
                "duplicate_ip": "Network (Layer 3)",
                "invalid_subnet": "Network (Layer 3)",
                "gateway_mismatch": "Network (Layer 3)",
                "missing_route": "Network (Layer 3)",
                "dhcp_inconsistency": "Application (Layer 7)",
                "nat_inconsistency": "Network (Layer 3)",
                "acl_deny": "Network (Layer 3)"
            }

            osi = layer_map.get(rule_id, "Network (Layer 3)")
            evidence_citations = [f"Rule Engine {primary_failure.rule_name}: {primary_failure.details}"]

            if primary_failure.affected_devices:
                evidence_citations.append(f"Affected devices: {', '.join(primary_failure.affected_devices)}")

            # Generate sensible diagnostic command and fix
            fix_map = {
                "interface_down": "Execute 'no shutdown' on affected interface.",
                "missing_vlan": "Create and activate VLAN on switch database: 'vlan <vlan_id>'.",
                "trunk_vlan_mismatch": "Align trunk allowed VLANs and native VLAN on both sides of the link.",
                "duplicate_ip": "Reassign duplicate IP to an unused host address.",
                "invalid_subnet": "Correct host IP to a valid host address within subnet boundaries.",
                "gateway_mismatch": "Configure default gateway to match active router interface IP.",
                "missing_route": "Add missing static route or verify routing protocol neighbor adjacency.",
                "dhcp_inconsistency": "Correct DHCP pool network or excluded-address range.",
                "nat_inconsistency": "Configure 'ip nat inside' / 'ip nat outside' on designated interfaces.",
                "acl_deny": "Modify ACL entry to permit required traffic flow."
            }

            cmd_map = {
                "interface_down": "show interfaces status",
                "missing_vlan": "show vlan brief",
                "trunk_vlan_mismatch": "show interfaces trunk",
                "duplicate_ip": "show arp",
                "invalid_subnet": "show ip interface brief",
                "gateway_mismatch": "show ip route",
                "missing_route": "show ip route",
                "dhcp_inconsistency": "show ip dhcp binding",
                "nat_inconsistency": "show ip nat translations",
                "acl_deny": "show access-lists"
            }

            return AIDiagnosisOutput(
                root_cause=primary_failure.details,
                osi_layer=osi,
                confidence=0.92,
                reasoning=f"Deterministic rule analysis identified fault in {primary_failure.rule_name}. Evidence directly confirms {primary_failure.details}",
                evidence_used=evidence_citations,
                next_diagnostic_command=cmd_map.get(rule_id, "show running-config"),
                proposed_fix=fix_map.get(rule_id, "Correct configuration as identified."),
                is_insufficient_evidence=False
            )

        # Case 3: All 10 deterministic rules passed, but symptom exists
        return AIDiagnosisOutput(
            root_cause="All standard Layer 1-4 checks passed. Issue may stem from higher layer policies or unprovided telemetry.",
            osi_layer="Transport / Application (Layer 4-7)",
            confidence=0.60,
            reasoning=f"All 10 deterministic network rules passed successfully. Reported symptom: '{symptom}'. Additional packet trace or application telemetry is recommended.",
            evidence_used=["10 Deterministic Network Rules passed"],
            next_diagnostic_command="debug ip packet detail",
            proposed_fix=None,
            is_insufficient_evidence=True
        )

ai_service = AIService()
