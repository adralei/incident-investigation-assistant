
from incident_assistant.evaluation.compare_reports import (
    load_report,
)
from incident_assistant.evaluation.claim_extractor import (
    extract_report_claims,
)


ARCHITECTURES = (
    "single_agent",
    "multi_agent",
)


def extract_saved_claims(architecture: str):
    """Kaydedilmiş rapordan doğrulanabilir iddiaları çıkarır."""

    report = load_report(architecture)
    return extract_report_claims(report)


def main():
    print("=== SAVED REPORT CLAIM EXTRACTION ===")

    for architecture in ARCHITECTURES:
        print(f"\n--- {architecture.upper()} ---")

        try:
            claims = extract_saved_claims(architecture)

        except FileNotFoundError:
            print("Report file not found.")
            continue

        except ValueError as exc:
            print(f"Invalid report: {exc}")
            continue

        print("Total claims:", len(claims))

        for claim in claims:
            print(f"\nClaim ID: {claim.claim_id}")
            print(f"Claim: {claim.claim}")
            print(f"Sources: {claim.source_ids}")
            print(f"Type: {claim.claim_type}")


if __name__ == "__main__":
    main()
