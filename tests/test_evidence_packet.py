
import unittest

from incident_assistant.evaluation.claim_extractor import (
    ExtractedClaim,
)

from incident_assistant.evaluation.evidence_packet import (
    MissingEvidenceError,
    build_evidence_packet,
    build_evidence_packets,
)


class TestEvidencePacket(unittest.TestCase):

    def setUp(self):
        self.sources = {
            "log-003": {
                "log_id": "log-003",
                "status_code": 500,
                "message": "GET /orders failed",
            },
            "log-004": {
                "log_id": "log-004",
                "status_code": 500,
                "message": "POST /checkout failed",
            },
        }

    def make_claim(self, source_ids):
        return ExtractedClaim(
            claim_id="finding-001",
            claim="HTTP 500 errors observed",
            source_ids=source_ids,
            claim_type="finding",
        )

    def test_single_source_packet(self):
        claim = self.make_claim(["log-003"])

        packet = build_evidence_packet(
            claim,
            self.sources,
        )

        self.assertEqual(packet.claim_id, "finding-001")
        self.assertEqual(len(packet.evidence), 1)
        self.assertEqual(
            packet.evidence[0].record["status_code"],
            500,
        )

    def test_multiple_sources_preserved(self):
        claim = self.make_claim([
            "log-003",
            "log-004",
        ])

        packet = build_evidence_packet(
            claim,
            self.sources,
        )

        self.assertEqual(
            [
                item.source_id
                for item in packet.evidence
            ],
            ["log-003", "log-004"],
        )

    def test_missing_source_rejected(self):
        claim = self.make_claim(["log-999"])

        with self.assertRaises(MissingEvidenceError):
            build_evidence_packet(
                claim,
                self.sources,
            )

    def test_batch_packet_generation(self):
        claims = [
            ExtractedClaim(
                claim_id="finding-001",
                claim="First error",
                source_ids=["log-003"],
                claim_type="finding",
            ),
            ExtractedClaim(
                claim_id="finding-002",
                claim="Second error",
                source_ids=["log-004"],
                claim_type="finding",
            ),
        ]

        packets = build_evidence_packets(
            claims,
            self.sources,
        )

        self.assertEqual(len(packets), 2)
        self.assertEqual(
            packets[1].evidence[0].source_id,
            "log-004",
        )


if __name__ == "__main__":
    unittest.main()
