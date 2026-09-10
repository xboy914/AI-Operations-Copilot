from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from pydantic import BaseModel

from .config import Settings, get_settings

password_hash = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)


class Role(StrEnum):
    OPERATOR = "operator"
    APPROVER = "approver"
    ADMIN = "admin"


class Permission(StrEnum):
    CREATE_WORKFLOW = "workflow:create"
    RUN_WORKFLOW = "workflow:run"
    APPROVE_WORKFLOW = "workflow:approve"
    VIEW_AUDIT = "audit:view"


ROLE_PERMISSIONS = {
    Role.OPERATOR: {Permission.CREATE_WORKFLOW, Permission.RUN_WORKFLOW},
    Role.APPROVER: {Permission.APPROVE_WORKFLOW, Permission.VIEW_AUDIT},
    Role.ADMIN: set(Permission),
}


class Principal(BaseModel):
    user_id: str
    email: str
    role: Role


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS[role]


def create_access_token(
    user_id: str,
    email: str,
    role: Role,
    settings: Settings,
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role.value,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> Principal:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return Principal(
            user_id=payload["sub"],
            email=payload["email"],
            role=Role(payload["role"]),
        )
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from exc


def get_principal(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Principal:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return decode_access_token(credentials.credentials, settings)


def require(permission: Permission):
    def dependency(principal: Annotated[Principal, Depends(get_principal)]) -> Principal:
        if not has_permission(principal.role, permission):
            raise HTTPException(status_code=403, detail=f"Missing permission: {permission.value}")
        return principal

    return dependency
