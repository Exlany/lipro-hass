---
phase: 90
slug: hotspot-routing-freeze-and-formal-home-decomposition-map
status: passed
verified_on: 2026-03-28
requirements:
  - HOT-40
---

# Phase 90 Verification

## Goal

验证 `Phase 90` 是否真正把 repo-wide terminal audit 的热点裁决冻结成唯一 current truth：five hotspots 继续保留 formal-home ownership，four outward shells 继续保持 protected thin posture，delete-gate 只允许 localized explicit entry，后续实现路线被清晰前推到 `Phase 91 -> 93`。

## Must-Have Score

- Verified: `4 / 4`
- Human-only items: `0`
- Gaps found: `0`

## Requirement Verdict

| Requirement | Verdict | Evidence |
|-------------|---------|----------|
| `HOT-40` | ✅ passed | `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`、`.planning/baseline/{PUBLIC_SURFACES,DEPENDENCY_MATRIX,VERIFICATION_MATRIX}.md`、`.planning/reviews/{FILE_MATRIX,RESIDUAL_LEDGER,KILL_LIST}.md`、`docs/developer_architecture.md` 与 `tests/meta/test_phase90_hotspot_map_guards.py` 共同证明 five hotspots / four protected shells / delete-gate policy 已冻结。 |

## Automated Proof

- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_phase90_hotspot_map_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py`
- `uv run pytest -q tests/meta`
- `uv run ruff check .`
- `uv run mypy`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 90`

## Verified Outcomes

- `client.py` no longer appears as a thin REST composition root in review truth; it is frozen as a stable import shell / home.
- `command_runtime.py`、`rest_facade.py`、`request_policy.py`、`mqtt_runtime.py` 与 `anonymous_share/manager.py` are explicitly preserved as formal homes.
- `__init__.py`、`runtime_access.py`、`entities/base.py` 与 `entities/firmware_update.py` are explicitly preserved as protected thin shells / projections.
- Current-route truth now honestly points to `Phase 90 complete` and `Phase 91` as the next discussion / planning hop.

## Human Verification

- none

## Gaps

- none

## Verdict

`Phase 90` 达成目标，当前里程碑已准备进入 `Phase 91` discussion / planning 路由。
