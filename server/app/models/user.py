"""
User model for instructors and TAs.
Handles authentication roles and metadata.

Note: This is the ORM model (database schema).
For API validation, use schemas/user.py
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import Base


class UserRole(str, Enum):
    """Valid user roles in the system."""
    INSTRUCTOR = "instructor"
    TA = "ta"


class User(Base):
    """
    Represents an instructor or TA in the system.
    
    Attributes:
        id: Unique identifier (UUID)
        email: User's email (unique, used for authentication)
        role: Either 'instructor' or 'ta'
        created_at: When user was created
        updated_at: When user was last modified
    
    Constraints:
        - Email must be unique
        - Role must be one of: 'instructor', 'ta'
    """
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique user identifier"
    )
    
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User email (must be unique)"
    )
    
    password_hash = Column(
        String(255),
        nullable=False,
        comment="Hashed password using bcrypt"
    )
    
    role = Column(
        String(20),
        nullable=False,
        comment="User role: instructor or ta"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when user was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when user was last updated"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
