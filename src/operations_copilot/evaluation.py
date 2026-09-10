from dataclasses import asdict, dataclass

from .planner import Planner
from .tools import ToolRegistry


@dataclass(frozen=True)
class EvaluationCase:
    request: str
    expected_tool: str
    expected_approval: bool


@dataclass(frozen=True)
class EvaluationResult:
    total: int
    passed: int
    tool_accuracy: float
    policy_accuracy: float


def evaluate_planner(
    planner: Planner,
    registry: ToolRegistry,
    cases: list[EvaluationCase],
) -> EvaluationResult:
    tool_matches = 0
    policy_matches = 0
    for case in cases:
        plan = planner.plan(case.request, registry)
        tool_matches += plan.tool_name == case.expected_tool
        policy_matches += (
            registry.get(plan.tool_name).requires_approval == case.expected_approval
        )
    total = len(cases)
    return EvaluationResult(
        total=total,
        passed=min(tool_matches, policy_matches),
        tool_accuracy=tool_matches / total if total else 1.0,
        policy_accuracy=policy_matches / total if total else 1.0,
    )


def evaluation_report(result: EvaluationResult) -> dict:
    return asdict(result)
