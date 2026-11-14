
from typing import Any

from incident_assistant.contracts.tool_contract import ToolError, ToolResult
from incident_assistant.tools.tool_dispatcher import dispatch_tool


ALLOWED_SPECIALIST_TOOLS = frozenset({
    "search_runbooks",
})


def dispatch_specialist_tool(
    tool_name: str,
    arguments: dict[str, Any],
) -> ToolResult:
    """Uzmanın yalnızca izinli araçları çalıştırmasını sağlar."""

    if tool_name not in ALLOWED_SPECIALIST_TOOLS:
        return ToolResult(
            status="error",
            error=ToolError(
                code="SPECIALIST_TOOL_FORBIDDEN",
                message="Tool is not allowed for this specialist",
            ),
        )

    # Ortak dispatcher parametre doğrulamasını
    # ve gerçek araç çağrısını gerçekleştirir.
    return dispatch_tool(tool_name, arguments)
