import pytest

from operations_copilot.tools import ToolRegistry, ToolSpec, default_registry


def test_registry_exposes_risk_metadata_and_rejects_duplicates():
    registry = default_registry()
    manifest = {item["name"]: item for item in registry.manifest()}

    assert manifest["task_creator"]["requires_approval"] is True
    assert manifest["report_builder"]["requires_approval"] is False

    with pytest.raises(ValueError, match="already registered"):
        registry.register(
            ToolSpec("report_builder", "duplicate", False, lambda arguments: arguments)
        )


def test_registry_rejects_unknown_tools():
    with pytest.raises(ValueError, match="Unknown tool"):
        ToolRegistry().get("missing")
