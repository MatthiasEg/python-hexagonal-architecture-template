"""SQLAlchemy ORM model for the tasks table."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base, TimestampMixin


class TaskModel(Base, TimestampMixin):
    """ORM mapping for a Task aggregate."""

    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String, default="", server_default="")
    status: Mapped[str] = mapped_column(String(20))
