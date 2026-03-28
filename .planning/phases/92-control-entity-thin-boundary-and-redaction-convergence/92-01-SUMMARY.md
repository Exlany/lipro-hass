---
phase: 92-control-entity-thin-boundary-and-redaction-convergence
plan: "01"
status: completed
completed: 2026-03-28
---

# Summary 92-01

**Shared redaction truth now converges on one canonical registry: diagnostics, anonymous-share, and telemetry all derive key normalization, secret-like detection, aliasing, and string-pattern redaction from `core/utils/redaction.py`.**

## Outcome

- `custom_components/lipro/core/utils/redaction.py` now owns the shared sensitive-key registry, reference-alias map, sink marker palette, and string redaction helpers.
- `custom_components/lipro/control/redaction.py` remains the diagnostics-facing adapter, but unknown secret-like keys now fail closed through the shared classifier instead of a sink-local folklore list.
- `custom_components/lipro/core/anonymous_share/sanitize.py` and `custom_components/lipro/core/telemetry/json_payloads.py` now derive their defaults from the same shared policy, while preserving their outward marker / budget contracts.

## Verification

- `uv run pytest -q tests/core/test_diagnostics_redaction.py tests/core/anonymous_share/test_sanitize.py tests/core/telemetry/test_models.py tests/core/telemetry/test_exporter.py`
- `uv run ruff check custom_components/lipro/core/utils/redaction.py custom_components/lipro/control/redaction.py custom_components/lipro/core/anonymous_share/sanitize.py custom_components/lipro/core/telemetry/json_payloads.py tests/core/test_diagnostics_redaction.py tests/core/anonymous_share/test_sanitize.py tests/core/telemetry/test_models.py tests/core/telemetry/test_exporter.py`

## Task Commits

- None — per user instruction, this workspace keeps the phase uncommitted.

## Deviations from Plan

- None.

## Next Readiness

- Phase 92-02 can converge diagnostics/report/exporter consumers on the shared contract without reopening a second sanitizer story.
