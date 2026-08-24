"""Base model mixin and common columns."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from app.core.database import Base


class TimestampMixin:
    """Mixin for audit timestamps."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


def generate_uuid() -> str:
    return str(uuid.uuid4())
