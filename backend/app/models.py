from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from app.database import Base
from datetime import datetime

class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True)
    case_id = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    symptom = Column(Text, nullable=False)
    topology = Column(Text, nullable=False)
    addressing = Column(Text, nullable=False)
    expected_fault = Column(Text, nullable=False)
    osi_layer = Column(String, nullable=False)
    concept = Column(Text, nullable=False)
    severity = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True)
    case_id = Column(String, nullable=False)
    source = Column(String, nullable=False)
    device = Column(String, nullable=False)
    command = Column(String, nullable=False)
    output = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Diagnosis(Base):
    __tablename__ = "diagnoses"
    id = Column(Integer, primary_key=True)
    case_id = Column(String, nullable=False)
    root_cause = Column(Text)
    category = Column(String)
    osi_layer = Column(String)
    confidence = Column(Float)
    evidence = Column(Text)
    rule_findings = Column(Text)
    next_command = Column(String)
    fix_steps = Column(Text)
    verification_command = Column(String)
    status = Column(String, default="PENDING")
    human_review_required = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    diagnosis_id = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    corrected_diagnosis = Column(Text)
    reviewer_comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
