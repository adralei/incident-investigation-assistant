
from typing import Literal

from pydantic import BaseModel, ConfigDict

from incident_assistant.tools.incident_tools import get_logs, get_deployments
from incident_assistant.tools.service_tools import get_service_status


START = "2026-10-20T09:00:00Z"
END = "2026-10-20T09:15:00Z"


class EvidenceClaim(BaseModel):
    """Tek bir kaynağa dayanan doğrulanabilir olgusal iddia."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    source_id: str
    field: str
    expected_value: str | int


def collect_evidence_records() -> dict[str, dict]:
    """Araç sonuçlarından kaynak içeriği indeksi oluşturur."""

    sources = {}

    tools = [
        (get_logs, "log_id"),
        (get_service_status, "snapshot_id"),
        (get_deployments, "deployment_id"),
    ]

    for tool, id_field in tools:
        result = tool("checkout-api", START, END)

        if result.status != "success":
            raise RuntimeError(
                f"Could not collect evidence: {tool.__name__}"
            )

        for record in result.data["records"]:
            sources[record[id_field]] = record

    return sources


def verify_claim(
    claim: EvidenceClaim,
    sources: dict[str, dict],
) -> dict:
    """Bir kaydın belirli bir olgusal iddiayı destekleyip
    desteklemediğini karşılaştırır.
    """

    record = sources.get(claim.source_id)

    if record is None:
        return {
            "status": "unknown_source",
            "reason": "Source was not collected",
        }

    if claim.field not in record:
        return {
            "status": "insufficient_evidence",
            "reason": f"Source has no '{claim.field}' field",
        }

    actual = record[claim.field]

    if type(actual) is not type(claim.expected_value):
        return {
            "status": "contradicted",
            "reason": "Field types do not match",
        }

    if actual == claim.expected_value:
        return {
            "status": "supported",
            "reason": "Source field matches expected value",
        }

    return {
        "status": "contradicted",
        "reason": (
            f"Expected {claim.expected_value!r}, "
            f"found {actual!r}"
        ),
    }


if __name__ == "__main__":

    sources = collect_evidence_records()

    print("Collected records:", len(sources))

    scenarios = [
        (
            "SUPPORTED CLAIM",
            EvidenceClaim(
                source_id="log-003",
                field="status_code",
                expected_value=500,
            ),
        ),
        (
            "CONTRADICTED CLAIM",
            EvidenceClaim(
                source_id="log-003",
                field="status_code",
                expected_value=503,
            ),
        ),
        (
            "INSUFFICIENT EVIDENCE",
            EvidenceClaim(
                source_id="log-003",
                field="database_status",
                expected_value="crashed",
            ),
        ),
        (
            "UNKNOWN SOURCE",
            EvidenceClaim(
                source_id="log-999",
                field="status_code",
                expected_value=500,
            ),
        ),
    ]

    for name, claim in scenarios:
        print(f"\n--- {name} ---")

        result = verify_claim(claim, sources)

        print("Source:", claim.source_id)
        print("Status:", result["status"])
        print("Reason:", result["reason"])
