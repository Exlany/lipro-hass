"""Collector that builds one AI Debug Evidence Pack from formal sources only."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime
import re
from secrets import token_hex
from typing import Any

from custom_components.lipro.core.telemetry.models import (
    SCHEMA_VERSION as TELEMETRY_SCHEMA_VERSION,
)
from tests.harness.evidence_pack.redaction import EvidencePackRedactor
from tests.harness.evidence_pack.schema import (
    EVIDENCE_PACK_INDEX_VERSION,
    EVIDENCE_PACK_SCHEMA_VERSION,
    AiDebugEvidencePack,
    EvidencePackMetadata,
)
from tests.harness.evidence_pack.sources import (
    ALLOWED_FORMAL_SOURCE_PATHS,
    AUTHORITY_MATRIX_PATH,
    BOUNDARY_INVENTORY_PATH,
    EVIDENCE_INDEX_PATH,
    KILL_LIST_PATH,
    REQUIREMENTS_PATH,
    RESIDUAL_LEDGER_PATH,
    ROADMAP_PATH,
    STATE_PATH,
    VERIFICATION_MATRIX_PATH,
    boundary_source_paths,
    governance_source_paths,
    read_formal_text,
    replay_source_paths,
    repo_relative,
    telemetry_source_paths,
)
from tests.harness.protocol.replay_assertions import build_replay_exporter_views
from tests.harness.protocol.replay_driver import ProtocolReplayDriver
from tests.harness.protocol.replay_loader import iter_replay_manifests
from tests.harness.protocol.replay_report import build_replay_run_summary

_COMMAND_PATTERN = re.compile(r"`(uv run [^`]+)`")
_RESIDUAL_PATTERN = re.compile(
    r"\| (Protocol-boundary family coverage|Replay scenario coverage) \| (?P<detail>.+?) \|"
)


class AiDebugEvidenceCollector:
    """Build one JSON-first evidence pack from registered formal sources."""

    def __init__(self, *, protocol_driver: ProtocolReplayDriver | None = None) -> None:
        self._protocol_driver = protocol_driver or ProtocolReplayDriver()

    def collect(
        self,
        *,
        report_id: str | None = None,
        generated_at: str | None = None,
    ) -> AiDebugEvidencePack:
        """Collect one pack from telemetry, replay, boundary, and governance truths."""
        report_id = report_id or token_hex(6)
        generated_at = generated_at or datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        redactor = EvidencePackRedactor(report_id=report_id)

        manifests = iter_replay_manifests()
        results = [self._protocol_driver.run_manifest(manifest) for manifest in manifests]
        telemetry_views_by_scenario = {
            manifest.scenario_id: build_replay_exporter_views(manifest, result)
            for manifest, result in zip(manifests, results, strict=True)
        }
        replay_summary = build_replay_run_summary(
            results,
            telemetry_views_by_scenario=telemetry_views_by_scenario,
        )
        telemetry_section = redactor.redact(
            {
                "source_paths": list(telemetry_source_paths()),
                "view_count": len(telemetry_views_by_scenario),
                "views": [
                    {
                        "scenario_id": manifest.scenario_id,
                        "channel": manifest.channel,
                        "snapshot": {
                            key: value
                            for key, value in telemetry_views_by_scenario[
                                manifest.scenario_id
                            ].snapshot.to_dict().items()
                            if key != "report_id"
                        },
                        "diagnostics": telemetry_views_by_scenario[
                            manifest.scenario_id
                        ].diagnostics,
                        "system_health": telemetry_views_by_scenario[
                            manifest.scenario_id
                        ].system_health,
                        "developer": telemetry_views_by_scenario[
                            manifest.scenario_id
                        ].developer,
                        "ci": telemetry_views_by_scenario[manifest.scenario_id].ci,
                    }
                    for manifest in manifests
                ],
            }
        )
        replay_section = redactor.redact(
            {
                "source_paths": list(replay_source_paths()),
                "summary": replay_summary,
            }
        )
        boundary_section = {
            "source_paths": list(boundary_source_paths()),
            "inventory_path": BOUNDARY_INVENTORY_PATH,
            "authority_matrix_path": AUTHORITY_MATRIX_PATH,
            "representative_families": [
                {
                    "scenario_id": manifest.scenario_id,
                    "channel": manifest.channel,
                    "family": manifest.family,
                    "version": manifest.version,
                    "manifest_path": repo_relative(manifest.manifest_path),
                    "authority_path": repo_relative(manifest.authority_path),
                    "assertion_families": list(manifest.assertion_families),
                }
                for manifest in manifests
            ],
            "carry_forward_residuals": self._extract_residuals(
                read_formal_text(RESIDUAL_LEDGER_PATH)
            ),
        }
        governance_text = read_formal_text(EVIDENCE_INDEX_PATH)
        governance_section = {
            "source_paths": list(governance_source_paths()),
            "evidence_index_path": EVIDENCE_INDEX_PATH,
            "verify_commands": self._extract_commands(
                [
                    governance_text,
                    read_formal_text(ROADMAP_PATH),
                    read_formal_text(REQUIREMENTS_PATH),
                ]
            ),
            "residual_pointer": RESIDUAL_LEDGER_PATH,
            "kill_list_path": KILL_LIST_PATH,
            "roadmap_path": ROADMAP_PATH,
            "requirements_path": REQUIREMENTS_PATH,
            "state_path": STATE_PATH,
        }
        return AiDebugEvidencePack(
            metadata=EvidencePackMetadata(
                schema_version=EVIDENCE_PACK_SCHEMA_VERSION,
                index_version=EVIDENCE_PACK_INDEX_VERSION,
                report_id=report_id,
                generated_at=generated_at,
                source_versions={
                    "telemetry": TELEMETRY_SCHEMA_VERSION,
                    "replay": replay_summary["schema_version"],
                    "governance": "v1.1.closeout",
                },
            ),
            telemetry=telemetry_section,
            replay=replay_section,
            boundary=boundary_section,
            governance=governance_section,
            index=self._build_index_section(),
        )

    @staticmethod
    def _extract_commands(texts: Iterable[str]) -> list[str]:
        commands: list[str] = []
        seen: set[str] = set()
        for text in texts:
            for command in _COMMAND_PATTERN.findall(text):
                if command not in seen:
                    seen.add(command)
                    commands.append(command)
        return commands

    @staticmethod
    def _extract_residuals(text: str) -> list[dict[str, str]]:
        residuals: list[dict[str, str]] = []
        for match in _RESIDUAL_PATTERN.finditer(text):
            residuals.append(
                {
                    "family": match.group(1),
                    "detail": match.group("detail"),
                }
            )
        return residuals

    @staticmethod
    def _build_index_section() -> dict[str, Any]:
        return {
            "allowed_formal_sources": list(ALLOWED_FORMAL_SOURCE_PATHS),
            "section_authority_trace": {
                "telemetry": list(telemetry_source_paths()),
                "replay": list(replay_source_paths()),
                "boundary": list(boundary_source_paths()),
                "governance": list(governance_source_paths()),
            },
            "verification_matrix_path": VERIFICATION_MATRIX_PATH,
            "notes": [
                "pull-only formal sources",
                "real timestamps allowed",
                "report-local pseudonymous refs only",
            ],
        }


def build_pack_index_markdown(pack: AiDebugEvidencePack) -> str:
    """Render one human-readable markdown index for the JSON pack."""
    payload = pack.to_dict()
    metadata = payload["metadata"]
    section_trace = payload["index"]["section_authority_trace"]
    lines = [
        "# AI Debug Evidence Pack Index",
        "",
        f"- `report_id`: `{metadata['report_id']}`",
        f"- `generated_at`: `{metadata['generated_at']}`",
        f"- `schema_version`: `{metadata['schema_version']}`",
        f"- `index_version`: `{metadata['index_version']}`",
        "",
        "## Sections",
        "",
    ]
    for section, sources in section_trace.items():
        lines.append(f"### {section}")
        for source in sources:
            lines.append(f"- `{source}`")
        lines.append("")
    lines.append("## Notes")
    lines.append("")
    for note in payload["index"]["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)
