# Phase 90: Hotspot routing freeze and formal-home decomposition map - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `90-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-03-28
**Phase:** 90-hotspot-routing-freeze-and-formal-home-decomposition-map
**Mode:** auto (`--auto` equivalent decisions synthesized from repo-wide audit)
**Areas discussed:** hotspot ownership freeze, REST/runtime decomposition line, anonymous-share boundary, thin-shell protection, delete-gate policy

---

## Hotspot ownership freeze

| Option | Description | Selected |
|--------|-------------|----------|
| Keep all five hotspots as formal homes | Preserve outward ownership and only allow inward split via sibling/support families | ✓ |
| Downgrade some hotspots to thin shells now | Recast large homes as shells before proving collaborator boundaries | |
| Mark hotspots as delete targets | Treat file size itself as deletion evidence | |

**Auto choice:** Keep all five hotspots as formal homes
**Notes:** Repo-wide audit shows these modules are large but still own legitimate orchestration or policy truth; size alone is not delete-gate evidence.

---

## REST and runtime decomposition line

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve current outward homes and deepen sibling splits | `rest_facade.py`, `request_policy.py`, `command_runtime.py`, `mqtt_runtime.py` stay as owners while helpers sink inward | ✓ |
| Create new façade/root layers for slimmer top files | Introduce additional outward shells to reduce line counts | |
| Spread ownership across helpers opportunistically | Let each touched helper become partial public truth | |

**Auto choice:** Preserve current outward homes and deepen sibling splits
**Notes:** Current code already exposes the correct pattern: `runtime/command/*`, `runtime/mqtt/*`, `request_policy_support.py`, `manager_submission.py`.

---

## Anonymous-share boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Keep `manager.py` as protocol-plane formal home for now | Record redaction convergence as downstream dependency only | ✓ |
| Re-home anonymous-share under control/redaction now | Merge ownership during the map-freeze phase | |
| Split aggregate and scoped flows into separate outward roots | Optimize by introducing distinct manager roots | |

**Auto choice:** Keep `manager.py` as protocol-plane formal home for now
**Notes:** `Phase 90` only freezes map truth. Real redaction convergence belongs to `SEC-01 / Phase 92`.

---

## Thin-shell protection

| Option | Description | Selected |
|--------|-------------|----------|
| Freeze thin-shell protection line now | Mark `__init__.py`, `runtime_access.py`, `entities/base.py`, `entities/firmware_update.py` as protected outward shells | ✓ |
| Leave shell boundaries implicit | Trust later phases to remember not to re-grow orchestration | |
| Allow tactical orchestration spillover if refactor gets easier | Use shells as temporary landing pads | |

**Auto choice:** Freeze thin-shell protection line now
**Notes:** User asked for彻底收口；最容易反复长回来的恰好是 outward shells，必须先锁边界结论。

---

## Delete-gate policy

| Option | Description | Selected |
|--------|-------------|----------|
| Only register explicit residuals with owner/phase/delete gate | Avoid accidental deletion narratives and keep later phases auditable | ✓ |
| Treat every large module as latent delete target | Bias planning toward file eradication | |
| Defer delete-gate discussion entirely | Leave residual routing to implementation time | |

**Auto choice:** Only register explicit residuals with owner/phase/delete gate
**Notes:** `Phase 90` should reduce ambiguity, not create folklore-driven cleanup pressure.

---

## the agent's Discretion

- Decide the exact freeze-table / evidence-matrix format that best fits planning and follow-up guards.
- Decide how much `.planning/codebase/*.md` evidence should be promoted into phase artifacts without letting derived docs outrank baseline/review truth.

## Deferred Ideas

- `Phase 91` actual protocol/runtime refactors and typing hardening.
- `Phase 92` control/entity/redaction convergence and assurance topicization.
- `Phase 93` final quality freeze and benchmark budget story.
- Full repo polish beyond hotspot map truth, including additional open-source wording cleanup and non-targeted residual pruning.
