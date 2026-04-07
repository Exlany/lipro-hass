---
phase: 66-release-target-fidelity-adapter-root-cleanup-and-focused-protocol-coverage-hardening
plan: "03"
status: completed
completed_at: "2026-03-23T00:00:00Z"
verification:
  - uv run pytest -q tests/core/api/test_api_transport_executor.py tests/core/coordinator/services/test_protocol_service.py tests/core/protocol/test_facade.py tests/core/api/test_protocol_contract_matrix.py
---

# Phase 66 Plan 03 Summary

## Objective

Add focused regression suites for the protocol transport / service / root seams so these hotspots no longer depend primarily on the mega-matrix contract tests for break detection.

## Completed Work

- `tests/core/api/test_api_transport_executor.py` now covers session/core alignment, session close semantics, and signed-header construction at the explicit transport-executor seam.
- `tests/core/coordinator/services/test_protocol_service.py` now covers schedule forwarding, `mesh_member_ids` normalization/copying, mapping-surface dict detachment, and formal protocol-home routing.
- `tests/core/protocol/test_facade.py` now covers shared rest-state / request-policy ownership, MQTT child attachment, protocol diagnostics snapshots, and MQTT error telemetry recording.
- `tests/core/api/test_protocol_contract_matrix.py` remains as the higher-level contract layer, but no longer carries the full burden of basic protocol seam behavior.

## Files Modified

- `tests/core/api/test_api_transport_executor.py`
- `tests/core/coordinator/services/test_protocol_service.py`
- `tests/core/protocol/test_facade.py`

## Verification

- `uv run pytest -q tests/core/api/test_api_transport_executor.py tests/core/coordinator/services/test_protocol_service.py tests/core/protocol/test_facade.py tests/core/api/test_protocol_contract_matrix.py` → `56 passed in 0.80s`

## Scope Notes

- This plan intentionally strengthened focused seam coverage without expanding the production surface or reworking the higher-level contract matrix.
