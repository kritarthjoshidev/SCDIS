# backend/security/security_manager.py

import logging
from datetime import datetime, timedelta, UTC
from typing import Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class SecurityManager:
    def __init__(self):
        self.fake_user = {
            "username": "enterprise_admin",
            "role": "admin",
            "permissions": ["decision", "runtime_control", "monitoring"]
        }

    # ---------------------------------------------------
    # Authentication (mock enterprise auth)
    # ---------------------------------------------------
    def authenticate_token(self, token: str) -> Optional[Dict]:
        """
        In production this would verify JWT.
        For now enterprise demo uses mock validation.
        """
        if token:
            return self.fake_user
        return None

    # ---------------------------------------------------
    # FastAPI dependency
    # ---------------------------------------------------
    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> Dict:
        user = self.authenticate_token(token)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        return user

    # ---------------------------------------------------
    # FastAPI dependency - Admin only
    # ---------------------------------------------------
    async def get_current_admin(self, token: str = Depends(oauth2_scheme)) -> Dict:
        user = self.authenticate_token(token)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        if user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required",
            )

        return user

    # ---------------------------------------------------
    # Token verification dependency
    # ---------------------------------------------------
    async def verify_token(self, token: str = Depends(oauth2_scheme)) -> Dict:
        """
        Verifies token and returns user info (alias for get_current_user)
        """
        return await self.get_current_user(token)

    # ---------------------------------------------------
    # Permission check
    # ---------------------------------------------------
    def check_permission(self, user: Dict, permission: str):
        if permission not in user.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )


# Singleton
security_manager = SecurityManager()
