"""Screening score model for job-candidate matching."""

from sqlalchemy import Column, Integer, Float, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.connection import Base


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    match_score = Column(Float, default=0.0)
    ats_score = Column(Float, default=0.0)
    missing_skills = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("job_id", "candidate_id", name="uq_job_candidate"),)

    job = relationship("Job", back_populates="scores")
    candidate = relationship("Candidate", back_populates="scores")
