from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .domain import WorkflowAction, WorkflowStatus


class BootstrapRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12)
    bootstrap_secret: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResult(BaseModel):
    access_token: str
    token_type: str = "bearer"


class WorkflowCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    request: str = Field(min_length=10, max_length=5000)


class WorkflowTransition(BaseModel):
    action: WorkflowAction


class WorkflowView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    title: str
    request: str
    status: WorkflowStatus
    created_at: datetime
