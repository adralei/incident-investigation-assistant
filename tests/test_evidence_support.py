
import unittest

from pathlib import Path
from unittest.mock import patch

from incident_assistant.evidence.evidence_support import (
    EvidenceClaim,
    collect_evidence_records,
    verify_claim,
)
from incident_assistant.contracts.tool_contract import ToolResult, ToolError


class TestEvidenceSupport(unittest.TestCase):

    def setUp(self):
        """Her test için aynı başlangıç kanıtlarını hazırlar."""

        self.sources = {
            "log-003": {
                "log_id": "log-003",
                "service": "checkout-api",
                "status_code": 500,
                "message": "GET /orders failed",
            },
            "dep-001": {
                "deployment_id": "dep-001",
                "service": "checkout-api",
                "version": "v1.5.1",
                "status": "succeeded",
            },
        }

    def test_supported_claim(self):
        claim = EvidenceClaim(
            source_id="log-003",
            field="status_code",
            expected_value=500,
        )

        result = verify_claim(claim, self.sources)

        self.assertEqual(result["status"], "supported")

    def test_contradicted_claim(self):
        claim = EvidenceClaim(
            source_id="log-003",
            field="status_code",
            expected_value=503,
        )

        result = verify_claim(claim, self.sources)

        self.assertEqual(result["status"], "contradicted")
        self.assertIn("found 500", result["reason"])

    def test_insufficient_evidence(self):
        claim = EvidenceClaim(
            source_id="log-003",
            field="database_status",
            expected_value="crashed",
        )

        result = verify_claim(claim, self.sources)

        self.assertEqual(
            result["status"],
            "insufficient_evidence",
        )

    def test_unknown_source(self):
        claim = EvidenceClaim(
            source_id="log-999",
            field="status_code",
            expected_value=500,
        )

        result = verify_claim(claim, self.sources)

        self.assertEqual(
            result["status"],
            "unknown_source",
        )

    def test_collection_failure(self):
        """Araç hatasının sessizce boş kanıta dönüşmesini önler."""

        def failing_get_logs(service, start_time, end_time):
            return ToolResult(
                status="error",
                error=ToolError(
                    code="DATA_READ_ERROR",
                    message="Could not read logs",
                ),
            )

        with patch(
            "incident_assistant.evidence.evidence_support.get_logs",
            new=failing_get_logs,
        ):
            with self.assertRaises(RuntimeError) as context:
                collect_evidence_records()

        self.assertIn(
            "Could not collect evidence",
            str(context.exception),
        )


if __name__ == "__main__":
    unittest.main()
