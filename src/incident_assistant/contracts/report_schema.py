
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
)


class StrictModel(BaseModel):
    """Tanımlanmayan alanları reddeden temel model."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )


class Finding(StrictModel):
    """Kaynaklı operasyonel gözlem."""

    description: str = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)


class Hypothesis(StrictModel):
    """Henüz kanıtlanmamış olası açıklama."""

    description: str = Field(min_length=1)
    supporting_source_ids: list[str]
    uncertainty: str = Field(min_length=1)


class RecommendedCheck(StrictModel):
    """Salt okunur sonraki inceleme önerisi."""

    action: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    runbook_source_ids: list[str]


class IncidentReport(StrictModel):
    """Agent inceleme raporunun ortak sözleşmesi."""

    service: str = Field(min_length=1)

    findings: list[Finding] = Field(min_length=1)

    hypotheses: list[Hypothesis]

    missing_information: list[str]

    recommended_checks: list[RecommendedCheck]


if __name__ == "__main__":

    print("--- VALID REPORT ---")

    report = IncidentReport(
        service="checkout-api",
        findings=[
            Finding(
                description="09:07 UTC'de HTTP 500 görüldü.",
                source_ids=["log-003"],
            ),
            Finding(
                description="09:05 UTC'de deployment gerçekleşti.",
                source_ids=["dep-001"],
            ),
        ],
        hypotheses=[
            Hypothesis(
                description="Deployment ile ilişkili hata olabilir.",
                supporting_source_ids=[
                    "dep-001",
                    "log-003",
                ],
                uncertainty=(
                    "Zamansal ilişki nedensellik kanıtı değildir."
                ),
            ),
        ],
        missing_information=[
            "Uygulama exception ayrıntıları",
            "Deployment değişiklik kapsamı",
        ],
        recommended_checks=[
            RecommendedCheck(
                action="Deployment değişikliklerini incele.",
                reason="Hatalar deployment sonrasında kaydedildi.",
                runbook_source_ids=[
                    "http-500.md:L10-L17",
                ],
            ),
        ],
    )

    print("Service:", report.service)
    print("Findings:", len(report.findings))
    print("Hypotheses:", len(report.hypotheses))
    print("Missing information:", len(report.missing_information))
    print("Recommended checks:", len(report.recommended_checks))

    print("\n--- INVALID REPORT ---")

    invalid_data = report.model_dump()

    # İlk bulgunun kaynaklarını kaldırıyoruz.
    invalid_data["findings"][0]["source_ids"] = []

    try:
        IncidentReport.model_validate(invalid_data)
    except ValidationError as exc:
        print("Report rejected")
        print("Validation errors:", exc.error_count())
        print("Error location:", exc.errors()[0]["loc"])

    print("\n--- VALID JSON OUTPUT ---")
    print(report.model_dump_json(indent=2))
