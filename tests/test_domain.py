import pytest

from operations_copilot.domain import (
    WorkflowAction,
    WorkflowStatus,
    transition,
)


def test_happy_path_requires_approval_before_completion():
    status = transition(WorkflowStatus.DRAFT, WorkflowAction.START)
    status = transition(status, WorkflowAction.REQUEST_APPROVAL)
    assert status is WorkflowStatus.WAITING_APPROVAL

    status = transition(status, WorkflowAction.APPROVE)
    status = transition(status, WorkflowAction.COMPLETE)
    assert status is WorkflowStatus.COMPLETED


def test_rejected_workflow_cannot_restart():
    status = transition(WorkflowStatus.WAITING_APPROVAL, WorkflowAction.REJECT)
    assert status is WorkflowStatus.REJECTED

    with pytest.raises(ValueError, match="Cannot start"):
        transition(status, WorkflowAction.START)


def test_completion_is_not_allowed_while_waiting_for_approval():
    with pytest.raises(ValueError, match="Cannot complete"):
        transition(WorkflowStatus.WAITING_APPROVAL, WorkflowAction.COMPLETE)
