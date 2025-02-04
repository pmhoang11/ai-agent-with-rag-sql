from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey

from app.models.base import BareBaseModel


class Space(BareBaseModel):
    """User database model."""
    __tablename__ = 'spaces'
    id = Column(Integer, primary_key=True)
    owner_id = Column(
        Integer,
        ForeignKey('users.id'),
        nullable=False
    )
    workspace_id = Column(
        Integer,
        ForeignKey('workspaces.id'),
        nullable=False
    )
    name = Column(String)
    last_updated = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=True
    )
    num_documents = Column(
        Integer,
        default=0,
    )
