"""Typed schema for the AI Debug Evidence Pack."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

EVIDENCE_PACK_SCHEMA_VERSION = "ai_debug_evidence_pack.v1"
EVIDENCE_PACK_INDEX_VERSION = "ai_debug_evidence_pack.index.v1"
PACK_SECTIONS = (
    "metadata",
    "telemetry",
    "replay",
    "boundary",
    "governance",
    "index",
)


@dataclass(frozen=True, slots=True)
class EvidencePackMetadata:
    """Top-level metadata for one generated evidence pack."""

    schema_version: str
    index_version: str
    report_id: str
    generated_at: str
    source_versions: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "index_version": self.index_version,
            "report_id": self.report_id,
            "generated_at": self.generated_at,
            "source_versions": dict(self.source_versions),
        }


@dataclass(frozen=True, slots=True)
class AiDebugEvidencePack:
    """Stable JSON-first evidence-pack envelope."""

    metadata: EvidencePackMetadata
    telemetry: dict[str, Any]
    replay: dict[str, Any]
    boundary: dict[str, Any]
    governance: dict[str, Any]
    index: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "metadata": self.metadata.to_dict(),
            "telemetry": self.telemetry,
            "replay": self.replay,
            "boundary": self.boundary,
            "governance": self.governance,
            "index": self.index,
        }
        missing = [section for section in PACK_SECTIONS if section not in payload]
        if missing:
            msg = f"Evidence pack missing required sections: {missing}"
            raise ValueError(msg)
        return payload
