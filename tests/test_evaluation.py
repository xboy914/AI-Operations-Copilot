from operations_copilot.evaluation import EvaluationCase, evaluate_planner, evaluation_report
from operations_copilot.planner import HeuristicPlanner
from operations_copilot.tools import default_registry


def test_baseline_planner_and_risk_policy_evaluation():
    result = evaluate_planner(
        HeuristicPlanner(),
        default_registry(),
        [
            EvaluationCase("Build the weekly report", "report_builder", False),
            EvaluationCase("گزارش عملیات را بساز", "report_builder", False),
            EvaluationCase("Follow up with supplier", "task_creator", True),
        ],
    )
    assert evaluation_report(result) == {
        "total": 3,
        "passed": 3,
        "tool_accuracy": 1.0,
        "policy_accuracy": 1.0,
    }


def test_empty_evaluation_suite_is_well_defined():
    result = evaluate_planner(HeuristicPlanner(), default_registry(), [])
    assert result.tool_accuracy == 1.0
    assert result.policy_accuracy == 1.0
