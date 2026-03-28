---
phase: 91-protocol-runtime-decomposition-and-typed-boundary-hardening
plan: "02"
status: completed
completed: 2026-03-28
---

# Summary 91-02

**Typed-boundary hardening now converges on shared runtime truth: decode results/registries are narrower, telemetry snapshots share one typed contract spine, and OTA/control projections no longer need loose dynamic payload aliases.**

## Outcome

- `custom_components/lipro/core/protocol/boundary/{result.py,schema_registry.py,rest_decoder_support.py}` now keep covariant/narrow decode contracts without reopening `Any` seams.
- `custom_components/lipro/core/coordinator/types.py`, `custom_components/lipro/runtime_types.py`, `custom_components/lipro/core/command/trace.py`, `custom_components/lipro/core/coordinator/runtime/status_runtime.py`, and `custom_components/lipro/core/coordinator/services/telemetry_service.py` now share `RuntimeTelemetrySnapshot`, `MetricMapping`, and `TracePayload` truth.
- `custom_components/lipro/entities/firmware_update.py` keeps its protected thin-shell posture while projecting typed extra attributes and OTA-row selection through the shared cache helpers.

## Verification

- `uv run ruff check custom_components/lipro/runtime_types.py custom_components/lipro/core/coordinator/types.py custom_components/lipro/core/protocol/boundary/result.py custom_components/lipro/core/protocol/boundary/schema_registry.py custom_components/lipro/core/protocol/boundary/rest_decoder_support.py custom_components/lipro/core/protocol/boundary/rest_decoder.py custom_components/lipro/core/protocol/boundary/mqtt_decoder.py custom_components/lipro/core/command/trace.py custom_components/lipro/core/protocol/protocol_facade_rest_methods.py custom_components/lipro/core/coordinator/runtime/command_runtime.py custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py custom_components/lipro/core/coordinator/runtime/status_runtime.py custom_components/lipro/core/coordinator/runtime/command/confirmation.py custom_components/lipro/core/coordinator/services/telemetry_service.py custom_components/lipro/entities/firmware_update.py`
- `uv run pytest -q tests/core/coordinator/runtime/test_runtime_telemetry_methods.py tests/core/coordinator/runtime/test_command_runtime_orchestration.py tests/core/test_runtime_access.py tests/platforms/test_firmware_update_entity_edges.py`
- `uv run mypy custom_components/lipro/runtime_types.py custom_components/lipro/core/coordinator/types.py custom_components/lipro/core/protocol/boundary/result.py custom_components/lipro/core/protocol/boundary/schema_registry.py custom_components/lipro/core/protocol/boundary/rest_decoder_support.py custom_components/lipro/core/protocol/boundary/rest_decoder.py custom_components/lipro/core/protocol/boundary/mqtt_decoder.py custom_components/lipro/core/command/trace.py custom_components/lipro/core/protocol/protocol_facade_rest_methods.py custom_components/lipro/core/coordinator/runtime/command_runtime.py custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py custom_components/lipro/core/coordinator/runtime/status_runtime.py custom_components/lipro/core/coordinator/runtime/command/confirmation.py custom_components/lipro/core/coordinator/services/telemetry_service.py custom_components/lipro/entities/firmware_update.py`

## Task Commits

- None — per user instruction, this workspace keeps the phase uncommitted.

## Deviations from Plan

- `BoundaryDecodeResult` uses an immutable private payload slot + covariant property projection so mypy can keep covariance without reopening broad parameter typing.

## Next Readiness

- Phase 91-03 can now freeze governance/docs/guards on top of stable typed contracts instead of partially dynamic runtime truth.
