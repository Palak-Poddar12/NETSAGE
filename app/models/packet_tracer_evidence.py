import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class PacketTracerEvidence(Base):
    __tablename__ = "packet_tracer_evidence"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=True, index=True)
    pt_case_id = Column(String(100), nullable=False, index=True)
    device = Column(String(100), nullable=False)
    command = Column(String(255), nullable=False)
    output = Column(Text, nullable=False)
    is_verification = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="packet_tracer_evidence")
