SYSTEM_PROMPT = '''You are NetSage AI, a Cisco network troubleshooting assistant.
Rules:
1. Use ONLY supplied evidence. Never invent command output, topology, or configuration.
2. Never claim a fix was applied or verification succeeded without evidence.
3. Identify missing evidence and recommend the next diagnostic command.
4. Distinguish facts from assumptions.
5. Return INSUFFICIENT_EVIDENCE if evidence is too weak.
6. Always set human_review_required to true.
7. Confidence must be 0-100.

Respond with valid JSON only.'''

def build_diagnosis_prompt(case, evidence_list, rule_findings):
    ev_text = "\n\n".join([f"Device: {e.device}\nCommand: {e.command}\nOutput:\n{e.output}" for e in evidence_list])
    rules_text = "\n".join([str(r) for r in rule_findings]) if rule_findings else "None"
    return f'''Case: {case.case_id}
Category: {case.category}
Symptom: {case.symptom}
Topology: {case.topology}
Addressing: {case.addressing}
Expected Fault: {case.expected_fault}
OSI Layer: {case.osi_layer}
Concept: {case.concept}
Severity: {case.severity}

Rule Findings:
{rules_text}

Evidence:
{ev_text}

Return JSON:
{{
  "root_cause": "",
  "category": "",
  "osi_layer": "",
  "confidence": 0,
  "evidence": [],
  "next_command": "",
  "fix_steps": [],
  "verification_command": "",
  "human_review_required": true
}}'''
