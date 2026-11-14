
import unittest

from pathlib import Path
from unittest.mock import patch

from incident_assistant.tools.specialist_dispatcher import dispatch_specialist_tool
from incident_assistant.contracts.tool_contract import ToolResult


class TestSpecialistDispatcher(unittest.TestCase):

    def test_forbidden_operational_tool(self):
        arguments = {
            "service": "checkout-api",
            "start_time": "2026-10-20T09:00:00Z",
            "end_time": "2026-10-20T09:15:00Z",
        }

        with patch(
            "incident_assistant.tools.specialist_dispatcher.dispatch_tool"
        ) as mocked_dispatch:

            result = dispatch_specialist_tool(
                "get_logs",
                arguments,
            )

            mocked_dispatch.assert_not_called()

        self.assertEqual(result.status, "error")
        self.assertEqual(
            result.error.code,
            "SPECIALIST_TOOL_FORBIDDEN",
        )

    def test_unknown_tool_forbidden(self):
        with patch(
            "incident_assistant.tools.specialist_dispatcher.dispatch_tool"
        ) as mocked_dispatch:

            result = dispatch_specialist_tool(
                "restart_service",
                {},
            )

            mocked_dispatch.assert_not_called()

        self.assertEqual(result.status, "error")
        self.assertEqual(
            result.error.code,
            "SPECIALIST_TOOL_FORBIDDEN",
        )

    def test_allowed_tool_forwarded(self):
        fake_result = ToolResult(
            status="success",
            data={
                "results": [],
                "count": 0,
                "embedding_tokens": 0,
            },
        )

        arguments = {
            "query": "HTTP 500 errors",
            "top_k": 3,
        }

        with patch(
            "incident_assistant.tools.specialist_dispatcher.dispatch_tool",
            return_value=fake_result,
        ) as mocked_dispatch:

            result = dispatch_specialist_tool(
                "search_runbooks",
                arguments,
            )

            mocked_dispatch.assert_called_once_with(
                "search_runbooks",
                arguments,
            )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["count"], 0)

    def test_invalid_runbook_arguments(self):
        result = dispatch_specialist_tool(
            "search_runbooks",
            {
                "query": "HTTP 500",
                "top_k": "three",
            },
        )

        self.assertEqual(result.status, "error")
        self.assertEqual(
            result.error.code,
            "INVALID_ARGUMENTS",
        )


if __name__ == "__main__":
    unittest.main()
