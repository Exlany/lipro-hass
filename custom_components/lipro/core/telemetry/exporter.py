"""Pull-first runtime telemetry exporter."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from hashlib import sha256
from secrets import token_hex
from time import time
from typing import cast

from ..utils.redaction import (
    SHARE_REDACTION_MARKERS,
    redact_sensitive_literal,
    redact_sensitive_text,
)
from .models import (
    SCHEMA_VERSION,
    CardinalityBudget,
    CITelemetryView,
    DeveloperTelemetryView,
    DiagnosticsTelemetryView,
    SystemHealthTelemetryView,
    TelemetryJsonValue,
    TelemetrySensitivity,
    TelemetrySnapshot,
    TelemetrySourcePayload,
    TelemetryViews,
)
from .ports import ProtocolTelemetrySource, RuntimeTelemetrySource, TelemetrySink
from .sinks import DEFAULT_TELEMETRY_SINKS

_SKIP = object()
_SUMMARY_MARKERS = (
    SHARE_REDACTION_MARKERS.token,
    SHARE_REDACTION_MARKERS.secret,
    SHARE_REDACTION_MARKERS.device_id,
    SHARE_REDACTION_MARKERS.mac,
    SHARE_REDACTION_MARKERS.ip,
)


class RuntimeTelemetryExporter:
    """Merge protocol/runtime snapshots into stable sink projections."""

    def __init__(
        self,
        *,
        protocol_source: ProtocolTelemetrySource,
        runtime_source: RuntimeTelemetrySource,
        sinks: Sequence[TelemetrySink] = DEFAULT_TELEMETRY_SINKS,
        sensitivity: TelemetrySensitivity | None = None,
        cardinality_budget: CardinalityBudget | None = None,
        time_provider: Callable[[], float] = time,
        report_id_factory: Callable[..., str] = token_hex,
    ) -> None:
        """Initialize the exporter with explicit source/sink collaborators."""
        self._protocol_source = protocol_source
        self._runtime_source = runtime_source
        self._sinks = tuple(sinks)
        self._sensitivity = sensitivity or TelemetrySensitivity()
        self._cardinality_budget = cardinality_budget or CardinalityBudget()
        self._time_provider = time_provider
        self._report_id_factory = report_id_factory
        self._reference_cache: dict[tuple[str, str], str] = {}

    def export_snapshot(self) -> TelemetrySnapshot:
        """Export one normalized snapshot from the configured sources."""
        report_id = self._new_report_id()
        protocol_raw = dict(self._protocol_source.get_protocol_telemetry_snapshot())
        runtime_raw = dict(self._runtime_source.get_runtime_telemetry_snapshot())
        self._reference_cache.clear()
        return TelemetrySnapshot(
            schema_version=SCHEMA_VERSION,
            report_id=report_id,
            generated_at=float(self._time_provider()),
            entry_ref=self._resolve_entry_ref(
                protocol_raw=protocol_raw,
                runtime_raw=runtime_raw,
                report_id=report_id,
            ),
            protocol=self._sanitize_mapping(protocol_raw, report_id=report_id),
            runtime=self._sanitize_mapping(runtime_raw, report_id=report_id),
        )

    def export_views(self) -> TelemetryViews:
        """Export all stable sink projections from one shared snapshot."""
        snapshot = self.export_snapshot()
        rendered = {sink.name: sink.build_view(snapshot) for sink in self._sinks}
        return TelemetryViews(
            snapshot=snapshot,
            diagnostics=cast(DiagnosticsTelemetryView, rendered["diagnostics"]),
            system_health=cast(
                SystemHealthTelemetryView,
                rendered["system_health"],
            ),
            developer=cast(DeveloperTelemetryView, rendered["developer"]),
            ci=cast(CITelemetryView, rendered["ci"]),
        )

    def _new_report_id(self) -> str:
        """Create one report-local identifier for pseudonymous references."""
        try:
            return str(self._report_id_factory(6))
        except TypeError:
            return str(self._report_id_factory())

    @staticmethod
    def _extract_entry_id(
        payload: Mapping[str, TelemetryJsonValue],
        *,
        primary_key: str,
        nested_mapping_key: str | None = None,
        nested_key: str = "entry_id",
    ) -> str | None:
        value = payload.get(primary_key)
        if isinstance(value, str) and value:
            return value
        if nested_mapping_key is None:
            return None
        nested_mapping = payload.get(nested_mapping_key)
        if not isinstance(nested_mapping, dict):
            return None
        nested_value = nested_mapping.get(nested_key)
        if isinstance(nested_value, str) and nested_value:
            return nested_value
        return None

    def _resolve_entry_ref(
        self,
        *,
        protocol_raw: Mapping[str, TelemetryJsonValue],
        runtime_raw: Mapping[str, TelemetryJsonValue],
        report_id: str,
    ) -> str | None:
        entry_id = self._extract_entry_id(
            protocol_raw,
            primary_key="entry_id",
            nested_mapping_key="session",
        )
        if entry_id is None:
            entry_id = self._extract_entry_id(runtime_raw, primary_key="entry_id")
        if entry_id is None:
            return None
        return self._build_reference("entry_ref", entry_id, report_id)

    def _sanitize_mapping(
        self,
        payload: Mapping[str, TelemetryJsonValue],
        *,
        report_id: str,
    ) -> TelemetrySourcePayload:
        sanitized: TelemetrySourcePayload = {}
        for key, value in payload.items():
            key_text = str(key)
            if len(sanitized) >= self._cardinality_budget.max_mapping_items:
                break
            sanitized_entry = self._sanitize_mapping_entry(
                key_text,
                value,
                report_id=report_id,
            )
            if sanitized_entry is None:
                continue
            entry_key, entry_value = sanitized_entry
            sanitized[entry_key] = entry_value
        return sanitized

    def _sanitize_mapping_entry(
        self,
        key: str,
        value: TelemetryJsonValue,
        *,
        report_id: str,
    ) -> tuple[str, TelemetryJsonValue] | None:
        if self._sensitivity.is_blocked(key):
            return None
        alias = self._sensitivity.reference_alias_for(key)
        if alias is not None:
            reference = self._build_reference(alias, value, report_id)
            if reference is None:
                return None
            return alias, reference
        sanitized_value = self._sanitize_value(
            value,
            key=key,
            report_id=report_id,
        )
        if sanitized_value is _SKIP:
            return None
        return key, cast(TelemetryJsonValue, sanitized_value)

    def _summarize_redacted_string(self, value: str) -> str | None:
        """Return a compact marker summary when a redacted string exceeds budget."""
        positions: list[tuple[int, str]] = []
        for marker in _SUMMARY_MARKERS:
            position = value.find(marker)
            if position >= 0:
                positions.append((position, marker))
        if not positions:
            return None
        summary = " ".join(dict.fromkeys(marker for _, marker in sorted(positions)))
        if len(summary) <= self._cardinality_budget.max_string_length:
            return summary
        return None

    def _sanitize_sequence(
        self,
        value: list[TelemetryJsonValue],
        *,
        report_id: str,
    ) -> list[TelemetryJsonValue]:
        result: list[TelemetryJsonValue] = []
        for item in value[: self._cardinality_budget.max_sequence_items]:
            sanitized_item = self._sanitize_value(
                item,
                key=None,
                report_id=report_id,
            )
            if sanitized_item is _SKIP:
                continue
            result.append(cast(TelemetryJsonValue, sanitized_item))
        return result

    def _sanitize_string_value(self, value: str) -> TelemetryJsonValue:
        literal = redact_sensitive_literal(
            value,
            markers=SHARE_REDACTION_MARKERS,
        )
        if literal is not None:
            return literal

        sanitized = redact_sensitive_text(
            value,
            markers=SHARE_REDACTION_MARKERS,
        )
        if sanitized != value:
            if len(sanitized) > self._cardinality_budget.max_string_length:
                marker_summary = self._summarize_redacted_string(sanitized)
                if marker_summary is not None:
                    return marker_summary
                return sanitized[: self._cardinality_budget.max_string_length]
            return sanitized

        if len(value) > self._cardinality_budget.max_string_length:
            return value[: self._cardinality_budget.max_string_length]
        return value

    def _sanitize_value(
        self,
        value: TelemetryJsonValue,
        *,
        key: str | None,
        report_id: str,
    ) -> TelemetryJsonValue | object:
        if key is not None and self._sensitivity.is_blocked(key):
            return _SKIP
        if isinstance(value, dict):
            return self._sanitize_mapping(value, report_id=report_id)
        if isinstance(value, list):
            return self._sanitize_sequence(value, report_id=report_id)
        if isinstance(value, str):
            return self._sanitize_string_value(value)
        return value

    def _build_reference(
        self,
        alias: str,
        value: TelemetryJsonValue,
        report_id: str,
    ) -> str | None:
        if value is None:
            return None
        raw = str(value)
        if not raw:
            return None
        cache_key = (alias, raw)
        cached = self._reference_cache.get(cache_key)
        if cached is not None:
            return cached
        prefix = "entry" if alias == "entry_ref" else "device"
        digest = sha256(f"{report_id}:{raw}".encode()).hexdigest()[:8]
        reference = f"{prefix}_{digest}"
        self._reference_cache[cache_key] = reference
        return reference


__all__ = ["RuntimeTelemetryExporter"]
