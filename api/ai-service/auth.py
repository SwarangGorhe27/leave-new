from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional

from config import settings

security = HTTPBearer(auto_error=False)


async def verify_token(credentials: HTTPAuthorizationCredentials = None, request: Request = None):
    """Verify JWT token from the Django backend."""
    token = None
    if credentials:
        token = credentials.credentials
    elif request:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return {
            "user_id": payload.get("user_id"),
            "tenant_id": payload.get("tenant_id"),
            "role": payload.get("role_type"),
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
