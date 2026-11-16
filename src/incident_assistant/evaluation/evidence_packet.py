
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from incident_assistant.evaluation.claim_extractor import (
    ExtractedClaim,
)


class EvidenceRecord(BaseModel):
    """Bir iddiaya bağlanan gerçek kaynak kaydı."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    source_id: str = Field(min_length=1)
    record: dict[str, Any]


class EvidencePacket(BaseModel):
    """Bir iddia ve ona ait operasyonel kanıtlar."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    claim_id: str = Field(min_length=1)
    claim: str = Field(min_length=1)
    evidence: list[EvidenceRecord] = Field(min_length=1)


class MissingEvidenceError(ValueError):
    """İddianın referans verdiği kaynak bulunamadı."""


def build_evidence_packet(
    claim: ExtractedClaim,
    sources: dict[str, dict],
) -> EvidencePacket:
    """İddiayı kaynak kayıtlarıyla eşleştirir."""

    evidence = []

    for source_id in claim.source_ids:
        record = sources.get(source_id)

        if record is None:
            raise MissingEvidenceError(
                f"Missing evidence source: {source_id}"
            )

        evidence.append(
            EvidenceRecord(
                source_id=source_id,
                record=record,
            )
        )

    return EvidencePacket(
        claim_id=claim.claim_id,
        claim=claim.claim,
        evidence=evidence,
    )


def build_evidence_packets(
    claims: list[ExtractedClaim],
    sources: dict[str, dict],
) -> list[EvidencePacket]:
    """Birden fazla iddia için kanıt paketleri oluşturur."""

    return [
        build_evidence_packet(claim, sources)
        for claim in claims
    ]
