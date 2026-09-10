from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from .agent import runtime
from .config import get_settings
from .database import AuditEvent, User, WorkflowRun, get_db
from .domain import WorkflowAction, WorkflowStatus, transition
from .schemas import (
    BootstrapRequest,
    LoginRequest,
    TokenResult,
    WorkflowCreate,
    WorkflowTransition,
    WorkflowView,
)
from .security import (
    Permission,
    Principal,
    Role,
    create_access_token,
    password_hash,
    require,
)

settings = get_settings()
app = FastAPI(title="AI Operations Copilot", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization", "X-Bootstrap-Secret"],
)

Db = Annotated[Session, Depends(get_db)]


class AgentRunRequest(BaseModel):
    request: str
    thread_id: str | None = None


class AgentDecision(BaseModel):
    approved: bool


class TransitionPreview(BaseModel):
    status: WorkflowStatus
    action: WorkflowAction


class TransitionPreviewResult(BaseModel):
    previous_status: WorkflowStatus
    action: WorkflowAction
    status: WorkflowStatus


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": app.version}


@app.get("/capabilities")
def capabilities() -> dict[str, list[str]]:
    return {
        "workflow_statuses": [item.value for item in WorkflowStatus],
        "human_actions": ["approve", "reject"],
        "permissions": [item.value for item in Permission],
    }


@app.post("/workflows/transition", response_model=TransitionPreviewResult)
def preview_transition(request: TransitionPreview) -> TransitionPreviewResult:
    try:
        status = transition(request.status, request.action)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return TransitionPreviewResult(
        previous_status=request.status,
        action=request.action,
        status=status,
    )


@app.post("/auth/bootstrap", response_model=TokenResult, status_code=201)
def bootstrap_admin(
    request: BootstrapRequest,
    db: Db,
    x_bootstrap_secret: Annotated[str | None, Header()] = None,
) -> TokenResult:
    if x_bootstrap_secret != settings.bootstrap_secret:
        raise HTTPException(status_code=403, detail="Invalid bootstrap secret")
    if db.scalar(select(User.id).limit(1)) is not None:
        raise HTTPException(status_code=409, detail="Bootstrap already completed")
    user = User(
        email=request.email.lower(),
        password_hash=password_hash.hash(request.password),
        role=Role.ADMIN.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResult(
        access_token=create_access_token(str(user.id), user.email, Role.ADMIN, settings)
    )


@app.post("/auth/token", response_model=TokenResult)
def login(request: LoginRequest, db: Db) -> TokenResult:
    user = db.scalar(select(User).where(User.email == request.email.lower()))
    if user is None or not password_hash.verify(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResult(
        access_token=create_access_token(str(user.id), user.email, Role(user.role), settings)
    )


@app.post("/workflows", response_model=WorkflowView, status_code=201)
def create_workflow(
    request: WorkflowCreate,
    db: Db,
    principal: Annotated[Principal, Depends(require(Permission.CREATE_WORKFLOW))],
) -> WorkflowRun:
    workflow = WorkflowRun(
        owner_id=UUID(principal.user_id),
        title=request.title,
        request=request.request,
    )
    db.add(workflow)
    db.flush()
    db.add(
        AuditEvent(
            workflow_id=workflow.id,
            event_type="workflow.created",
            actor=principal.email,
            payload={"title": workflow.title},
        )
    )
    db.commit()
    db.refresh(workflow)
    return workflow


@app.get("/workflows", response_model=list[WorkflowView])
def list_workflows(
    db: Db,
    principal: Annotated[Principal, Depends(require(Permission.CREATE_WORKFLOW))],
) -> list[WorkflowRun]:
    query = select(WorkflowRun).order_by(WorkflowRun.created_at.desc())
    if principal.role is not Role.ADMIN:
        query = query.where(WorkflowRun.owner_id == UUID(principal.user_id))
    return list(db.scalars(query))


@app.post("/workflows/{workflow_id}/transition", response_model=WorkflowView)
def transition_workflow(
    workflow_id: UUID,
    request: WorkflowTransition,
    db: Db,
    principal: Annotated[Principal, Depends(require(Permission.RUN_WORKFLOW))],
) -> WorkflowRun:
    workflow = db.get(WorkflowRun, workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if (
        request.action in {WorkflowAction.APPROVE, WorkflowAction.REJECT}
        and principal.role not in {Role.APPROVER, Role.ADMIN}
    ):
        raise HTTPException(status_code=403, detail="Approver role required")
    try:
        workflow.status = transition(WorkflowStatus(workflow.status), request.action).value
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    db.add(
        AuditEvent(
            workflow_id=workflow.id,
            event_type=f"workflow.{request.action.value}",
            actor=principal.email,
            payload={"status": workflow.status},
        )
    )
    db.commit()
    db.refresh(workflow)
    return workflow


@app.get("/tools")
def list_tools(
    principal: Annotated[Principal, Depends(require(Permission.RUN_WORKFLOW))],
) -> list[dict]:
    return runtime.registry.manifest()


@app.post("/agent/runs")
def start_agent_run(
    request: AgentRunRequest,
    principal: Annotated[Principal, Depends(require(Permission.RUN_WORKFLOW))],
) -> dict:
    return runtime.start(request.request, request.thread_id)


@app.post("/agent/runs/{thread_id}/decision")
def decide_agent_run(
    thread_id: str,
    request: AgentDecision,
    principal: Annotated[Principal, Depends(require(Permission.APPROVE_WORKFLOW))],
) -> dict:
    return runtime.resume(thread_id, request.approved)
