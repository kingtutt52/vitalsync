from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.user import User
from app.models.billing import Subscription

bearer_scheme = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_subscription(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Subscription:
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not sub:
        # Create a free tier on demand — this handles legacy users or the first call
        sub = Subscription(user_id=user.id, tier="free", is_active=True)
        db.add(sub)
        db.commit()
        db.refresh(sub)
    return sub


def require_tier(minimum_tier: str):
    """
    Dependency factory. Use as: Depends(require_tier("premium_lite"))
    Tier order: free < premium_lite < vital_plus < vital_pro
    """
    TIER_ORDER = {"free": 0, "premium_lite": 1, "vital_plus": 2, "vital_pro": 3}

    def checker(sub: Subscription = Depends(get_subscription)):
        if TIER_ORDER.get(sub.tier, 0) < TIER_ORDER.get(minimum_tier, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires {minimum_tier} or higher. Upgrade at /billing/create-checkout-session.",
            )
        return sub

    return checker
