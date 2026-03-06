from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_tier
from app.models.user import User
from app.models.health import BloodworkEntry, LifestyleEntry
from app.schemas.ai import HealthPlan, Subscores
from app.services.health_score import compute_health_plan

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post(
    "/generate-plan",
    response_model=HealthPlan,
    dependencies=[Depends(require_tier("premium_lite"))],
)
def generate_plan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate a personalised Health Score and Action Plan from the user's latest data.
    Requires Premium Lite or higher.
    """
    latest_bw = (
        db.query(BloodworkEntry)
        .filter(BloodworkEntry.user_id == current_user.id)
        .order_by(BloodworkEntry.test_date.desc())
        .first()
    )
    latest_ls = (
        db.query(LifestyleEntry)
        .filter(LifestyleEntry.user_id == current_user.id)
        .order_by(LifestyleEntry.entry_date.desc())
        .first()
    )

    result = compute_health_plan(latest_bw, latest_ls)

    return HealthPlan(
        health_score=result.health_score,
        subscores=Subscores(**result.subscores),
        insights=result.insights,
        actions=result.actions,
    )
