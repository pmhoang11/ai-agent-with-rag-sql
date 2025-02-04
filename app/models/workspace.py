from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey

from app.models.base import BareBaseModel


class Workspace(BareBaseModel):
    """User database model."""
    __tablename__ = 'workspaces'
    id = Column(Integer, primary_key=True)
    owner_id = Column(
        Integer,
        ForeignKey('users.id'),
        nullable=False
    )
    name = Column(String)
    last_updated = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
    )

