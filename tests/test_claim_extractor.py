
import unittest

from incident_assistant.contracts.report_schema import IncidentReport
from incident_assistant.evaluation.claim_extractor import (
    extract_report_claims,
)


class TestClaimExtractor(unittest.TestCase):

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
            "hypotheses": [
                {
                    "description": "Deployment may have caused errors",
                    "supporting_source_ids": [
                        "dep-001",
                        "log-003",
                    ],
                    "uncertainty": "Causality is not established",
                },
            ],
            "missing_information": [],
            "recommended_checks": [],
        })

    def test_extract_findings(self):
        report = self.make_report()

        claims = extract_report_claims(report)

        self.assertEqual(len(claims), 2)
        self.assertEqual(claims[0].claim_id, "finding-001")
        self.assertEqual(claims[1].claim_id, "finding-002")

    def test_sources_preserved(self):
        report = self.make_report()

        claims = extract_report_claims(report)

        self.assertEqual(
            claims[0].source_ids,
            ["log-003"],
        )
        self.assertEqual(
            claims[1].source_ids,
            ["dep-001"],
        )

    def test_hypotheses_not_extracted(self):
        report = self.make_report()

        claims = extract_report_claims(report)

        self.assertTrue(
            all(claim.claim_type == "finding" for claim in claims)
        )

        self.assertFalse(
            any(
                "may have caused" in claim.claim
                for claim in claims
            )
        )


if __name__ == "__main__":
    unittest.main()
