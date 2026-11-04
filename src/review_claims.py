
import json
from pathlib import Path

from evidence_support import collect_evidence_records


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CASES_FILE = PROJECT_ROOT / "evals" / "claim_cases.json"


def load_cases() -> list[dict]:
    """Referans değerlendirme senaryolarını okur."""

    with CASES_FILE.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    if not isinstance(cases, list):
        raise ValueError("Evaluation cases must be a list")

    required = {
        "case_id",
        "claim",
        "source_ids",
        "expected_label",
        "reason",
    }

    allowed_labels = {
        "supported",
        "contradicted",
        "insufficient_evidence",
    }

    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("Invalid evaluation case")

        if set(case) != required:
            raise ValueError("Invalid evaluation case fields")

        if case["expected_label"] not in allowed_labels:
            raise ValueError("Invalid expected label")

        if (
            not isinstance(case["source_ids"], list)
            or not case["source_ids"]
            or not all(
                isinstance(item, str) and item
                for item in case["source_ids"]
            )
        ):
            raise ValueError("Invalid source IDs")

    return cases


def review_cases() -> None:
    """İddiaları ve gerçek kaynak kayıtlarını yan yana gösterir."""

    cases = load_cases()
    sources = collect_evidence_records()

    print("Evaluation cases:", len(cases))
    print("Available evidence records:", len(sources))

    for case in cases:
        print("\n" + "=" * 55)

        print("Case:", case["case_id"])
        print("Claim:", case["claim"])

        print("\nEVIDENCE:")

        for source_id in case["source_ids"]:
            record = sources.get(source_id)

            if record is None:
                print(source_id, "NOT FOUND")
            else:
                print(
                    source_id,
                    json.dumps(record, ensure_ascii=False),
                )

        print("\nREFERENCE EVALUATION:")
        print("Expected:", case["expected_label"])
        print("Reason:", case["reason"])

        print("Automatic semantic verification: NOT IMPLEMENTED")

    print("\n" + "=" * 55)
    print("Review packets generated:", len(cases))
    print("Automatic claim accuracy: NOT MEASURED")


if __name__ == "__main__":
    review_cases()
