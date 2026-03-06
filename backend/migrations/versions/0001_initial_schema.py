"""initial schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("tier", sa.String(50), nullable=False, default="free"),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(255), nullable=True),
        sa.Column("current_period_end", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_subscriptions_stripe_customer_id", "subscriptions", ["stripe_customer_id"])

    op.create_table(
        "bloodwork_entries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("test_date", sa.Date(), nullable=False),
        sa.Column("vitamin_d", sa.Float(), nullable=True),
        sa.Column("ldl", sa.Float(), nullable=True),
        sa.Column("hdl", sa.Float(), nullable=True),
        sa.Column("triglycerides", sa.Float(), nullable=True),
        sa.Column("a1c", sa.Float(), nullable=True),
        sa.Column("fasting_glucose", sa.Float(), nullable=True),
        sa.Column("crp", sa.Float(), nullable=True),
        sa.Column("testosterone_total", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_bloodwork_entries_user_id", "bloodwork_entries", ["user_id"])

    op.create_table(
        "lifestyle_entries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("sleep_hours", sa.Float(), nullable=True),
        sa.Column("steps", sa.Integer(), nullable=True),
        sa.Column("resting_hr", sa.Integer(), nullable=True),
        sa.Column("hrv", sa.Float(), nullable=True),
        sa.Column("workout_minutes", sa.Integer(), nullable=True),
        sa.Column("stress_1_10", sa.Integer(), nullable=True),
        sa.Column("diet_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_lifestyle_entries_user_id", "lifestyle_entries", ["user_id"])

    op.create_table(
        "uploaded_files",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("file_type", sa.String(50), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("stored_path", sa.String(500), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("parsed_summary", sa.Text(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_uploaded_files_user_id", "uploaded_files", ["user_id"])


def downgrade() -> None:
    op.drop_table("uploaded_files")
    op.drop_table("lifestyle_entries")
    op.drop_table("bloodwork_entries")
    op.drop_table("subscriptions")
    op.drop_table("users")
