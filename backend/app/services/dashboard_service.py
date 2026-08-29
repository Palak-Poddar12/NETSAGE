from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.case import Case
from app.models.diagnosis import Diagnosis
from app.models.review import Review
from app.schemas.dashboard import DashboardMetricsResponse, ReviewStats

class DashboardService:
    def get_metrics(self, db: Session) -> DashboardMetricsResponse:
        """
        Dynamically calculates dashboard metrics from actual database records.
        Never hardcodes any statistics.
        """
        # 1. Total cases and diagnoses
        total_cases = db.query(func.count(Case.id)).scalar() or 0
        total_diagnoses = db.query(func.count(Diagnosis.id)).scalar() or 0

        # 2. Review counts
        accepted_count = db.query(func.count(Review.id)).filter(Review.status == "ACCEPTED").scalar() or 0
        edited_count = db.query(func.count(Review.id)).filter(Review.status == "EDITED").scalar() or 0
        rejected_count = db.query(func.count(Review.id)).filter(Review.status == "REJECTED").scalar() or 0
        pending_count = db.query(func.count(Case.id)).filter(Case.status == "DIAGNOSED").scalar() or 0

        # 3. Agreement rate, conflicts, insufficient evidence, issue distribution, severity distribution
        diagnoses = db.query(Diagnosis).all()
        agreed_count = 0
        conflicts_count = 0
        insufficient_evidence_count = 0
        issue_distribution: Dict[str, int] = {}
        severity_distribution: Dict[str, int] = {
            "info": 0,
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0
        }

        for d in diagnoses:
            # Issue distribution by OSI layer
            layer = d.osi_layer or "Unknown"
            issue_distribution[layer] = issue_distribution.get(layer, 0) + 1

            # Insufficient evidence count
            if d.is_insufficient_evidence:
                insufficient_evidence_count += 1

            # Correlation analysis
            corr = d.correlation or {}
            if corr.get("conflict", False):
                conflicts_count += 1
            if corr.get("agreement", True):
                agreed_count += 1

            # Severity distribution from rule findings
            findings = d.rule_findings or []
            for f in findings:
                if isinstance(f, dict):
                    sev = str(f.get("severity", "info")).lower()
                    severity_distribution[sev] = severity_distribution.get(sev, 0) + 1

        agreement_rate = (agreed_count / total_diagnoses) if total_diagnoses > 0 else 1.0

        return DashboardMetricsResponse(
            total_cases=total_cases,
            total_diagnoses=total_diagnoses,
            reviews=ReviewStats(
                accepted=accepted_count,
                edited=edited_count,
                rejected=rejected_count,
                pending=pending_count
            ),
            agreement_rate=round(agreement_rate, 4),
            issue_distribution=issue_distribution,
            severity_distribution=severity_distribution,
            conflicts_count=conflicts_count,
            insufficient_evidence_count=insufficient_evidence_count
        )

dashboard_service = DashboardService()
