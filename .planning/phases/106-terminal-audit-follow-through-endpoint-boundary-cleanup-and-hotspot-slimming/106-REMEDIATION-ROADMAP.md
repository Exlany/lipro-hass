# Phase 106 Remediation Roadmap

## Fixed in Phase 106

- remove endpoint-private auth collaborator reach-through
- slim device-status batching orchestration
- slim options-flow schema composition
- align ADR terminology with current `facade` contract

## Best Next Formal Phases

### Future Phase Seed A: REST/auth/status hotspot convergence
- target files: `core/api/rest_facade.py`, `core/api/status_fallback_support.py`, `core/api/request_policy_support.py`
- purpose: further reduce decision density without widening public surface

### Future Phase Seed B: Anonymous-share manager decomposition
- target files: `core/anonymous_share/manager.py`, `manager_support.py`, `manager_submission.py`
- purpose: continue inward split so manager stops being a high-branch orchestration shell

### Future Phase Seed C: Runtime snapshot surface reduction
- target files: `core/coordinator/runtime/device/snapshot.py`, adjacent runtime snapshot helpers/tests
- purpose: shrink snapshot assembly carrier and isolate formatting vs sourcing vs arbitration logic

### Future Phase Seed E: MQTT transport-runtime de-friendization
- target files: `core/mqtt/transport_runtime.py`, `core/mqtt/transport.py`, adjacent runtime lifecycle tests
- purpose: remove whole-file private-state reach-through and replace it with explicit owner/state contract

- target files: `core/coordinator/runtime/device/snapshot.py`, adjacent runtime snapshot helpers/tests
- purpose: shrink snapshot assembly carrier and isolate formatting vs sourcing vs arbitration logic

## Non-Goals

- not reopening `v1.29` as active route
- not doing archive-transition churn without a fresh milestone bootstrap
- not pretending organizational continuity risk is solvable by code-only edits
