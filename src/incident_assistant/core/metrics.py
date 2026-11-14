
from pydantic import BaseModel, ConfigDict, Field


class AgentMetrics(BaseModel):
    """Bir agent'ın ölçülen kaynak kullanımı."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    embedding_tokens: int = Field(ge=0)
    duration_seconds: float = Field(ge=0)


class CombinedMetrics(BaseModel):
    """Multi-agent çalıştırmasının birleştirilmiş ölçümleri."""

    model_config = ConfigDict(extra="forbid")

    input_tokens: int
    output_tokens: int
    embedding_tokens: int
    total_model_tokens: int
    wall_time_seconds: float


def aggregate_metrics(
    main: AgentMetrics,
    specialist: AgentMetrics,
) -> CombinedMetrics:
    """Ana agent ve uzmanın token ölçümlerini birleştirir.

    Main duration, specialist süresini zaten içerir.
    Bu nedenle süreler toplanmaz.
    """

    input_total = main.input_tokens + specialist.input_tokens
    output_total = main.output_tokens + specialist.output_tokens

    return CombinedMetrics(
        input_tokens=input_total,
        output_tokens=output_total,
        embedding_tokens=(
            main.embedding_tokens + specialist.embedding_tokens
        ),
        total_model_tokens=input_total + output_total,
        wall_time_seconds=main.duration_seconds,
    )


if __name__ == "__main__":
    # Önceki gerçek konsol çıktımızdan alınan örnek değerler.
    # Bu bölüm canlı agent çalıştırmaz.
    main = AgentMetrics(
        input_tokens=9699,
        output_tokens=2701,
        embedding_tokens=0,
        duration_seconds=51.52,
    )

    specialist = AgentMetrics(
        input_tokens=2213,
        output_tokens=832,
        embedding_tokens=378,
        duration_seconds=12.11,
    )

    combined = aggregate_metrics(main, specialist)

    print("=== COMBINED METRICS ===")
    print(combined.model_dump_json(indent=2))
    print("Specialist duration:", specialist.duration_seconds)
    print("End-to-end duration:", combined.wall_time_seconds)
