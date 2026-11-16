
from pydantic import BaseModel, ConfigDict, Field

from incident_assistant.contracts.report_schema import IncidentReport


class ExtractedClaim(BaseModel):
    """Agent raporundan çıkarılan değerlendirilebilir iddia."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    claim_id: str = Field(min_length=1)
    claim: str = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)
    claim_type: str = Field(min_length=1)


def extract_report_claims(
    report: IncidentReport,
) -> list[ExtractedClaim]:
    """Raporun findings bölümündeki iddiaları çıkarır."""

    claims = []

    for index, finding in enumerate(report.findings, start=1):
        claim = ExtractedClaim(
            claim_id=f"finding-{index:03d}",
            claim=finding.description,
            source_ids=list(finding.source_ids),
            claim_type="finding",
        )

        claims.append(claim)

    return claims
