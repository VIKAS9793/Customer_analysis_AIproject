"""
Authentication and Authorization - Handles user authentication and authorization.

This module provides functionality for authenticating users and authorizing
access to various parts of the FinConnectAI framework.
"""

import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import jwt
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class User(BaseModel):
    """User model for authentication."""

    user_id: str
    username: str
    email: str
    role: str
    permissions: List[str]
    created_at: datetime
    last_login: Optional[datetime] = None


class AuthManager:
    """
    Manager for authentication and authorization.

    This class handles user authentication and authorization for the
    FinConnectAI framework.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize an authentication manager.

        Args:
            config: Configuration for the manager
        """
        self.config = config
        self.secret_key = os.environ.get("JWT_SECRET_KEY", "default-secret-key")
        self.token_expiry = config.get("token_expiry_minutes", 60)
        self.refresh_token_expiry = config.get("refresh_token_expiry_days", 7)

        # In a real implementation, this would use a database
        # For now, we'll use an in-memory store
        self.users = {}
        self.tokens = {}
        self.refresh_tokens = {}

        # Create a default admin user if enabled
        if config.get("create_default_admin", False):
            self._create_default_admin()

        logger.info("Initialized authentication manager")

    def _create_default_admin(self) -> None:
        """Create a default admin user."""
        admin_username = self.config.get("default_admin_username", "admin")
        admin_email = self.config.get("default_admin_email", "admin@example.com")

        # Check if admin user already exists
        for user in self.users.values():
            if user.username == admin_username or user.email == admin_email:
                logger.info("Default admin user already exists")
                return

        # Create admin user
        admin_id = str(uuid.uuid4())
        admin_user = User(
            user_id=admin_id,
            username=admin_username,
            email=admin_email,
            role="admin",
            permissions=["admin", "read", "write", "execute"],
            created_at=datetime.now(),
        )

        self.users[admin_id] = admin_user
        logger.info(f"Created default admin user: {admin_username}")

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user.

        Args:
            username: The username
            password: The password

        Returns:
            Authentication result with tokens if successful, None otherwise
        """
        logger.info(f"Authenticating user: {username}")

        # In a real implementation, this would verify credentials against a database
        # For now, we'll use a mock implementation

        # Find user by username
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break

        if not user:
            logger.warning(f"User not found: {username}")
            return None

        # In a real implementation, this would verify the password
        # For now, we'll assume the password is correct for the mock

        # Generate tokens
        access_token = self._generate_token(user)
        refresh_token = self._generate_refresh_token(user)

        # Update last login
        user.last_login = datetime.now()

        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh an access token.

        Args:
            refresh_token: The refresh token

        Returns:
            New tokens if successful, None otherwise
        """
        logger.info("Refreshing access token")

        # Verify refresh token
        user_id = self.refresh_tokens.get(refresh_token)
        if not user_id:
            logger.warning("Invalid refresh token")
            return None

        # Get user
        user = self.users.get(user_id)
        if not user:
            logger.warning(f"User not found for refresh token: {user_id}")
            return None

        # Generate new tokens
        access_token = self._generate_token(user)
        new_refresh_token = self._generate_refresh_token(user)

        # Invalidate old refresh token
        self.refresh_tokens.pop(refresh_token, None)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify an access token.

        Args:
            token: The access token

        Returns:
            Token payload if valid, None otherwise
        """
        logger.debug("Verifying access token")

        try:
            # Verify token signature and expiry
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])

            # Check if token is in the blacklist
            if token in self.tokens and self.tokens[token] == "blacklisted":
                logger.warning("Token is blacklisted")
                return None

            # Get user
            user_id = payload.get("sub")
            user = self.users.get(user_id)

            if not user:
                logger.warning(f"User not found for token: {user_id}")
                return None

            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None

    def invalidate_token(self, token: str) -> bool:
        """
        Invalidate an access token.

        Args:
            token: The access token

        Returns:
            True if successful, False otherwise
        """
        logger.info("Invalidating access token")

        try:
            # Verify token first
            jwt.decode(token, self.secret_key, algorithms=["HS256"])

            # Add token to blacklist
            self.tokens[token] = "blacklisted"

            return True
        except jwt.InvalidTokenError:
            logger.warning("Invalid token for invalidation")
            return False

    def invalidate_all_tokens(self, user_id: str) -> bool:
        """
        Invalidate all tokens for a user.

        Args:
            user_id: The user ID

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Invalidating all tokens for user: {user_id}")

        # In a real implementation, this would invalidate all tokens in a database
        # For now, we'll assume it's successful

        return True

    def has_permission(self, user_id: str, permission: str) -> bool:
        """
        Check if a user has a permission.

        Args:
            user_id: The user ID
            permission: The permission to check

        Returns:
            True if the user has the permission, False otherwise
        """
        logger.debug(f"Checking permission: {permission} for user: {user_id}")

        # Get user
        user = self.users.get(user_id)
        if not user:
            logger.warning(f"User not found for permission check: {user_id}")
            return False

        # Check if user has admin role
        if user.role == "admin":
            return True

        # Check if user has the permission
        return permission in user.permissions

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "user",
        permissions: Optional[List[str]] = None,
    ) -> Optional[User]:
        """
        Create a new user.

        Args:
            username: The username
            email: The email
            password: The password
            role: The role
            permissions: The permissions

        Returns:
            The created user if successful, None otherwise
        """
        logger.info(f"Creating user: {username}")

        # Check if username or email already exists
        for user in self.users.values():
            if user.username == username:
                logger.warning(f"Username already exists: {username}")
                return None
            if user.email == email:
                logger.warning(f"Email already exists: {email}")
                return None

        # Create user
        user_id = str(uuid.uuid4())
        permissions = permissions or ["read"]

        user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            permissions=permissions,
            created_at=datetime.now(),
        )

        # In a real implementation, this would hash the password and store it
        # For now, we'll just store the user

        self.users[user_id] = user

        return user

    def _generate_token(self, user: User) -> str:
        """
        Generate an access token for a user.

        Args:
            user: The user

        Returns:
            The generated token
        """
        now = datetime.now()
        expiry = now + timedelta(minutes=self.token_expiry)

        payload = {
            "sub": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "permissions": user.permissions,
            "iat": int(time.time()),
            "exp": int(expiry.timestamp()),
        }

        token = jwt.encode(payload, self.secret_key, algorithm="HS256")

        return token

    def _generate_refresh_token(self, user: User) -> str:
        """
        Generate a refresh token for a user.

        Args:
            user: The user

        Returns:
            The generated refresh token
        """
        refresh_token = str(uuid.uuid4())

        # Store refresh token
        self.refresh_tokens[refresh_token] = user.user_id

        return refresh_token
