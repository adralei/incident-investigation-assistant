
from typing import Any

from incident_tools import get_logs, get_deployments
from service_tools import get_service_status
from tool_contract import ToolError, ToolResult


# İzin verilen araçlar
TOOL_REGISTRY = {
    "get_logs": get_logs,
    "get_service_status": get_service_status,
    "get_deployments": get_deployments,
}

REQUIRED_ARGUMENTS = {
    "service",
    "start_time",
    "end_time",
}


def dispatch_tool(
    tool_name: str,
    arguments: dict[str, Any],
) -> ToolResult:
    """Araç çağrısını kontrol ederek ilgili fonksiyona yönlendirir."""

    # 1. Araç ismini kontrol et
    if tool_name not in TOOL_REGISTRY:
        return ToolResult(
            status="error",
            error=ToolError(
                code="UNKNOWN_TOOL",
                message=f"Tool '{tool_name}' is not allowed",
            ),
        )

    # 2. Parametre yapısını kontrol et
    if not isinstance(arguments, dict):
        return ToolResult(
            status="error",
            error=ToolError(
                code="INVALID_ARGUMENTS",
                message="Arguments must be a dictionary",
            ),
        )

    # 3. Eksik veya fazla alanları kontrol et
    if set(arguments.keys()) != REQUIRED_ARGUMENTS:
        return ToolResult(
            status="error",
            error=ToolError(
                code="INVALID_ARGUMENTS",
                message="Expected service, start_time and end_time",
            ),
        )

    # 4. Parametre tiplerini kontrol et
    if not all(
        isinstance(value, str)
        for value in arguments.values()
    ):
        return ToolResult(
            status="error",
            error=ToolError(
                code="INVALID_ARGUMENTS",
                message="All arguments must be strings",
            ),
        )

    # 5. İlgili Python fonksiyonunu çalıştır
    tool_function = TOOL_REGISTRY[tool_name]

    try:
        result = tool_function(**arguments)
    except Exception as exc:
        # Beklenmeyen hataların agent döngüsünü
        # kontrolsüz biçimde durdurmasını önler.
        # İç hata ayrıntıları modele gönderilmez.
        return ToolResult(
            status="error",
            error=ToolError(
                code="TOOL_EXECUTION_ERROR",
                message="Tool execution failed",
            ),
        )

    # 6. Araç sonuç sözleşmesini kontrol et
    if not isinstance(result, ToolResult):
        return ToolResult(
            status="error",
            error=ToolError(
                code="INVALID_TOOL_RESULT",
                message="Tool returned an invalid result type",
            ),
        )

    return result


if __name__ == "__main__":

    valid_arguments = {
        "service": "checkout-api",
        "start_time": "2026-10-20T09:00:00Z",
        "end_time": "2026-10-20T09:15:00Z",
    }

    print("--- VALID TOOL CALL ---")

    result = dispatch_tool(
        "get_logs",
        valid_arguments,
    )

    print("Status:", result.status)

    if result.status == "success":
        print("Log count:", result.data["count"])

    print("\n--- UNKNOWN TOOL ---")

    result = dispatch_tool(
        "restart_service",
        valid_arguments,
    )

    print("Status:", result.status)
    print("Error:", result.error.code)

    print("\n--- INVALID ARGUMENTS ---")

    result = dispatch_tool(
        "get_logs",
        {"service": "checkout-api"},
    )

    print("Status:", result.status)
    print("Error:", result.error.code)
