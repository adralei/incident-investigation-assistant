
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from incident_assistant.retrieval.hybrid_search import hybrid_search
from incident_assistant.contracts.tool_contract import ToolResult, ToolError


class RunbookQuery(BaseModel):
    """Runbook araması için girdi modeli."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    query: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=5)


def search_runbooks_tool(
    query: str,
    top_k: int = 3,
) -> ToolResult:
    """Kaynaklı runbook araması gerçekleştirir."""

    # 1. Girdi doğrulama
    try:
        validated = RunbookQuery(
            query=query,
            top_k=top_k,
        )

        if not validated.query.strip():
            raise ValueError("Query cannot be blank")

    except (ValidationError, ValueError) as exc:
        return ToolResult(
            status="error",
            error=ToolError(
                code="INVALID_INPUT",
                message=str(exc),
            ),
        )

    # 2. Arama işlemi
    try:
        search_output = hybrid_search(
            query=validated.query,
            top_k=validated.top_k,
        )

    except Exception:
        # API veya belge okuma hatalarını
        # boş arama sonucuyla karıştırmıyoruz.
        return ToolResult(
            status="error",
            error=ToolError(
                code="RETRIEVAL_ERROR",
                message="Runbook search could not be completed",
            ),
        )

    # 3. Başarılı sonuç
    return ToolResult(
        status="success",
        data={
            "query": validated.query,
            "results": search_output["results"],
            "count": len(search_output["results"]),
            "embedding_tokens": search_output["embedding_tokens"],
        },
    )


if __name__ == "__main__":

    print("--- VALID RUNBOOK SEARCH ---")

    result = search_runbooks_tool(
        query="HTTP 500 errors after deployment",
        top_k=3,
    )

    print("Status:", result.status)

    if result.status == "success":
        print("Count:", result.data["count"])
        print(
            "Embedding tokens:",
            result.data["embedding_tokens"],
        )

        for item in result.data["results"]:
            print(
                item["source_id"],
                "|", item["title"],
            )
    else:
        print("Error:", result.error.code)

    print("\n--- INVALID QUERY ---")

    result = search_runbooks_tool(
        query="   ",
        top_k=3,
    )

    print("Status:", result.status)
    print("Error:", result.error.code)

    print("\n--- INVALID TOP_K ---")

    result = search_runbooks_tool(
        query="HTTP 500",
        top_k=0,
    )

    print("Status:", result.status)
    print("Error:", result.error.code)
