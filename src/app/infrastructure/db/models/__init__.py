"""ORM models package. Importing it registers all models on ``Base.metadata``."""

from app.infrastructure.db.models.task import TaskModel

__all__ = ["TaskModel"]
