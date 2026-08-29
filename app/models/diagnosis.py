import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    root_cause = Column(Text, nullable=False)
    osi_layer = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=False)
    evidence_used = Column(JSON, nullable=False, default=list)
    rule_findings = Column(JSON, nullable=False, default=list)
    correlation = Column(JSON, nullable=False, default=dict)
    next_diagnostic_command = Column(Text, nullable=True)
    proposed_fix = Column(Text, nullable=True)
    is_insufficient_evidence = Column(Boolean, default=False, nullable=False)
    raw_ai_response = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="diagnosis")
    evaluations = relationship("Evaluation", back_populates="diagnosis", cascade="all, delete-orphan")
