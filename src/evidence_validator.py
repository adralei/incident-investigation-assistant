
from report_schema import IncidentReport


OPERATIONAL_TOOLS = {
    "get_logs": "log_id",
    "get_service_status": "snapshot_id",
    "get_deployments": "deployment_id",
}


def register_evidence(
    registry: dict[str, str],
    tool_name: str,
    data: dict,
) -> None:
    """Başarılı araç sonuçlarının kaynaklarını kaydeder."""

    if tool_name in OPERATIONAL_TOOLS:
        id_field = OPERATIONAL_TOOLS[tool_name]

        for record in data.get("records", []):
            source_id = record.get(id_field)

            if isinstance(source_id, str) and source_id:
                registry[source_id] = "operational"

    elif tool_name == "search_runbooks":
        for item in data.get("results", []):
            source_id = item.get("source_id")

            if isinstance(source_id, str) and source_id:
                registry[source_id] = "runbook"


def validate_evidence(
    report: IncidentReport,
    registry: dict[str, str],
) -> list[str]:
    """Rapor kaynaklarının varlığını ve türünü kontrol eder."""

    errors = []

    def check_source(
        source_id: str,
        expected_type: str,
        location: str,
    ):
        actual_type = registry.get(source_id)

        if actual_type is None:
            errors.append(
                f"{location}: Unknown source '{source_id}'"
            )

        elif actual_type != expected_type:
            errors.append(
                f"{location}: Source '{source_id}' "
                f"must be {expected_type}, got {actual_type}"
            )

    # Bulgular operasyonel kaynaklara dayanmalı.
    for index, finding in enumerate(report.findings):
        for source_id in finding.source_ids:
            check_source(
                source_id,
                "operational",
                f"findings[{index}]",
            )

    # Hipotezlerin destekleyici kaynakları da
    # operasyonel kayıtlar olmalı.
    for index, hypothesis in enumerate(report.hypotheses):
        for source_id in hypothesis.supporting_source_ids:
            check_source(
                source_id,
                "operational",
                f"hypotheses[{index}]",
            )

    # Önerilerin runbook referansları
    # yalnızca runbook kaynakları olmalı.
    for index, recommendation in enumerate(
        report.recommended_checks
    ):
        for source_id in recommendation.runbook_source_ids:
            check_source(
                source_id,
                "runbook",
                f"recommended_checks[{index}]",
            )

    return errors


if __name__ == "__main__":

    # Küçük, bağımsız bir test senaryosu.
    registry = {
        "log-003": "operational",
        "dep-001": "operational",
        "http-500.md:L10-L17": "runbook",
    }

    valid_data = {
        "service": "checkout-api",
        "findings": [
            {
                "description": "HTTP 500 hatası görüldü.",
                "source_ids": ["log-003"],
            }
        ],
        "hypotheses": [
            {
                "description": "Deployment ilişkili olabilir.",
                "supporting_source_ids": ["dep-001"],
                "uncertainty": "Nedensellik kanıtlanmadı.",
            }
        ],
        "missing_information": [
            "Exception ayrıntıları"
        ],
        "recommended_checks": [
            {
                "action": "Deployment değişikliklerini incele.",
                "reason": "Zaman ilişkisini araştırmak için.",
                "runbook_source_ids": [
                    "http-500.md:L10-L17"
                ],
            }
        ],
    }

    print("--- VALID EVIDENCE ---")

    report = IncidentReport.model_validate(valid_data)
    errors = validate_evidence(report, registry)

    print("Errors:", errors)
    print("Validation:", "PASS" if not errors else "FAIL")

    print("\n--- UNKNOWN SOURCE ---")

    invalid_data = report.model_dump()
    invalid_data["findings"][0]["source_ids"] = ["log-999"]

    invalid_report = IncidentReport.model_validate(invalid_data)

    errors = validate_evidence(invalid_report, registry)

    print("Errors:", errors)
    print("Validation:", "PASS" if not errors else "FAIL")

    print("\n--- WRONG SOURCE TYPE ---")

    wrong_type_data = report.model_dump()
    wrong_type_data["findings"][0]["source_ids"] = [
        "http-500.md:L10-L17"
    ]

    wrong_type_report = IncidentReport.model_validate(
        wrong_type_data
    )

    errors = validate_evidence(wrong_type_report, registry)

    print("Errors:", errors)
    print("Validation:", "PASS" if not errors else "FAIL")
