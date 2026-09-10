from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from .tools import ToolRegistry, ToolSpec


class MCPTransport(Protocol):
    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]: ...


@dataclass(frozen=True)
class MCPToolDefinition:
    name: str
    description: str
    requires_approval: bool


def register_mcp_tools(
    registry: ToolRegistry,
    transport: MCPTransport,
    definitions: list[MCPToolDefinition],
) -> None:
    for definition in definitions:
        def handler(
            arguments: dict[str, Any],
            tool_name: str = definition.name,
        ) -> dict[str, Any]:
            return transport.call_tool(tool_name, arguments)

        registry.register(
            ToolSpec(
                name=definition.name,
                description=definition.description,
                requires_approval=definition.requires_approval,
                handler=handler,
            )
        )
