# Phase 57 Research

status: passed

## Question

- where should the typed command-result outcome / reason-code contract live so runtime sender and diagnostics consumers stop relying on scattered literals without growing a second helper story?

## Findings

1. `Phase 50` already converged command-result ownership into `custom_components/lipro/core/command/{result_policy.py,result.py}`, so the correct next move is to harden those homes rather than adding a new package or shared wrapper.
2. The repo already uses canonical `reason_code` language in other typed outcome families (`OperationOutcome`, anonymous-share outcome payloads), which means command-result flows are the notable stringly-typed outlier.
3. The outward behaviors that matter are already stable: diagnostics query service exposes `state` / `attempts` / `result`, while runtime sender exposes `verified` + classification / timeout semantics. Hardening should stay beneath those surfaces.
4. The narrowest honest contract is: typed aliases + shared constants + focused typed payload/trace helpers within the command-result family itself.

## Decision

- keep the formal home inside `result_policy.py` / `result.py`
- type the state / verification / failure-reason vocabulary there and re-export through `result.py`
- align runtime sender and diagnostics response typing to that shared contract without changing public semantics
- freeze the route in focused tests plus minimal public/dependency/governance notes

## Non-Goals

- no retry-policy unification across planes
- no new public package export or compat layer
- no conversion of command-result flows into a generalized telemetry framework
