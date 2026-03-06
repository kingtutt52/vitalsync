from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    tier: str  # premium_lite | vital_plus | vital_pro

    def validate_tier(self) -> bool:
        return self.tier in ("premium_lite", "vital_plus", "vital_pro")


class CheckoutResponse(BaseModel):
    checkout_url: str


class SubscriptionStatus(BaseModel):
    tier: str
    is_active: bool
    stripe_customer_id: Optional[str]
    stripe_subscription_id: Optional[str]
    current_period_end: Optional[datetime]

    model_config = {"from_attributes": True}
