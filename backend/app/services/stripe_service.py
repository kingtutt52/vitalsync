"""
Stripe integration helpers.

All Stripe calls are isolated here. The rest of the app only imports these functions,
making it straightforward to swap payment providers or add PayPal later.
"""
from typing import Optional
import stripe

from app.core.config import get_settings

settings = get_settings()
stripe.api_key = settings.stripe_secret_key

TIER_TO_PRICE = {
    "premium_lite": settings.stripe_price_premium_lite,
    "vital_plus": settings.stripe_price_vital_plus,
    "vital_pro": settings.stripe_price_vital_pro,
}

PRICE_TO_TIER = {v: k for k, v in TIER_TO_PRICE.items()}


def create_checkout_session(
    user_id: str,
    user_email: str,
    tier: str,
    existing_customer_id: Optional[str] = None,
) -> str:
    """
    Create a Stripe Checkout Session and return the redirect URL.
    """
    price_id = TIER_TO_PRICE.get(tier)
    if not price_id:
        raise ValueError(f"Unknown tier: {tier}")

    session_kwargs = {
        "payment_method_types": ["card"],
        "mode": "subscription",
        "line_items": [{"price": price_id, "quantity": 1}],
        "success_url": f"{settings.app_base_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
        "cancel_url": f"{settings.app_base_url}/billing/cancel",
        "metadata": {"user_id": user_id, "tier": tier},
        "subscription_data": {"metadata": {"user_id": user_id, "tier": tier}},
        "customer_email": user_email if not existing_customer_id else None,
        "customer": existing_customer_id,
    }
    # Clean up None values — Stripe rejects them
    session_kwargs = {k: v for k, v in session_kwargs.items() if v is not None}

    session = stripe.checkout.Session.create(**session_kwargs)
    return session.url


def get_subscription_tier_from_event(event: dict) -> Optional[tuple[str, str, str, int]]:
    """
    Parse a Stripe webhook event for subscription lifecycle events.
    Returns (stripe_customer_id, stripe_subscription_id, tier, period_end_timestamp) or None.
    """
    sub_obj = event.get("data", {}).get("object", {})
    customer_id = sub_obj.get("customer")
    sub_id = sub_obj.get("id")
    period_end = sub_obj.get("current_period_end")
    items = sub_obj.get("items", {}).get("data", [])

    if not items:
        return None

    price_id = items[0].get("price", {}).get("id")
    tier = PRICE_TO_TIER.get(price_id, "free")

    return customer_id, sub_id, tier, period_end
