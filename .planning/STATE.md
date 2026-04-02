---
gsd_state_version: 1.0
milestone: v1.38
milestone_name: Governance Story Compression, Archive Segregation & Public Entry Simplification
status: archived / evidence-ready (2026-04-02)
stopped_at: Milestone closeout complete; next step = $gsd-new-milestone
last_updated: '2026-04-02T23:59:59Z'
last_activity: '2026-04-02'
progress:
  total_phases: 1
  completed_phases: 1
  total_plans: 3
  completed_plans: 3
  percent: 100
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-04-02)

<!-- governance-route-contract:start -->
```yaml
contract_version: 1
contract_name: governance-route
projection_targets:
- .planning/PROJECT.md
- .planning/ROADMAP.md
- .planning/REQUIREMENTS.md
- .planning/STATE.md
- .planning/MILESTONES.md
active_milestone: null
latest_archived:
  version: v1.38
  name: Governance Story Compression, Archive Segregation & Public Entry Simplification
  status: archived / evidence-ready (2026-04-02)
  phase: '132'
  phase_title: current-story compression and archive-boundary cleanup
  phase_dir: 132-current-story-compression-and-archive-boundary-cleanup
  audit_path: .planning/v1.38-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_38_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.37
  name: Repo-Wide Terminal Audit, Hotspot Decomposition & Governance Continuity Decisions
  evidence_path: .planning/reviews/V1_37_EVIDENCE_INDEX.md
bootstrap:
  current_route: no active milestone route / latest archived baseline = v1.38
  default_next_command: $gsd-new-milestone
  latest_archived_evidence_pointer: .planning/reviews/V1_38_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->
**Current milestone:** `No active milestone route`
**Latest archived milestone:** `v1.38 Governance Story Compression, Archive Segregation & Public Entry Simplification`
**Previous archived milestone:** `v1.37 Repo-Wide Terminal Audit, Hotspot Decomposition & Governance Continuity Decisions`
**Core value:** `v1.38 已把 current selector、archive boundary、developer/runbook first-hop 与 meta helper 当前真相压回单一路径；closeout 后保持 archived-only selector truth 稳定，为下一轮新路线留出干净入口。`
**Current focus:** `Milestone closeout complete — Phase 132 evidence 已冻结为 latest archived baseline，后续如需继续推进需从 `$gsd-new-milestone` 显式重启。`
**Current mode:** `no active milestone route / latest archived baseline = v1.38`

## Current Position

- **Phase:** `132 of 132`
- **Plan:** `3 of 3`
- **Status:** `archived / evidence-ready (2026-04-02)`
- **Last activity:** `2026-04-02` — 已完成 `v1.38` milestone closeout、archived snapshots / audit / evidence index 归档与 live selector archived-only 切换。
- **Progress:** `[██████████] 100%`

## Performance Metrics

- **Total plans completed:** `3`
- **Average duration:** `-`
- **Total execution time:** `-`

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 132 | complete | 3/3 | - |

## Governance Truth Sources

- Primary route contract: `.planning/PROJECT.md`
- Route execution map: `.planning/ROADMAP.md`
- Requirement coverage truth: `.planning/REQUIREMENTS.md`
- Latest archived evidence pointer: `.planning/reviews/V1_38_EVIDENCE_INDEX.md`
- Latest archived audit verdict: `.planning/v1.38-MILESTONE-AUDIT.md`
- Latest archived snapshots: `.planning/milestones/v1.38-ROADMAP.md`, `.planning/milestones/v1.38-REQUIREMENTS.md`
- Previous archived snapshots: `.planning/milestones/v1.37-ROADMAP.md`, `.planning/milestones/v1.37-REQUIREMENTS.md`
- Promoted phase evidence allowlist: `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- Latest archived phase workspace: `.planning/phases/132-current-story-compression-and-archive-boundary-cleanup/`
- North-star authority: `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`

## Accumulated Context

### Decisions

- `v1.38` 已成为 latest archived baseline；selector truth 已切回 archived-only route，不再把 `Phase 132` closeout-ready 中间态保留为 live default story。
- `Phase 132` 已完成 planning docs archived-only refresh、developer/runbook first-hop 切换、route-marker helper dedupe，以及 recent promoted-asset coverage 从 handoff smoke 回流到 promoted suites。
- canonical route 继续以 `.planning/baseline/GOVERNANCE_REGISTRY.json::planning_route` 为唯一 machine-readable truth；future work 只能通过 `$gsd-new-milestone` 显式建立新路线。

### Pending Todos

- 若要继续处理 production hotspots，优先显式 reopen `runtime_types.py` / coordinator-service contract family、`core/auth/manager.py`、`request_policy.py` / `dispatch.py`，而不要回写 `v1.38` archived truth。
- 若要启动下一轮治理或重构波次，直接执行 `$gsd-new-milestone`。

### Blockers/Concerns

- 当前无 closeout blocker；主要 remaining concern 是 sanctioned hotspot breadth 与 archive-era governance mega-suite topicization，它们已诚实保留为 future work，而不是当前 active route debt。
- `v1.38` archived truth 现已稳定；除非开新 milestone，否则不要把 active planning / execution 命令重新写回 current docs。

## Recommended Next Command

- **Primary:** `$gsd-new-milestone` — 基于 `v1.38` latest archived baseline 启动下一轮正式路线。
- **Status check:** `$gsd-next` — 若要重新计算当前路线的自动下一步，可在任意阶段复核。

## Session Continuity

- **Last session:** 2026-04-02T23:59:59Z
- **Stopped at:** Milestone closeout complete; latest archived baseline = `v1.38`.
- **Resume file:** `.planning/reviews/V1_38_EVIDENCE_INDEX.md`
- **Read next:** `.planning/PROJECT.md` → `.planning/ROADMAP.md` → `.planning/v1.38-MILESTONE-AUDIT.md`
