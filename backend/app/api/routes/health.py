from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.health import BloodworkEntry, LifestyleEntry
from app.schemas.health import (
    BloodworkCreate, BloodworkResponse,
    LifestyleCreate, LifestyleResponse,
    HealthSummary,
)

router = APIRouter(prefix="/health", tags=["health"])


@router.post("/bloodwork", response_model=BloodworkResponse, status_code=status.HTTP_201_CREATED)
def create_bloodwork(
    payload: BloodworkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = BloodworkEntry(user_id=current_user.id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/bloodwork", response_model=List[BloodworkResponse])
def list_bloodwork(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(BloodworkEntry)
        .filter(BloodworkEntry.user_id == current_user.id)
        .order_by(BloodworkEntry.test_date.desc())
        .all()
    )


@router.post("/lifestyle", response_model=LifestyleResponse, status_code=status.HTTP_201_CREATED)
def create_lifestyle(
    payload: LifestyleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = LifestyleEntry(user_id=current_user.id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/lifestyle", response_model=List[LifestyleResponse])
def list_lifestyle(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(LifestyleEntry)
        .filter(LifestyleEntry.user_id == current_user.id)
        .order_by(LifestyleEntry.entry_date.desc())
        .all()
    )


@router.get("/summary", response_model=HealthSummary)
def health_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
    bw_count = db.query(BloodworkEntry).filter(BloodworkEntry.user_id == current_user.id).count()
    ls_count = db.query(LifestyleEntry).filter(LifestyleEntry.user_id == current_user.id).count()

    return HealthSummary(
        latest_bloodwork=latest_bw,
        latest_lifestyle=latest_ls,
        bloodwork_count=bw_count,
        lifestyle_count=ls_count,
    )
