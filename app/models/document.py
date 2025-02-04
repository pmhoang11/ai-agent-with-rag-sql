from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey

from app.models.base import BareBaseModel


class Document(BareBaseModel):
    """User database model."""
    __tablename__ = 'documents'
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
    space_id = Column(
        Integer,
        ForeignKey('spaces.id'),
        nullable=False
    )
    title = Column(String)
    uploaded_date = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False
    )

