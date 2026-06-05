"""
Base model configuration for all database models.
Provides common fields and functionality.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

# Base class for all ORM models
Base = declarative_base()


class BaseModel(Base):
    """
    Abstract base model with common fields:
    - id: UUID primary key
    - created_at: Timestamp of creation
    - updated_at: Timestamp of last update
    """
    __abstract__ = True

    # These will be overridden in subclasses with proper columns
    # This is just for documentation
    
    def __repr__(self) -> str:
        """String representation of model instance."""
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', None)})>"

    def to_dict(self) -> dict:
        """
        Convert model instance to dictionary.
        Useful for serialization to JSON.
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
