from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey

from app.models.base import BareBaseModel


class User(BareBaseModel):
    """User database model."""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    created_by = Column(
        Integer,
        ForeignKey('users.id'),
        nullable=True  # self registration case
    )
    modified_at = Column(
        DateTime,
        onupdate=datetime.now,
        nullable=True
    )
    modified_by = Column(
        Integer,
        ForeignKey('users.id'),
        nullable=True  # self registration case
    )
