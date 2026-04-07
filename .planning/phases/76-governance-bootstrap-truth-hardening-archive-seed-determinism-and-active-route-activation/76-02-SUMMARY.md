---
phase: 76-governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation
plan: "02"
subsystem: archive-selectors
tags: [governance, milestones, archive, history, guards]
requirements-completed: [ARC-20]
completed: 2026-03-26
---

# Phase 76 Plan 02 Summary

**历史 milestone 叙事已退回 archive-only 身份，current/latest selector 不再被旧正文抢位，但审计与归档上下文完整保留。**

## Accomplishments
- `.planning/MILESTONES.md`、`.planning/ROADMAP.md` 与 `.planning/REQUIREMENTS.md` 现把 `v1.20`、`v1.19` 的旧 route truth 明确降级为 `historical closeout route truth` / `historical archive-transition route truth`，不再让历史 prose 伪装成 current selector。
- 历史 milestone 的 shipped / closeout 叙事、phase range、audit 与 evidence 指针继续保留，archive context 没有因 selector 收口而被删空。
- `tests/meta/test_governance_milestone_archives.py`、`tests/meta/governance_followup_route_current_milestones.py` 与 `tests/meta/test_phase75_governance_closeout_guards.py` 新增 focused guard，显式防守 historical route 重新抬头，并拒绝 `current governance state` / `live governance state` 这类旧 selector 文案回流。

## Proof
- `uv run pytest -q tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_phase75_governance_closeout_guards.py` → `25 passed`
