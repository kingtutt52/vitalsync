from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models here so Alembic autogenerate can detect them.
# Keep this list in sync as new models are added.
from app.models import user, health, files, billing  # noqa: F401, E402
