from enum import StrEnum


class WorkflowStatus(StrEnum):
    DRAFT = "draft"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"


class WorkflowAction(StrEnum):
    START = "start"
    REQUEST_APPROVAL = "request_approval"
    APPROVE = "approve"
    REJECT = "reject"
    COMPLETE = "complete"
    FAIL = "fail"


TRANSITIONS = {
    (WorkflowStatus.DRAFT, WorkflowAction.START): WorkflowStatus.RUNNING,
    (WorkflowStatus.RUNNING, WorkflowAction.REQUEST_APPROVAL): (
        WorkflowStatus.WAITING_APPROVAL
    ),
    (WorkflowStatus.RUNNING, WorkflowAction.COMPLETE): WorkflowStatus.COMPLETED,
    (WorkflowStatus.RUNNING, WorkflowAction.FAIL): WorkflowStatus.FAILED,
    (WorkflowStatus.WAITING_APPROVAL, WorkflowAction.APPROVE): WorkflowStatus.RUNNING,
    (WorkflowStatus.WAITING_APPROVAL, WorkflowAction.REJECT): WorkflowStatus.REJECTED,
}


def transition(status: WorkflowStatus, action: WorkflowAction) -> WorkflowStatus:
    try:
        return TRANSITIONS[(status, action)]
    except KeyError as exc:
        raise ValueError(f"Cannot {action.value} a workflow in {status.value}") from exc
