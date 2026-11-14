
import unittest

from pathlib import Path
from unittest.mock import patch
from pydantic import ValidationError


# src klasöründeki modülleri import edebilmek için

from incident_assistant.tools.incident_tools import get_logs, get_deployments
from incident_assistant.tools.service_tools import get_service_status
from incident_assistant.contracts.tool_contract import ToolResult


START = "2026-10-20T09:00:00Z"
END = "2026-10-20T09:15:00Z"


class TestIncidentTools(unittest.TestCase):

    def test_valid_logs(self):
        result = get_logs("checkout-api", START, END)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["count"], 3)

        log_ids = {
            record["log_id"]
            for record in result.data["records"]
        }

        self.assertEqual(
            log_ids,
            {"log-002", "log-003", "log-004"}
        )

    def test_no_logs_found(self):
        result = get_logs(
            "checkout-api",
            "2026-10-20T11:00:00Z",
            "2026-10-20T11:15:00Z",
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["count"], 0)
        self.assertEqual(result.data["records"], [])
        self.assertIsNone(result.error)

    def test_invalid_time_range(self):
        result = get_logs(
            "checkout-api",
            "2026-10-20T10:00:00Z",
            "2026-10-20T09:00:00Z",
        )

        self.assertEqual(result.status, "error")
        self.assertEqual(result.error.code, "INVALID_INPUT")
        self.assertTrue(result.error.message)

    def test_log_file_error(self):
        with patch(
            "incident_assistant.data.inspect_logs.LOG_FILE",
            Path("nonexistent_logs.jsonl")
        ):
            result = get_logs("checkout-api", START, END)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.error.code, "DATA_READ_ERROR")
        self.assertTrue(result.error.message)

    def test_deployment_file_error(self):
        with patch(
            "incident_assistant.tools.incident_tools.DEPLOYMENT_FILE",
            Path("nonexistent_deployments.jsonl")
        ):
            result = get_deployments(
                "checkout-api", START, END
            )

        self.assertEqual(result.status, "error")
        self.assertEqual(result.error.code, "DATA_READ_ERROR")
        self.assertTrue(result.error.message)

    def test_invalid_json_file(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as temp_dir:
            bad_file = Path(temp_dir) / "bad_logs.jsonl"
            bad_file.write_text(
                "this is not valid json\n",
                encoding="utf-8"
            )

            with patch(
                "incident_assistant.data.inspect_logs.LOG_FILE",
                bad_file,
            ):
                result = get_logs("checkout-api", START, END)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.error.code, "DATA_READ_ERROR")

    def test_error_requires_details(self):
        with self.assertRaises(ValidationError):
            ToolResult(status="error", error=None)

    def test_service_status_contract(self):
        result = get_service_status(
            "checkout-api", START, END
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["count"], 2)

    def test_deployment_contract(self):
        result = get_deployments(
            "checkout-api", START, END
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["count"], 1)


if __name__ == "__main__":
    unittest.main()
