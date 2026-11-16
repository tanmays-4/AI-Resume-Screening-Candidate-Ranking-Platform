"""Candidate profile model."""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.connection import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(255), default="")
    phone = Column(String(50), default="")
    skills = Column(Text, default="")
    education = Column(Text, default="")
    experience = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="candidate")
    resumes = relationship(
        "Resume",
        back_populates="candidate",
        cascade="all, delete-orphan",
        order_by="Resume.id",
    )
    scores = relationship("Score", back_populates="candidate", cascade="all, delete-orphan")
