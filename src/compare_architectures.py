
import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_FILE = (
    PROJECT_ROOT / "evals" / "benchmark_runs.json"
)


class BenchmarkRun(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    architecture: str = Field(min_length=1)
    scenario: str = Field(min_length=1)

    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    embedding_tokens: int = Field(ge=0)
    duration_seconds: float = Field(ge=0)

    schema_valid: bool
    references_valid: bool

    @property
    def total_model_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


def load_runs() -> list[BenchmarkRun]:
    with BENCHMARK_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    return [
        BenchmarkRun.model_validate(item)
        for item in data
    ]


def percentage_change(
    baseline: float,
    candidate: float,
) -> float | None:
    if baseline == 0:
        return None

    return ((candidate - baseline) / baseline) * 100


def compare_runs(
    single: BenchmarkRun,
    multi: BenchmarkRun,
) -> None:

    if single.scenario != multi.scenario:
        raise ValueError(
            "Cannot compare different incident scenarios"
        )

    print("=== ARCHITECTURE COMPARISON ===")
    print("Scenario:", single.scenario)

    measurements = [
        (
            "Model tokens",
            single.total_model_tokens,
            multi.total_model_tokens,
        ),
        (
            "Embedding tokens",
            single.embedding_tokens,
            multi.embedding_tokens,
        ),
        (
            "Duration (seconds)",
            single.duration_seconds,
            multi.duration_seconds,
        ),
    ]

    for name, single_value, multi_value in measurements:
        change = percentage_change(
            single_value,
            multi_value,
        )

        print(f"\n{name}")
        print("Single-Agent:", single_value)
        print("Multi-Agent:", multi_value)

        if change is None:
            print("Change: N/A")
        else:
            print(f"Change: {change:+.2f}%")

    print("\n=== VALIDATION RESULTS ===")

    for run in [single, multi]:
        print(
            f"{run.architecture}: "
            f"schema={run.schema_valid}, "
            f"references={run.references_valid}"
        )

    print("\n=== INTERPRETATION LIMIT ===")
    print("Historical single-run comparison only.")
    print("Semantic report accuracy was not measured.")
    print("No statistical performance conclusion.")


if __name__ == "__main__":
    runs = load_runs()

    single_runs = [
        run for run in runs
        if run.architecture == "single_agent"
    ]

    multi_runs = [
        run for run in runs
        if run.architecture == "multi_agent"
    ]

    if len(single_runs) != 1 or len(multi_runs) != 1:
        raise ValueError(
            "Expected one run per architecture"
        )

    compare_runs(
        single_runs[0],
        multi_runs[0],
    )
