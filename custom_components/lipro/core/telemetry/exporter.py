"""Pull-first runtime telemetry exporter."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from hashlib import sha256
from secrets import token_hex
from time import time
from typing import Any

from .models import (
    SCHEMA_VERSION,
    CardinalityBudget,
    TelemetrySensitivity,
    TelemetrySnapshot,
    TelemetryViews,
)
from .ports import ProtocolTelemetrySource, RuntimeTelemetrySource, TelemetrySink
from .sinks import DEFAULT_TELEMETRY_SINKS

_SKIP = object()


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
        entry_ref = self._resolve_entry_ref(
            protocol_raw=protocol_raw,
            runtime_raw=runtime_raw,
            report_id=report_id,
        )
        return TelemetrySnapshot(
            schema_version=SCHEMA_VERSION,
            report_id=report_id,
            generated_at=float(self._time_provider()),
            entry_ref=entry_ref,
            protocol=self._sanitize_mapping(protocol_raw, report_id=report_id),
            runtime=self._sanitize_mapping(runtime_raw, report_id=report_id),
        )

    def export_views(self) -> TelemetryViews:
        """Export all stable sink projections from one shared snapshot."""
        snapshot = self.export_snapshot()
        rendered = {sink.name: dict(sink.build_view(snapshot)) for sink in self._sinks}
        return TelemetryViews(
            snapshot=snapshot,
            diagnostics=rendered["diagnostics"],
            system_health=rendered["system_health"],
            developer=rendered["developer"],
            ci=rendered["ci"],
        )

    def _new_report_id(self) -> str:
        """Create one report-local identifier for pseudonymous references."""
        try:
            return str(self._report_id_factory(6))
        except TypeError:
            return str(self._report_id_factory())

    def _resolve_entry_ref(
        self,
        *,
        protocol_raw: Mapping[str, Any],
        runtime_raw: Mapping[str, Any],
        report_id: str,
    ) -> str | None:
        entry_id = protocol_raw.get("entry_id")
        if not isinstance(entry_id, str):
            session = protocol_raw.get("session")
            if isinstance(session, Mapping):
                nested = session.get("entry_id")
                if isinstance(nested, str):
                    entry_id = nested
        if not isinstance(entry_id, str):
            nested = runtime_raw.get("entry_id")
            if isinstance(nested, str):
                entry_id = nested
        if not isinstance(entry_id, str) or not entry_id:
            return None
        return self._build_reference("entry_ref", entry_id, report_id)

    def _sanitize_mapping(
        self,
        payload: Mapping[str, Any],
        *,
        report_id: str,
    ) -> dict[str, Any]:
        sanitized: dict[str, Any] = {}
        for key, value in payload.items():
            key_text = str(key)
            if len(sanitized) >= self._cardinality_budget.max_mapping_items:
                break
            if self._sensitivity.is_blocked(key_text):
                continue
            alias = self._sensitivity.reference_alias_for(key_text)
            if alias is not None:
                reference = self._build_reference(alias, value, report_id)
                if reference is not None:
                    sanitized[alias] = reference
                continue
            sanitized_value = self._sanitize_value(
                value,
                key=key_text,
                report_id=report_id,
            )
            if sanitized_value is _SKIP:
                continue
            sanitized[key_text] = sanitized_value
        return sanitized

    def _sanitize_value(self, value: Any, *, key: str | None, report_id: str) -> Any:
        if key is not None and self._sensitivity.is_blocked(key):
            return _SKIP
        if isinstance(value, Mapping):
            return self._sanitize_mapping(value, report_id=report_id)
        if isinstance(value, Sequence) and not isinstance(
            value, (str, bytes, bytearray)
        ):
            result: list[Any] = []
            for item in value[: self._cardinality_budget.max_sequence_items]:
                sanitized_item = self._sanitize_value(
                    item,
                    key=None,
                    report_id=report_id,
                )
                if sanitized_item is _SKIP:
                    continue
                result.append(sanitized_item)
            return result
        if (
            isinstance(value, str)
            and len(value) > self._cardinality_budget.max_string_length
        ):
            return value[: self._cardinality_budget.max_string_length]
        return value

    def _build_reference(self, alias: str, value: Any, report_id: str) -> str | None:
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
