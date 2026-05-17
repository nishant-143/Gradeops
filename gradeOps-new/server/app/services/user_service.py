"""
User service layer - Business logic for user operations.

Handles:
- User creation and authentication
- Role management
- User retrieval and updates
- Password hashing and verification
"""

import logging
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import User, UserRole
from app.schemas import UserCreate, UserUpdate, UserResponse
from app.core.security import hash_password, verify_password

logger = logging.getLogger(__name__)


class UserService:
    """Service layer for user operations."""
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """
        Create a new user (instructor or TA).
        
        Args:
            db: Database session
            user: UserCreate schema with email, password and role
            
        Returns:
            Created User object
            
        Raises:
            ValueError: If email already exists
        """
        try:
            # Hash the password
            password_hash = hash_password(user.password)
            
            db_user = User(
                email=user.email.lower(),
                password_hash=password_hash,
                role=user.role.value
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            logger.info(f"Created user: {db_user.email} ({db_user.role})")
            return db_user
            
        except IntegrityError as e:
            db.rollback()
            db.expire_all()
            logger.error(f"Email already exists: {user.email}")
            raise ValueError(f"Email {user.email} already registered")
        except Exception as e:
            db.rollback()
            db.expire_all()
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Retrieve user by email.
        
        Args:
            db: Database session
            email: User email to search
            
        Returns:
            User object or None if not found
        """
        try:
            user = db.query(User).filter(
                User.email == email.lower()
            ).first()
            return user
        except Exception as e:
            logger.error(f"Error retrieving user by email: {str(e)}")
            raise
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate user by email and password.
        
        Args:
            db: Database session
            email: User email
            password: Plain text password to verify
            
        Returns:
            User object if credentials are valid, None otherwise
        """
        try:
            user = UserService.get_user_by_email(db, email)
            if not user:
                logger.warning(f"Authentication failed: User {email} not found")
                return None
            
            # Verify password
            if not verify_password(password, user.password_hash):
                logger.warning(f"Authentication failed: Invalid password for {email}")
                return None
            
            logger.info(f"User authenticated successfully: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return None
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """
        Retrieve user by ID.
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            User object or None if not found
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()
            return user
        except Exception as e:
            logger.error(f"Error retrieving user by ID: {str(e)}")
            raise
    
    @staticmethod
    def get_all_users(db: Session, role: Optional[str] = None) -> List[User]:
        """
        Retrieve all users, optionally filtered by role.
        
        Args:
            db: Database session
            role: Optional role filter (instructor or ta)
            
        Returns:
            List of User objects
        """
        try:
            query = db.query(User)
            if role:
                query = query.filter(User.role == role)
            return query.all()
        except Exception as e:
            logger.error(f"Error retrieving users: {str(e)}")
            raise
    
    @staticmethod
    def update_user(db: Session, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        """
        Update user information.
        
        Args:
            db: Database session
            user_id: User UUID to update
            user_update: UserUpdate schema with new values
            
        Returns:
            Updated User object or None if not found
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User not found: {user_id}")
                return None
            
            update_data = user_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(user, key, value)
            
            db.commit()
            db.refresh(user)
            logger.info(f"Updated user: {user_id}")
            return user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user: {str(e)}")
            raise
    
    @staticmethod
    def delete_user(db: Session, user_id: UUID) -> bool:
        """
        Delete a user.
        
        Args:
            db: Database session
            user_id: User UUID to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User not found for deletion: {user_id}")
                return False
            
            db.delete(user)
            db.commit()
            logger.info(f"Deleted user: {user_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting user: {str(e)}")
            raise
    
    @staticmethod
    def is_instructor(db: Session, user_id: UUID) -> bool:
        """Check if user is an instructor."""
        user = UserService.get_user_by_id(db, user_id)
        return user and user.role == UserRole.INSTRUCTOR
    
    @staticmethod
    def is_ta(db: Session, user_id: UUID) -> bool:
        """Check if user is a TA."""
        user = UserService.get_user_by_id(db, user_id)
        return user and user.role == UserRole.TA
