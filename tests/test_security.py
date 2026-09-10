import pytest
from fastapi import HTTPException

from operations_copilot.config import Settings
from operations_copilot.security import (
    Permission,
    Role,
    create_access_token,
    decode_access_token,
    has_permission,
)


def settings() -> Settings:
    return Settings(jwt_secret="test-secret", access_token_minutes=5)


def test_role_permissions_are_separated():
    assert has_permission(Role.OPERATOR, Permission.RUN_WORKFLOW)
    assert not has_permission(Role.OPERATOR, Permission.APPROVE_WORKFLOW)
    assert has_permission(Role.APPROVER, Permission.APPROVE_WORKFLOW)
    assert has_permission(Role.ADMIN, Permission.VIEW_AUDIT)


def test_access_token_round_trip():
    token = create_access_token("user-1", "admin@example.com", Role.ADMIN, settings())
    principal = decode_access_token(token, settings())

    assert principal.user_id == "user-1"
    assert principal.role is Role.ADMIN


def test_invalid_token_is_rejected():
    with pytest.raises(HTTPException) as error:
        decode_access_token("not-a-token", settings())

    assert error.value.status_code == 401
