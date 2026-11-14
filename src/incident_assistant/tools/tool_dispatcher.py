
from typing import Any

from incident_assistant.tools.incident_tools import get_logs, get_deployments
from incident_assistant.tools.service_tools import get_service_status
from incident_assistant.tools.runbook_tool import search_runbooks_tool

from incident_assistant.contracts.tool_contract import ToolError, ToolResult


# İzin verilen araçlar
TOOL_REGISTRY = {
    "get_logs": get_logs,
    "get_service_status": get_service_status,
    "get_deployments": get_deployments,
    "search_runbooks": search_runbooks_tool,
}


# Her aracın kabul ettiği parametreler
TOOL_ARGUMENTS = {
    "get_logs": {
        "service": str,
        "start_time": str,
        "end_time": str,
    },
    "get_service_status": {
        "service": str,
        "start_time": str,
        "end_time": str,
    },
    "get_deployments": {
        "service": str,
        "start_time": str,
        "end_time": str,
    },
    "search_runbooks": {
        "query": str,
        "top_k": int,
    },
}


def dispatch_tool(
    tool_name: str,
    arguments: dict[str, Any],
) -> ToolResult:
    """İzin verilen aracı doğrular ve çalıştırır."""

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

    # 3. Aracın beklediği parametreleri bul
    expected = TOOL_ARGUMENTS[tool_name]

    if set(arguments.keys()) != set(expected.keys()):
        return ToolResult(
            status="error",
            error=ToolError(
                code="INVALID_ARGUMENTS",
                message=f"Expected arguments: {list(expected.keys())}",
            ),
        )

    # 4. Parametre tiplerini kontrol et
    for name, expected_type in expected.items():
        value = arguments[name]

        # type() kullanıyoruz çünkü bool, Python'da
        # int sınıfının alt sınıfıdır.
        if type(value) is not expected_type:
            return ToolResult(
                status="error",
                error=ToolError(
                    code="INVALID_ARGUMENTS",
                    message=f"Invalid type for '{name}'",
                ),
            )

    # 5. İlgili Python fonksiyonunu çalıştır
    tool_function = TOOL_REGISTRY[tool_name]

    try:
        result = tool_function(**arguments)

    except Exception:
        return ToolResult(
            status="error",
            error=ToolError(
                code="TOOL_EXECUTION_ERROR",
                message="Tool execution failed",
            ),
        )

    # 6. Sonuç sözleşmesini kontrol et
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

    incident_args = {
        "service": "checkout-api",
        "start_time": "2026-10-20T09:00:00Z",
        "end_time": "2026-10-20T09:15:00Z",
    }

    print("--- EXISTING TOOL ---")

    result = dispatch_tool("get_logs", incident_args)

    print("Status:", result.status)
    if result.status == "success":
        print("Records:", result.data["count"])

    print("\n--- RUNBOOK TOOL ---")

    result = dispatch_tool(
        "search_runbooks",
        {
            "query": "HTTP 500 errors after deployment",
            "top_k": 3,
        },
    )

    print("Status:", result.status)

    if result.status == "success":
        print("Records:", result.data["count"])
        print("Embedding tokens:", result.data["embedding_tokens"])

        for item in result.data["results"]:
            print(item["title"], "|", item["source_id"])
    else:
        print("Error:", result.error.code)

    print("\n--- UNKNOWN TOOL ---")

    result = dispatch_tool(
        "restart_service",
        incident_args,
    )

    print("Status:", result.status)
    print("Error:", result.error.code)

    print("\n--- INVALID RUNBOOK ARGUMENTS ---")

    result = dispatch_tool(
        "search_runbooks",
        {
            "query": "HTTP 500",
            "top_k": "three",
        },
    )

    print("Status:", result.status)
    print("Error:", result.error.code)
