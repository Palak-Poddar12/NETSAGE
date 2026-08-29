import json
import os
from typing import Any

from openai import OpenAI

from app.prompts import SYSTEM_PROMPT, USER_TEMPLATE
from app.schemas import AIOutput


class AIServiceError(Exception):
    pass


def _format_evidence(evidence: list[Any]) -> str:
    if not evidence:
        return "NO EVIDENCE SUPPLIED"
    chunks = []
    for item in evidence:
        chunks.append(
            f"[device={item.device} command={item.command} source={item.source}]\n"
            f"{item.output}"
        )
    return "\n\n".join(chunks)


def _format_rules(rule_findings: list[dict[str, Any]]) -> str:
    if not rule_findings:
        return "NO DETERMINISTIC FINDINGS"
    return json.dumps(rule_findings, ensure_ascii=False, indent=2)


def diagnose(case: Any, evidence: list[Any], rule_findings: list[dict[str, Any]]) -> AIOutput:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "").strip()

    if not api_key:
        raise AIServiceError("OPENAI_API_KEY is not configured.")
    if not model:
        raise AIServiceError("OPENAI_MODEL is not configured.")

    client = OpenAI(api_key=api_key, timeout=45.0)

    user_prompt = USER_TEMPLATE.format(
        case_id=case.case_id,
        category=case.category,
        symptom=case.symptom,
        topology=case.topology,
        addressing=case.addressing,
        expected_fault=case.expected_fault,
        osi_layer=case.osi_layer,
        concept=case.concept,
        severity=case.severity,
        evidence=_format_evidence(evidence),
        rule_findings=_format_rules(rule_findings),
    )

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
    except Exception as exc:
        raise AIServiceError(f"OpenAI request failed: {exc}") from exc

    content = response.choices[0].message.content if response.choices else None
    if not content or not content.strip():
        raise AIServiceError("OpenAI returned an empty response.")

    try:
        payload = json.loads(content)
        result = AIOutput.model_validate(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        raise AIServiceError(f"OpenAI returned invalid diagnosis JSON: {exc}") from exc

    return result
