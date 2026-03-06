#!/usr/bin/env python3
"""
Seed script: creates a test user with example health data.

Usage:
    python seed.py

Requires the database to be running and migrations to have run:
    alembic upgrade head
"""
import sys
import os
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(__file__))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.health import BloodworkEntry, LifestyleEntry
from app.models.billing import Subscription
from app.core.security import hash_password

TEST_EMAIL = "demo@vitalsync.dev"
TEST_PASSWORD = "VitalSync123!"
TEST_NAME = "Demo User"


def seed():
    db = SessionLocal()

    try:
        existing = db.query(User).filter(User.email == TEST_EMAIL).first()
        if existing:
            print(f"[seed] User {TEST_EMAIL} already exists. Skipping.")
            return

        import uuid

        user = User(
            id=str(uuid.uuid4()),
            email=TEST_EMAIL,
            name=TEST_NAME,
            hashed_password=hash_password(TEST_PASSWORD),
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db.add(user)
        db.flush()

        sub = Subscription(
            id=str(uuid.uuid4()),
            user_id=user.id,
            tier="premium_lite",  # give the demo user access to plan generation
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(sub)

        bw = BloodworkEntry(
            id=str(uuid.uuid4()),
            user_id=user.id,
            test_date=date(2024, 12, 15),
            vitamin_d=24.0,   # insufficient → will trigger rule
            ldl=138.0,         # borderline high
            hdl=52.0,
            triglycerides=145.0,
            a1c=5.8,           # pre-diabetic range
            fasting_glucose=102.0,
            crp=2.1,           # intermediate
            testosterone_total=410.0,
            created_at=datetime.utcnow(),
        )
        db.add(bw)

        ls = LifestyleEntry(
            id=str(uuid.uuid4()),
            user_id=user.id,
            entry_date=date.today(),
            sleep_hours=6.5,   # below 7 → rule fires
            steps=6200,        # below 7000
            resting_hr=68,
            hrv=45.0,
            workout_minutes=25,
            stress_1_10=7,     # elevated
            diet_notes="High carb day; had pasta for lunch and skipped veggies.",
            created_at=datetime.utcnow(),
        )
        db.add(ls)

        db.commit()
        print(f"[seed] Created user: {TEST_EMAIL} / {TEST_PASSWORD}")
        print(f"[seed] Subscription: premium_lite")
        print(f"[seed] Bloodwork and lifestyle entries added.")

    except Exception as e:
        db.rollback()
        print(f"[seed] Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
