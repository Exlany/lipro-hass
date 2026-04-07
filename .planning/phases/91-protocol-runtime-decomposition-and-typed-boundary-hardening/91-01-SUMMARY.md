---
phase: 91-protocol-runtime-decomposition-and-typed-boundary-hardening
plan: "01"
status: completed
completed: 2026-03-28
---

# Summary 91-01

**Protocol live path now collapses onto one canonical boundary truth: raw REST child ports stay raw, while `LiproProtocolFacade` returns only canonical device-page/status/mesh-group/MQTT contracts to runtime consumers.**

## Outcome

- `custom_components/lipro/core/protocol/protocol_facade_rest_methods.py` now canonicalizes device list, device status, mesh-group status, and MQTT config at the protocol root.
- `custom_components/lipro/core/protocol/rest_port.py` remains the raw REST child-facing port family, so the child façade and the public protocol root no longer tell competing payload stories.
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py` and `custom_components/lipro/core/coordinator/orchestrator.py` now consume canonical protocol rows directly instead of re-normalizing the same payload.

## Verification

- `uv run pytest -q tests/core/api/test_protocol_contract_facade_runtime.py tests/core/api/test_protocol_contract_boundary_decoders.py`
- `uv run ruff check custom_components/lipro/core/protocol/protocol_facade_rest_methods.py custom_components/lipro/core/protocol/rest_port.py custom_components/lipro/core/coordinator/runtime/device/snapshot.py custom_components/lipro/core/coordinator/orchestrator.py tests/core/api/test_protocol_contract_facade_runtime.py`

## Task Commits

- None — per user instruction, this workspace keeps the phase uncommitted.

## Deviations from Plan

- None.

## Next Readiness

- Phase 91-02 can harden the shared typed-boundary / telemetry contracts without fighting a second live-path truth.
