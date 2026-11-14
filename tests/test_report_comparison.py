
import unittest
from pathlib import Path

from incident_assistant.contracts.report_schema import IncidentReport
from incident_assistant.evaluation.compare_reports import evaluate_report


def make_report(
    finding_ids: list[str],
    runbook_ids: list[str],
    hypothesis_ids: list[str] | None = None,
) -> IncidentReport:

    return IncidentReport.model_validate({
        "service": "checkout-api",
        "findings": [
            {
                "description": "Test observation",
                "source_ids": finding_ids,
            }
        ],
        "hypotheses": [
            {
                "description": "Test hypothesis",
                "supporting_source_ids": (
                    hypothesis_ids or []
                ),
                "uncertainty": "Cause is not proven",
            }
        ],
        "missing_information": [],
        "recommended_checks": [
            {
                "action": "Investigate",
                "reason": "Runbook guidance",
                "runbook_source_ids": runbook_ids,
            }
        ],
    })


class TestReportComparison(unittest.TestCase):

    def test_complete_reference_coverage(self):
        report = make_report(
            finding_ids=[
                "svc-001",
                "log-002",
                "dep-001",
                "log-003",
                "log-004",
                "svc-002",
            ],
            runbook_ids=[
                "http-500.md:L4-L9",
                "http-500.md:L10-L17",
                "kubernetes-readiness.md:L4-L10",
                "http-500.md:L18-L25",
            ],
        )

        result = evaluate_report(report)

        self.assertEqual(
            len(result["findings"]["covered"]),
            5,
        )

        self.assertEqual(
            len(result["runbook_topics"]["covered"]),
            4,
        )

    def test_hypothesis_sources_do_not_count_as_findings(self):
        report = make_report(
            finding_ids=["svc-001"],
            runbook_ids=[],
            hypothesis_ids=[
                "log-002",
                "dep-001",
                "log-003",
                "log-004",
                "svc-002",
            ],
        )

        result = evaluate_report(report)

        self.assertEqual(
            result["findings"]["covered"],
            ["initial_health"],
        )

        self.assertEqual(
            len(result["findings"]["missing"]),
            4,
        )

    def test_missing_runbook_topics(self):
        report = make_report(
            finding_ids=["log-003"],
            runbook_ids=["http-500.md:L4-L9"],
        )

        result = evaluate_report(report)

        self.assertEqual(
            result["runbook_topics"]["covered"],
            ["http_500_initial"],
        )

        self.assertIn(
            "dependency_checks",
            result["runbook_topics"]["missing"],
        )


if __name__ == "__main__":
    unittest.main()
