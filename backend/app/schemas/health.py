from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class BloodworkCreate(BaseModel):
    test_date: date
    vitamin_d: Optional[float] = None
    ldl: Optional[float] = None
    hdl: Optional[float] = None
    triglycerides: Optional[float] = None
    a1c: Optional[float] = None
    fasting_glucose: Optional[float] = None
    crp: Optional[float] = None
    testosterone_total: Optional[float] = None

    @field_validator("vitamin_d", "ldl", "hdl", "triglycerides", "a1c",
                     "fasting_glucose", "crp", "testosterone_total", mode="before")
    @classmethod
    def must_be_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError("Biomarker values must be positive")
        return v


class BloodworkResponse(BloodworkCreate):
    id: str
    user_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LifestyleCreate(BaseModel):
    entry_date: date
    sleep_hours: Optional[float] = None
    steps: Optional[int] = None
    resting_hr: Optional[int] = None
    hrv: Optional[float] = None
    workout_minutes: Optional[int] = None
    stress_1_10: Optional[int] = None
    diet_notes: Optional[str] = None

    @field_validator("stress_1_10")
    @classmethod
    def stress_range(cls, v):
        if v is not None and not (1 <= v <= 10):
            raise ValueError("stress_1_10 must be between 1 and 10")
        return v

    @field_validator("sleep_hours")
    @classmethod
    def sleep_range(cls, v):
        if v is not None and not (0 < v <= 24):
            raise ValueError("sleep_hours must be between 0 and 24")
        return v


class LifestyleResponse(LifestyleCreate):
    id: str
    user_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class HealthSummary(BaseModel):
    latest_bloodwork: Optional[BloodworkResponse] = None
    latest_lifestyle: Optional[LifestyleResponse] = None
    bloodwork_count: int = 0
    lifestyle_count: int = 0
