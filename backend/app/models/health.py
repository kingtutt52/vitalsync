import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Date, DateTime, Float, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BloodworkEntry(Base):
    __tablename__ = "bloodwork_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    test_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Biomarkers — all optional since a panel may not test everything
    vitamin_d: Mapped[Optional[float]] = mapped_column(Float, nullable=True)       # ng/mL
    ldl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)             # mg/dL
    hdl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)             # mg/dL
    triglycerides: Mapped[Optional[float]] = mapped_column(Float, nullable=True)   # mg/dL
    a1c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)             # %
    fasting_glucose: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # mg/dL
    crp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)             # mg/L
    testosterone_total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # ng/dL

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bloodwork_entries")


class LifestyleEntry(Base):
    __tablename__ = "lifestyle_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)

    sleep_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    steps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resting_hr: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # bpm
    hrv: Mapped[Optional[float]] = mapped_column(Float, nullable=True)          # ms
    workout_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    stress_1_10: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    diet_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="lifestyle_entries")
