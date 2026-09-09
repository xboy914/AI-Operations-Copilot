from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import get_settings
from .domain import WorkflowAction, WorkflowStatus, transition

settings = get_settings()
app = FastAPI(
    title="AI Operations Copilot",
    version="0.1.0",
    description="Auditable agentic workflows with human approval.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


class TransitionRequest(BaseModel):
    status: WorkflowStatus
    action: WorkflowAction


class TransitionResult(BaseModel):
    previous_status: WorkflowStatus
    action: WorkflowAction
    status: WorkflowStatus


class WorkflowDraft(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    request: str = Field(min_length=10, max_length=5000)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": app.version}


@app.get("/capabilities")
def capabilities() -> dict[str, list[str]]:
    return {
        "workflow_statuses": [item.value for item in WorkflowStatus],
        "human_actions": ["approve", "reject"],
        "planned_tools": ["database_query", "report_builder", "task_creator"],
    }


@app.post("/workflows/transition", response_model=TransitionResult)
def preview_transition(request: TransitionRequest) -> TransitionResult:
    next_status = transition(request.status, request.action)
    return TransitionResult(
        previous_status=request.status,
        action=request.action,
        status=next_status,
    )
