
from pathlib import Path

from incident_assistant.contracts.report_schema import IncidentReport


from incident_assistant.core.paths import PROJECT_ROOT
RESULTS_DIR = PROJECT_ROOT / "evals" / "results"


# Her gözlem grubunun bulunması gereken kaynakları.
# Birden fazla ID varsa hepsini bulgularda arıyoruz.
FINDING_REQUIREMENTS = {
    "initial_health": {"svc-001"},
    "successful_request": {"log-002"},
    "deployment": {"dep-001"},
    "http_500_errors": {"log-003", "log-004"},
    "degraded_health": {"svc-002"},
}


# Bir runbook konusu için aşağıdaki referanslardan
# en az birinin önerilerde bulunması yeterlidir.
RUNBOOK_REQUIREMENTS = {
    "http_500_initial": {
        "http-500.md:L4-L9",
    },
    "deployment_correlation": {
        "http-500.md:L10-L17",
    },
    "readiness_checks": {
        "kubernetes-readiness.md:L4-L10",
        "kubernetes-readiness.md:L11-L18",
    },
    "dependency_checks": {
        "http-500.md:L18-L25",
    },
}


def evaluate_report(report: IncidentReport) -> dict:
    """Raporun kaynak referansı kapsamını değerlendirir."""

    # Yalnızca findings içindeki operasyonel kaynaklar.
    finding_sources = {
        source_id
        for finding in report.findings
        for source_id in finding.source_ids
    }

    # Yalnızca önerilerdeki runbook kaynakları.
    recommendation_sources = {
        source_id
        for recommendation in report.recommended_checks
        for source_id in recommendation.runbook_source_ids
    }

    covered_findings = [
        name
        for name, required_ids in FINDING_REQUIREMENTS.items()
        if required_ids.issubset(finding_sources)
    ]

    missing_findings = [
        name
        for name in FINDING_REQUIREMENTS
        if name not in covered_findings
    ]

    covered_topics = [
        name
        for name, accepted_ids in RUNBOOK_REQUIREMENTS.items()
        if accepted_ids.intersection(recommendation_sources)
    ]

    missing_topics = [
        name
        for name in RUNBOOK_REQUIREMENTS
        if name not in covered_topics
    ]

    return {
        "findings": {
            "covered": covered_findings,
            "missing": missing_findings,
            "total": len(FINDING_REQUIREMENTS),
        },
        "runbook_topics": {
            "covered": covered_topics,
            "missing": missing_topics,
            "total": len(RUNBOOK_REQUIREMENTS),
        },
    }


def load_report(architecture: str) -> IncidentReport:
    """Kaydedilmiş raporu Pydantic ile tekrar okur."""

    if architecture not in {
        "single_agent",
        "multi_agent",
    }:
        raise ValueError("Unknown architecture")

    path = RESULTS_DIR / f"{architecture}.json"

    return IncidentReport.model_validate_json(
        path.read_text(encoding="utf-8")
    )


def print_evaluation(architecture: str) -> None:
    report = load_report(architecture)
    result = evaluate_report(report)

    print(f"\n=== {architecture.upper()} ===")
    print("Service:", report.service)

    findings = result["findings"]
    topics = result["runbook_topics"]

    print(
        "Finding reference coverage:",
        f"{len(findings['covered'])}/{findings['total']}",
    )

    print(
        "Missing finding groups:",
        findings["missing"],
    )

    print(
        "Runbook topic reference coverage:",
        f"{len(topics['covered'])}/{topics['total']}",
    )

    print(
        "Missing runbook topics:",
        topics["missing"],
    )

    print("Findings count:", len(report.findings))
    print("Hypotheses count:", len(report.hypotheses))
    print(
        "Recommendations count:",
        len(report.recommended_checks),
    )


if __name__ == "__main__":
    print("=== REPORT COVERAGE COMPARISON ===")

    print_evaluation("single_agent")
    print_evaluation("multi_agent")

    print("\n=== EVALUATION LIMITS ===")
    print("This measures citation coverage only.")
    print("It does not prove semantic claim correctness.")
    print("No overall report quality score is assigned.")
