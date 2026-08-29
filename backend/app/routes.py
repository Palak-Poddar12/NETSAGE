from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app import models, schemas, rules, ai
import json

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "service": "netsage-backend"}

@router.post("/api/cases", response_model=schemas.CaseOut)
def create_case(case: schemas.CaseCreate, db: Session = Depends(get_db)):
    if db.query(models.Case).filter(models.Case.case_id == case.case_id).first():
        raise HTTPException(status_code=409, detail="case_id already exists")
    c = models.Case(**case.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@router.get("/api/cases", response_model=List[schemas.CaseOut])
def list_cases(db: Session = Depends(get_db)):
    return db.query(models.Case).all()

@router.get("/api/cases/{case_id}", response_model=schemas.CaseOut)
def get_case(case_id: str, db: Session = Depends(get_db)):
    c = db.query(models.Case).filter(models.Case.case_id == case_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    return c

@router.post("/api/evidence", response_model=schemas.EvidenceOut)
def create_evidence(ev: schemas.EvidenceCreate, db: Session = Depends(get_db)):
    e = models.Evidence(**ev.model_dump())
    db.add(e)
    db.commit()
    db.refresh(e)
    return e

@router.get("/api/evidence/{case_id}", response_model=List[schemas.EvidenceOut])
def get_evidence(case_id: str, db: Session = Depends(get_db)):
    return db.query(models.Evidence).filter(models.Evidence.case_id == case_id).all()

@router.post("/api/diagnose", response_model=schemas.DiagnosisOut)
def diagnose(req: schemas.DiagnosisCreate, db: Session = Depends(get_db)):
    case = db.query(models.Case).filter(models.Case.case_id == req.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    evidence = db.query(models.Evidence).filter(models.Evidence.case_id == req.case_id).all()
    rule_findings = rules.run_rules(evidence)
    ai_result = ai.diagnose(case, evidence, rule_findings)
    d = models.Diagnosis(
        case_id=req.case_id,
        root_cause=ai_result.get("root_cause"),
        category=ai_result.get("category"),
        osi_layer=ai_result.get("osi_layer"),
        confidence=ai_result.get("confidence"),
        evidence=json.dumps(ai_result.get("evidence", [])),
        rule_findings=json.dumps(rule_findings),
        next_command=ai_result.get("next_command"),
        fix_steps=json.dumps(ai_result.get("fix_steps", [])),
        verification_command=ai_result.get("verification_command"),
        status="PENDING",
        human_review_required=True,
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d

@router.post("/api/reviews", response_model=schemas.ReviewOut)
def create_review(r: schemas.ReviewCreate, db: Session = Depends(get_db)):
    diag = db.query(models.Diagnosis).filter(models.Diagnosis.id == r.diagnosis_id).first()
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    review = models.Review(**r.model_dump())
    db.add(review)
    diag.status = r.status
    db.commit()
    db.refresh(review)
    return review

@router.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db)):
    total_cases = db.query(models.Case).count()
    total_diag = db.query(models.Diagnosis).count()
    accepted = db.query(models.Review).filter(models.Review.status == "ACCEPTED").count()
    edited = db.query(models.Review).filter(models.Review.status == "EDITED").count()
    rejected = db.query(models.Review).filter(models.Review.status == "REJECTED").count()
    pending = total_diag - accepted - edited - rejected
    total_reviews = accepted + edited + rejected
    agreement = (accepted / total_reviews * 100) if total_reviews else 0.0
    cats = db.query(models.Case.category, func.count()).group_by(models.Case.category).all()
    sevs = db.query(models.Case.severity, func.count()).group_by(models.Case.severity).all()
    return {
        "total_cases": total_cases,
        "total_diagnoses": total_diag,
        "accepted": accepted,
        "edited": edited,
        "rejected": rejected,
        "pending": pending,
        "agreement_rate": round(agreement, 2),
        "issue_distribution": {c: n for c, n in cats},
        "severity_distribution": {s: n for s, n in sevs},
    }
