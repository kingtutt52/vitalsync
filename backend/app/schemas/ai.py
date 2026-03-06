from typing import List, Optional
from pydantic import BaseModel


class Subscores(BaseModel):
    metabolic: float
    lipids: float
    sleep_recovery: float
    hormones: float
    inflammation: float


class HealthPlan(BaseModel):
    health_score: float
    subscores: Subscores
    insights: List[str]
    actions: List[str]
    disclaimer: str = (
        "This analysis is for informational purposes only and does not constitute "
        "medical advice. Always consult a qualified healthcare provider before making "
        "changes to your health regimen."
    )
