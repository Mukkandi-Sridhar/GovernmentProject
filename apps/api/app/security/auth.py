from __future__ import annotations

from functools import lru_cache
from typing import Any

import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials as firebase_credentials

from app.config import Settings, get_settings

security = HTTPBearer(auto_error=False)


@lru_cache
def _firebase_app(credentials_path: str | None) -> firebase_admin.App | None:
    if not firebase_admin._apps:
        if credentials_path:
            cred = firebase_credentials.Certificate(credentials_path)
            return firebase_admin.initialize_app(cred)
        return firebase_admin.initialize_app()
    return firebase_admin.get_app()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    if settings.disable_auth:
        return {"uid": "local-dev", "roles": ["admin", "reviewer"]}

    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing auth token")

    _firebase_app(settings.google_application_credentials)
    try:
        decoded = firebase_auth.verify_id_token(credentials.credentials)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth token") from exc

    return {
        "uid": decoded.get("uid", "unknown"),
        "roles": decoded.get("roles", []),
    }


def require_roles(*required: str):
    async def _checker(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
        roles = set(user.get("roles", []))
        if not any(role in roles for role in required):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user

    return _checker

