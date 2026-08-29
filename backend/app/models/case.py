import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pt_case_id = Column(String(100), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    symptom = Column(Text, nullable=False)
    topology = Column(JSON, nullable=False, default=dict)
    addressing = Column(JSON, nullable=False, default=list)
    show_outputs = Column(JSON, nullable=False, default=dict)
    status = Column(String(50), default="DIAGNOSED", nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    diagnosis = relationship("Diagnosis", back_populates="case", uselist=False, cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="case", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="case", cascade="all, delete-orphan")
    packet_tracer_evidence = relationship("PacketTracerEvidence", back_populates="case", cascade="all, delete-orphan")
