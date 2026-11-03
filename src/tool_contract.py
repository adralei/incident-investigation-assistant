
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class IncidentQuery(BaseModel):
    """Araç sorgularında kullanılacak doğrulanmış girdi."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True
    )

    service: str = Field(min_length=1)
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def validate_query(self):
        if not self.service.strip():
            raise ValueError("Service cannot be blank")

        if (
            self.start_time.utcoffset() is None
            or self.end_time.utcoffset() is None
        ):
            raise ValueError("Timestamps must have timezone information")

        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")

        return self


class ToolError(BaseModel):
    code: str
    message: str


class ToolResult(BaseModel):
    """Tüm okuma araçlarımız için ortak sonuç sözleşmesi."""

    status: Literal["success", "error"]
    data: Any = None
    error: ToolError | None = None

    @model_validator(mode="after")
    def validate_result(self):
        if self.status == "success" and self.error is not None:
            raise ValueError("Successful result cannot contain an error")

        if self.status == "error" and self.error is None:
            raise ValueError("Error result must contain error details")

        if self.status == "error" and self.data is not None:
            raise ValueError("Error result cannot contain data")

        return self


if __name__ == "__main__":

    print("--- VALID QUERY ---")

    valid_query = IncidentQuery(
        service="checkout-api",
        start_time=datetime.fromisoformat("2026-10-20T09:00:00+00:00"),
        end_time=datetime.fromisoformat("2026-10-20T09:15:00+00:00"),
    )

    print("Validated service:", valid_query.service)

    print("\n--- SUCCESS RESULT ---")

    success = ToolResult(
        status="success",
        data={"records": [], "count": 0}
    )

    print(success.model_dump())

    print("\n--- ERROR RESULT ---")

    failure = ToolResult(
        status="error",
        error=ToolError(
            code="FILE_READ_ERROR",
            message="Unable to read log file"
        )
    )

    print(failure.model_dump())

    print("\n--- INVALID QUERY ---")

    try:
        IncidentQuery(
            service="checkout-api",
            start_time=datetime.fromisoformat("2026-10-20T10:00:00+00:00"),
            end_time=datetime.fromisoformat("2026-10-20T09:00:00+00:00"),
        )
    except ValueError:
        print("Invalid time range rejected")
