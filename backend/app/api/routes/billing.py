from datetime import datetime

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.config import get_settings
from app.models.user import User
from app.models.billing import Subscription
from app.schemas.billing import CheckoutRequest, CheckoutResponse, SubscriptionStatus
from app.services.stripe_service import create_checkout_session, get_subscription_tier_from_event

settings = get_settings()
router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/create-checkout-session", response_model=CheckoutResponse)
def create_checkout(
    payload: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.validate_tier():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier '{payload.tier}'. Choose: premium_lite, vital_plus, vital_pro",
        )

    sub = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    existing_customer = sub.stripe_customer_id if sub else None

    try:
        url = create_checkout_session(
            user_id=current_user.id,
            user_email=current_user.email,
            tier=payload.tier,
            existing_customer_id=existing_customer,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Stripe error: {str(e)}",
        )

    return CheckoutResponse(checkout_url=url)


@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Stripe sends events here. We verify the signature and update subscription records.
    Register this URL in your Stripe dashboard under Webhooks.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event.get("type", "")

    if event_type in (
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
    ):
        parsed = get_subscription_tier_from_event(event)
        if not parsed:
            return {"status": "ignored"}

        customer_id, sub_id, tier, period_end = parsed
        is_active = event_type != "customer.subscription.deleted"

        # Find user by stripe_customer_id, or look up from metadata
        sub = db.query(Subscription).filter(
            Subscription.stripe_customer_id == customer_id
        ).first()

        # Fallback: try metadata on the event
        if not sub:
            user_id = (
                event.get("data", {})
                .get("object", {})
                .get("metadata", {})
                .get("user_id")
            )
            if user_id:
                sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()

        if sub:
            sub.stripe_customer_id = customer_id
            sub.stripe_subscription_id = sub_id
            sub.tier = tier if is_active else "free"
            sub.is_active = is_active
            sub.current_period_end = datetime.fromtimestamp(period_end) if period_end else None
            sub.updated_at = datetime.utcnow()
            db.commit()

    elif event_type == "invoice.payment_failed":
        # Could notify user via email in a real app
        pass

    return {"status": "ok"}


@router.get("/status", response_model=SubscriptionStatus)
def billing_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sub = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if not sub:
        # Return a free-tier stub — the row will be created next time they hit an endpoint
        return SubscriptionStatus(
            tier="free",
            is_active=True,
            stripe_customer_id=None,
            stripe_subscription_id=None,
            current_period_end=None,
        )
    return sub


@router.get("/wearables", tags=["wearables"])
def wearables_stub():
    """Wearables integration is coming soon. This endpoint is a placeholder."""
    return {
        "status": "coming_soon",
        "message": "Wearables integration (Apple Health, Garmin, Oura) is planned for Vital+ tier.",
    }
