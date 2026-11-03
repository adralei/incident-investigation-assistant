
from datetime import datetime
from pydantic import ValidationError

from inspect_context import read_records, STATUS_FILE
from tool_contract import IncidentQuery, ToolResult, ToolError


def get_service_status(
    service: str,
    start_time: str,
    end_time: str,
) -> ToolResult:
    """Servisin zaman aralığındaki durum kayıtlarını döndürür."""

    # 1. Girdi doğrulama
    try:
        query = IncidentQuery.model_validate_json(
            __import__("json").dumps({
                "service": service,
                "start_time": start_time,
                "end_time": end_time,
            })
        )
    except (ValidationError, TypeError, ValueError) as exc:
        return ToolResult(
            status="error",
            error=ToolError(
                code="INVALID_INPUT",
                message=str(exc)
            )
        )

    # 2. Veri okuma
    try:
        records = read_records(
            STATUS_FILE,
            query.service,
            query.start_time.isoformat(),
            query.end_time.isoformat(),
        )

    except (OSError, ValueError, KeyError) as exc:
        return ToolResult(
            status="error",
            error=ToolError(
                code="FILE_READ_ERROR",
                message=str(exc)
            )
        )

    # 3. Başarılı sonuç
    return ToolResult(
        status="success",
        data={
            "service": query.service,
            "records": records,
            "count": len(records),
        }
    )


if __name__ == "__main__":

    print("--- VALID REQUEST ---")

    result = get_service_status(
        service="checkout-api",
        start_time="2026-10-20T09:00:00Z",
        end_time="2026-10-20T09:15:00Z",
    )

    print(result.model_dump())

    print("\n--- NO DATA ---")

    result = get_service_status(
        service="checkout-api",
        start_time="2026-10-20T11:00:00Z",
        end_time="2026-10-20T11:15:00Z",
    )

    print(result.model_dump())

    print("\n--- INVALID TIME RANGE ---")

    result = get_service_status(
        service="checkout-api",
        start_time="2026-10-20T10:00:00Z",
        end_time="2026-10-20T09:00:00Z",
    )

    print(result.status)
    print(result.error.code if result.error else None)

    print("\n--- INVALID TIMESTAMP ---")

    result = get_service_status(
        service="checkout-api",
        start_time="not-a-date",
        end_time="2026-10-20T09:15:00Z",
    )

    print(result.status)
    print(result.error.code if result.error else None)
