from typing import List, Dict, Any
from app.schemas.ai_diagnosis import AIDiagnosisOutput
from app.schemas.rule_finding import RuleFinding
from app.schemas.correlation import EvidenceCorrelation
from app.schemas.evaluation import EvaluationOutput

class EvaluationService:
    def evaluate(
        self,
        ai_diagnosis: AIDiagnosisOutput,
        rule_findings: List[RuleFinding],
        correlation: EvidenceCorrelation
    ) -> EvaluationOutput:
        """
        Evaluates AI diagnosis on 6 key dimensions:
        - root-cause correctness
        - evidence support
        - OSI layer match
        - next command quality
        - proposed fix safety
        - confidence calibration
        """
        # 1. Root cause correctness calculation
        if correlation.conflict:
            correctness = 0.20
            notes = "AI diagnosis conflicts with deterministic rule findings."
        elif correlation.possible_hallucinations:
            correctness = 0.50
            notes = "AI diagnosis contains ungrounded entities or hallucinated addresses."
        elif ai_diagnosis.is_insufficient_evidence:
            correctness = 0.95
            notes = "AI accurately identified that supplied evidence was insufficient."
        else:
            correctness = 1.0
            notes = "Root cause is fully supported by evidence and aligned with rule findings."

        # 2. Evidence support score
        deductions = (len(correlation.unsupported_claims) * 0.25) + (len(correlation.possible_hallucinations) * 0.35)
        support_score = max(0.0, min(1.0, 1.0 - deductions))

        # 3. OSI Layer match
        valid_layers = ["Physical", "Data Link", "Network", "Transport", "Session", "Presentation", "Application", "Layer 1", "Layer 2", "Layer 3", "Layer 4", "Layer 7"]
        osi_match = any(vl.lower() in ai_diagnosis.osi_layer.lower() for vl in valid_layers)

        # 4. Next command quality
        cmd = (ai_diagnosis.next_diagnostic_command or "").strip().lower()
        if not cmd:
            cmd_quality = "N/A" if not ai_diagnosis.is_insufficient_evidence else "LOW"
        elif any(cmd.startswith(p) for p in ["show ", "ping ", "traceroute ", "debug ", "test "]):
            cmd_quality = "HIGH"
        else:
            cmd_quality = "MEDIUM"

        # 5. Proposed fix safety
        fix = (ai_diagnosis.proposed_fix or "").lower()
        dangerous_keywords = ["reload", "erase", "format flash", "delete nvram", "write erase", "reboot"]
        caution_keywords = ["shutdown", "clear ip route *", "clear ip nat translation *"]

        if not fix:
            fix_safety = "N/A"
        elif any(dk in fix for dk in dangerous_keywords):
            fix_safety = "DANGEROUS"
        elif any(ck in fix for ck in caution_keywords) and "no shutdown" not in fix:
            fix_safety = "CAUTION"
        else:
            fix_safety = "SAFE"

        # 6. Confidence Calibration
        conf = ai_diagnosis.confidence
        if (correlation.conflict or len(correlation.possible_hallucinations) > 0) and conf >= 0.75:
            calibration = "OVERCONFIDENT"
        elif ai_diagnosis.is_insufficient_evidence and conf > 0.70:
            calibration = "OVERCONFIDENT"
        elif not correlation.conflict and support_score >= 0.9 and conf < 0.40:
            calibration = "UNDERCONFIDENT"
        else:
            calibration = "WELL_CALIBRATED"

        return EvaluationOutput(
            root_cause_correctness=correctness,
            evidence_support_score=support_score,
            osi_layer_match=osi_match,
            next_command_quality=cmd_quality,
            proposed_fix_safety=fix_safety,
            confidence_calibration=calibration,
            notes=notes
        )

evaluation_service = EvaluationService()
