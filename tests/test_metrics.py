
import unittest
from pathlib import Path

from incident_assistant.core.metrics import AgentMetrics, aggregate_metrics


class TestMetrics(unittest.TestCase):

    def setUp(self):
        self.main = AgentMetrics(
            input_tokens=9699,
            output_tokens=2701,
            embedding_tokens=0,
            duration_seconds=51.52,
        )

        self.specialist = AgentMetrics(
            input_tokens=2213,
            output_tokens=832,
            embedding_tokens=378,
            duration_seconds=12.11,
        )

    def test_token_aggregation(self):
        result = aggregate_metrics(
            self.main,
            self.specialist,
        )

        self.assertEqual(result.input_tokens, 11912)
        self.assertEqual(result.output_tokens, 3533)
        self.assertEqual(result.total_model_tokens, 15445)

    def test_embedding_aggregation(self):
        result = aggregate_metrics(
            self.main,
            self.specialist,
        )

        self.assertEqual(result.embedding_tokens, 378)

    def test_duration_not_double_counted(self):
        result = aggregate_metrics(
            self.main,
            self.specialist,
        )

        self.assertEqual(result.wall_time_seconds, 51.52)

    def test_zero_specialist_usage(self):
        empty_specialist = AgentMetrics(
            input_tokens=0,
            output_tokens=0,
            embedding_tokens=0,
            duration_seconds=0.0,
        )

        result = aggregate_metrics(
            self.main,
            empty_specialist,
        )

        self.assertEqual(result.input_tokens, 9699)
        self.assertEqual(result.output_tokens, 2701)
        self.assertEqual(result.embedding_tokens, 0)


if __name__ == "__main__":
    unittest.main()
