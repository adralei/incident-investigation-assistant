from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
)


class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )


class DelegationRequest(StrictModel):
    """Ana agent'ın uzmana gönderdiği görev."""

    task_id: str = Field(min_length=1)
    service: str = Field(min_length=1)
    question: str = Field(min_length=1)
    observed_facts: list[str] = Field(min_length=1)


class SpecialistRecommendation(StrictModel):
    """Runbook kaynaklı inceleme önerisi."""

    action: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)


class SpecialistResult(StrictModel):
    """Uzman agent'ın ana agent'a döndürdüğü sonuç."""

    task_id: str = Field(min_length=1)
    status: Literal[
        "completed",
        "insufficient_information",
        "error",
    ]
    summary: str = Field(min_length=1)
    recommendations: list[SpecialistRecommendation]
    limitations: list[str]


if __name__ == "__main__":

    print("--- DELEGATION REQUEST ---")

    request = DelegationRequest(
        task_id="task-001",
        service="checkout-api",
        question=(
            "Deployment sonrası HTTP 500 hataları ve "
            "readiness azalması için hangi kontroller öneriliyor?"
        ),
        observed_facts=[
            "09:07 ve 09:08 UTC'de HTTP 500 görüldü.",
            "09:05 UTC'de deployment gerçekleşti.",
            "09:12 UTC'de ready replicas 2/3 oldu.",
        ],
    )

    print(request.model_dump_json(indent=2))

    print("\n--- SPECIALIST RESULT ---")

    result = SpecialistResult(
        task_id=request.task_id,
        status="completed",
        summary=(
            "Runbook belgeleri deployment ve "
            "readiness kontrollerini öneriyor."
        ),
        recommendations=[
            SpecialistRecommendation(
                action="Deployment değişikliklerini incele.",
                reason="Hatalarla zaman ilişkisini araştırmak için.",
                source_ids=[
                    "http-500.md:L10-L17",
                ],
            ),
            SpecialistRecommendation(
                action="Pod readiness durumunu incele.",
                reason="Hazır replica sayısındaki düşüşü araştırmak için.",
                source_ids=[
                    "kubernetes-readiness.md:L4-L10",
                ],
            ),
        ],
        limitations=[
            "Runbook kök nedeni kanıtlamaz.",
            "Uzman operasyonel araçları çağırmadı.",
        ],
    )

    print(result.model_dump_json(indent=2))

    print("\n--- INVALID RECOMMENDATION ---")

    invalid_data = result.model_dump()

    invalid_data["recommendations"][0]["source_ids"] = []

    try:
        SpecialistResult.model_validate(invalid_data)
    except ValidationError as exc:
        print("Invalid specialist result rejected")
        print("Validation errors:", exc.error_count())
        print("Error location:", exc.errors()[0]["loc"])