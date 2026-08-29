from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.case import Case
from app.models.diagnosis import Diagnosis
from app.models.evaluation import Evaluation
from app.models.review import Review
from app.schemas.case import CaseCreate, CaseSummaryResponse, CaseDetailResponse
from app.schemas.ai_diagnosis import DiagnosisResponse
from app.schemas.rule_finding import RuleFinding
from app.schemas.correlation import EvidenceCorrelation
from app.schemas.evaluation import EvaluationResponse
from app.schemas.review import ReviewResponse
from app.rules.engine import rule_engine
from app.services.ai_service import ai_service
from app.services.correlation_service import correlation_service
from app.services.evaluation_service import evaluation_service

class CaseService:
    def create_case(self, db: Session, case_in: CaseCreate) -> CaseDetailResponse:
        """
        Creates a new Case and runs the full diagnostic pipeline:
        1. Deterministic Rule Engine (10 rules)
        2. AI Diagnostic Service
        3. Evidence Correlation Engine
        4. Automated AI Evaluation
        5. Atomic DB Persistence
        """
        # Step 1: Instantiate DB Case record
        case_db = Case(
            title=case_in.title,
            symptom=case_in.symptom,
            topology=case_in.topology or {},
            addressing=case_in.addressing or [],
            show_outputs=case_in.show_outputs or {},
            status="DIAGNOSED"
        )
        db.add(case_db)
        db.flush()  # Allocates case_db.id

        # Step 2: Run 10 Deterministic Networking Rules
        rule_findings = rule_engine.run_all(
            topology=case_in.topology or {},
            addressing=case_in.addressing or [],
            show_outputs=case_in.show_outputs or {}
        )

        # Step 3: Run AI Diagnostic Reasoning
        ai_diagnosis = ai_service.diagnose(
            symptom=case_in.symptom,
            topology=case_in.topology or {},
            addressing=case_in.addressing or [],
            show_outputs=case_in.show_outputs or {},
            rule_findings=rule_findings
        )

        # Step 4: Run Evidence Correlation Engine
        correlation = correlation_service.correlate(
            ai_diagnosis=ai_diagnosis,
            rule_findings=rule_findings,
            topology=case_in.topology or {},
            addressing=case_in.addressing or [],
            show_outputs=case_in.show_outputs or {}
        )

        # Step 5: Run Automated AI Evaluation
        evaluation_output = evaluation_service.evaluate(
            ai_diagnosis=ai_diagnosis,
            rule_findings=rule_findings,
            correlation=correlation
        )

        # Step 6: Persist Diagnosis
        diagnosis_db = Diagnosis(
            case_id=case_db.id,
            root_cause=ai_diagnosis.root_cause,
            osi_layer=ai_diagnosis.osi_layer,
            confidence=ai_diagnosis.confidence,
            reasoning=ai_diagnosis.reasoning,
            evidence_used=ai_diagnosis.evidence_used,
            rule_findings=[f.model_dump() for f in rule_findings],
            correlation=correlation.model_dump(),
            next_diagnostic_command=ai_diagnosis.next_diagnostic_command,
            proposed_fix=ai_diagnosis.proposed_fix,
            is_insufficient_evidence=ai_diagnosis.is_insufficient_evidence,
            raw_ai_response=ai_diagnosis.model_dump()
        )
        db.add(diagnosis_db)
        db.flush()  # Allocates diagnosis_db.id

        # Step 7: Persist Evaluation separately
        evaluation_db = Evaluation(
            case_id=case_db.id,
            diagnosis_id=diagnosis_db.id,
            root_cause_correctness=evaluation_output.root_cause_correctness,
            evidence_support_score=evaluation_output.evidence_support_score,
            osi_layer_match=evaluation_output.osi_layer_match,
            next_command_quality=evaluation_output.next_command_quality,
            proposed_fix_safety=evaluation_output.proposed_fix_safety,
            confidence_calibration=evaluation_output.confidence_calibration,
            notes=evaluation_output.notes
        )
        db.add(evaluation_db)

        db.commit()
        db.refresh(case_db)
        db.refresh(diagnosis_db)
        db.refresh(evaluation_db)

        # Step 8: Build and return structured response
        return self._build_case_detail_response(case_db, diagnosis_db, evaluation_db, None)

    def list_cases(
        self,
        db: Session,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[CaseSummaryResponse]:
        query = db.query(Case)
        if status:
            query = query.filter(Case.status == status.upper())
        cases = query.order_by(Case.created_at.desc()).offset(offset).limit(limit).all()

        results = []
        for c in cases:
            conf = c.diagnosis.confidence if c.diagnosis else None
            osi = c.diagnosis.osi_layer if c.diagnosis else None
            results.append(
                CaseSummaryResponse(
                    id=c.id,
                    title=c.title,
                    symptom=c.symptom,
                    status=c.status,
                    confidence=conf,
                    osi_layer=osi,
                    created_at=c.created_at.isoformat() if c.created_at else None
                )
            )
        return results

    def get_case_by_id(self, db: Session, case_id: int) -> Optional[CaseDetailResponse]:
        case_db = db.query(Case).filter(Case.id == case_id).first()
        if not case_db:
            return None

        diagnosis_db = case_db.diagnosis
        latest_eval = case_db.evaluations[-1] if case_db.evaluations else None
        latest_review = case_db.reviews[-1] if case_db.reviews else None

        return self._build_case_detail_response(case_db, diagnosis_db, latest_eval, latest_review)

    def get_diagnosis_by_id(self, db: Session, diagnosis_id: int) -> Optional[DiagnosisResponse]:
        """Retrieves a single stored diagnosis by its ID."""
        diagnosis_db = db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
        if not diagnosis_db:
            return None
        return DiagnosisResponse(
            id=diagnosis_db.id,
            root_cause=diagnosis_db.root_cause,
            osi_layer=diagnosis_db.osi_layer,
            confidence=diagnosis_db.confidence,
            reasoning=diagnosis_db.reasoning,
            evidence_used=diagnosis_db.evidence_used or [],
            next_diagnostic_command=diagnosis_db.next_diagnostic_command,
            proposed_fix=diagnosis_db.proposed_fix,
            is_insufficient_evidence=diagnosis_db.is_insufficient_evidence,
            created_at=diagnosis_db.created_at.isoformat() if diagnosis_db.created_at else None
        )

    def _build_case_detail_response(
        self,
        case_db: Case,
        diagnosis_db: Optional[Diagnosis],
        evaluation_db: Optional[Evaluation],
        review_db: Optional[Review]
    ) -> CaseDetailResponse:
        diag_resp = None
        rule_findings = None
        corr_resp = None

        if diagnosis_db:
            diag_resp = DiagnosisResponse(
                id=diagnosis_db.id,
                root_cause=diagnosis_db.root_cause,
                osi_layer=diagnosis_db.osi_layer,
                confidence=diagnosis_db.confidence,
                reasoning=diagnosis_db.reasoning,
                evidence_used=diagnosis_db.evidence_used or [],
                next_diagnostic_command=diagnosis_db.next_diagnostic_command,
                proposed_fix=diagnosis_db.proposed_fix,
                is_insufficient_evidence=diagnosis_db.is_insufficient_evidence,
                created_at=diagnosis_db.created_at.isoformat() if diagnosis_db.created_at else None
            )
            rule_findings = [RuleFinding(**rf) for rf in (diagnosis_db.rule_findings or [])]
            if diagnosis_db.correlation:
                corr_resp = EvidenceCorrelation(**diagnosis_db.correlation)

        eval_resp = None
        if evaluation_db:
            eval_resp = EvaluationResponse(
                id=evaluation_db.id,
                case_id=evaluation_db.case_id,
                diagnosis_id=evaluation_db.diagnosis_id,
                root_cause_correctness=evaluation_db.root_cause_correctness,
                evidence_support_score=evaluation_db.evidence_support_score,
                osi_layer_match=evaluation_db.osi_layer_match,
                next_command_quality=evaluation_db.next_command_quality,
                proposed_fix_safety=evaluation_db.proposed_fix_safety,
                confidence_calibration=evaluation_db.confidence_calibration,
                notes=evaluation_db.notes,
                created_at=evaluation_db.created_at.isoformat() if evaluation_db.created_at else None
            )

        review_resp = None
        if review_db:
            review_resp = ReviewResponse(
                id=review_db.id,
                case_id=review_db.case_id,
                status=review_db.status,
                reviewer_name=review_db.reviewer_name,
                reviewer_comment=review_db.reviewer_comment,
                corrected_diagnosis=review_db.corrected_diagnosis,
                created_at=review_db.created_at.isoformat() if review_db.created_at else None
            )

        return CaseDetailResponse(
            id=case_db.id,
            title=case_db.title,
            symptom=case_db.symptom,
            topology=case_db.topology or {},
            addressing=case_db.addressing or [],
            show_outputs=case_db.show_outputs or {},
            status=case_db.status,
            created_at=case_db.created_at.isoformat() if case_db.created_at else None,
            updated_at=case_db.updated_at.isoformat() if case_db.updated_at else None,
            diagnosis=diag_resp,
            rule_findings=rule_findings,
            correlation=corr_resp,
            evaluation=eval_resp,
            review=review_resp
        )

case_service = CaseService()
