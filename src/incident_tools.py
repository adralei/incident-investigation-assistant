
import json

from pydantic import ValidationError

from inspect_context import (
    read_records,
    DEPLOYMENT_FILE,
)
from inspect_logs import read_logs

from tool_contract import (
    IncidentQuery,
    ToolResult,
    ToolError,
)


def validate_query(
    service: str,
    start_time: str,
    end_time: str,
) -> IncidentQuery:
    """Gelen araç girdilerini doğrular."""

    payload = json.dumps({
        "service": service,
        "start_time": start_time,
        "end_time": end_time,
    })

    return IncidentQuery.model_validate_json(payload)


def get_logs(
    service: str,
    start_time: str,
    end_time: str,
) -> ToolResult:
    """İstenen servis ve zaman aralığındaki logları getirir."""

    try:
        query = validate_query(service, start_time, end_time)

    except (ValidationError, TypeError, ValueError) as exc:
        return ToolResult(
            status="error",
            error=ToolError(
                code="INVALID_INPUT",
                message=str(exc),
            ),
        )

    try:
        records = read_logs(
            service=query.service,
            start_time=query.start_time.isoformat(),
            end_time=query.end_time.isoformat(),
        )

    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        return ToolResult(
            status="error",
            error=ToolError(
                code="DATA_READ_ERROR",
                message=str(exc),
            ),
        )

    return ToolResult(
        status="success",
        data={
            "service": query.service,
            "records": records,
            "count": len(records),
        },
    )


def get_deployments(
    service: str,
    start_time: str,
    end_time: str,
) -> ToolResult:
    """İstenen servis ve zaman aralığındaki deployment'ları getirir."""

    try:
        query = validate_query(service, start_time, end_time)

    except (ValidationError, TypeError, ValueError) as exc:
        return ToolResult(
            status="error",
            error=ToolError(
                code="INVALID_INPUT",
                message=str(exc),
            ),
        )

    try:
        records = read_records(
            DEPLOYMENT_FILE,
            query.service,
            query.start_time.isoformat(),
            query.end_time.isoformat(),
        )

    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        return ToolResult(
            status="error",
            error=ToolError(
                code="DATA_READ_ERROR",
                message=str(exc),
            ),
        )

    return ToolResult(
        status="success",
        data={
            "service": query.service,
            "records": records,
            "count": len(records),
        },
    )


if __name__ == "__main__":

    service = "checkout-api"
    start_time = "2026-10-20T09:00:00Z"
    end_time = "2026-10-20T09:15:00Z"

    print("--- LOG TOOL ---")

    logs_result = get_logs(
        service, start_time, end_time
    )

    print("Status:", logs_result.status)

    if logs_result.status == "success":
        print("Count:", logs_result.data["count"])

        for record in logs_result.data["records"]:
            print(
                record["log_id"],
                record["status_code"],
                record["message"],
            )

    print("\n--- DEPLOYMENT TOOL ---")

    deployments_result = get_deployments(
        service, start_time, end_time
    )

    print("Status:", deployments_result.status)

    if deployments_result.status == "success":
        print("Count:", deployments_result.data["count"])

        for record in deployments_result.data["records"]:
            print(
                record["deployment_id"],
                record["version"],
                record["status"],
            )

    print("\n--- INVALID INPUT TEST ---")

    invalid_result = get_logs(
        service="checkout-api",
        start_time="invalid-date",
        end_time=end_time,
    )

    print("Status:", invalid_result.status)

    if invalid_result.error:
        print("Error code:", invalid_result.error.code)
        print("Has message:", bool(invalid_result.error.message))
