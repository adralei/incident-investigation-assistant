
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from incident_assistant.contracts.report_schema import (
    IncidentReport,
)
from incident_assistant.reports.report_store import save_report
from incident_assistant.evaluation.extract_saved_claims import (
    extract_saved_claims,
)


class TestExtractSavedClaims(unittest.TestCase):

    def make_report(self):
        return IncidentReport.model_validate({
            "service": "checkout-api",
            "findings": [
                {
                    "description": "HTTP 500 observed",
                    "source_ids": ["log-003"],
                },
                {
                    "description": "Deployment completed",
                    "source_ids": ["dep-001"],
                },
            ],
            "hypotheses": [],
            "missing_information": [],
            "recommended_checks": [],
        })

    def test_saved_report_extraction(self):
        with TemporaryDirectory() as directory:
            output_dir = Path(directory)

            save_report(
                self.make_report(),
                "single_agent",
                output_dir,
            )

            with patch(
                "incident_assistant.evaluation.compare_reports.RESULTS_DIR",
                output_dir,
            ):
                claims = extract_saved_claims("single_agent")

            self.assertEqual(len(claims), 2)
            self.assertEqual(
                claims[0].source_ids,
                ["log-003"],
            )

    def test_missing_report_raises_error(self):
        with TemporaryDirectory() as directory:
            with patch(
                "incident_assistant.evaluation.compare_reports.RESULTS_DIR",
                Path(directory),
            ):
                with self.assertRaises(FileNotFoundError):
                    extract_saved_claims("multi_agent")

    def test_unknown_architecture_rejected(self):
        with self.assertRaises(ValueError):
            extract_saved_claims("../invalid")


if __name__ == "__main__":
    unittest.main()
