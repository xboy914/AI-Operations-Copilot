from operations_copilot.mcp_adapter import MCPToolDefinition, register_mcp_tools
from operations_copilot.tools import ToolRegistry


class FakeTransport:
    def call_tool(self, name, arguments):
        return {"name": name, "arguments": arguments}


def test_mcp_adapter_preserves_risk_policy_and_delegates_calls():
    registry = ToolRegistry()
    register_mcp_tools(
        registry,
        FakeTransport(),
        [MCPToolDefinition("crm.update", "Update CRM record", True)],
    )

    tool = registry.get("crm.update")
    assert tool.requires_approval is True
    assert tool.handler({"id": 7}) == {
        "name": "crm.update",
        "arguments": {"id": 7},
    }
