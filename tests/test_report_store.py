
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from incident_assistant.contracts.report_schema import IncidentReport
from incident_assistant.reports.report_store import save_report


class TestReportStore(unittest.TestCase):

    def setUp(self):
        self.report = IncidentReport.model_validate({
            "service": "checkout-api",
            "findings": [
                {
                    "description": "HTTP 500 görüldü.",
                    "source_ids": ["log-003"],
                }
            ],
            "hypotheses": [],
            "missing_information": [],
            "recommended_checks": [],
        })

    def test_single_agent_report_saved(self):
        with TemporaryDirectory() as directory:
            output = save_report(
                self.report,
                "single_agent",
                Path(directory),
            )

            self.assertTrue(output.exists())
            self.assertEqual(output.name, "single_agent.json")
            self.assertIn(
                "checkout-api",
                output.read_text(encoding="utf-8"),
            )

    def test_multi_agent_report_saved(self):
        with TemporaryDirectory() as directory:
            output = save_report(
                self.report,
                "multi_agent",
                Path(directory),
            )

            self.assertTrue(output.exists())
            self.assertEqual(output.name, "multi_agent.json")

    def test_unknown_architecture_rejected(self):
        with TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                save_report(
                    self.report,
                    "../invalid",
                    Path(directory),
                )


if __name__ == "__main__":
    unittest.main()
