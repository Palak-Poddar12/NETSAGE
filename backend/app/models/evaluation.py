import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    diagnosis_id = Column(Integer, ForeignKey("diagnoses.id", ondelete="CASCADE"), nullable=False, index=True)
    root_cause_correctness = Column(Float, nullable=False, default=1.0)
    evidence_support_score = Column(Float, nullable=False, default=1.0)
    osi_layer_match = Column(Boolean, nullable=False, default=True)
    next_command_quality = Column(String(50), nullable=False, default="HIGH")
    proposed_fix_safety = Column(String(50), nullable=False, default="SAFE")
    confidence_calibration = Column(String(50), nullable=False, default="WELL_CALIBRATED")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="evaluations")
    diagnosis = relationship("Diagnosis", back_populates="evaluations")
