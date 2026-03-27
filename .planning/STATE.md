---
gsd_state_version: 1.0
milestone: v1.22
milestone_name: Maintainer Entry Contracts, Release Operations Closure & Contributor Routing
status: v1.22 milestone complete
last_updated: "2026-03-27T00:00:00Z"
progress:
  total_phases: 4
  completed_phases: 4
  total_plans: 12
  completed_plans: 12
---

# Project State

## Project Reference

See: `.planning/PROJECT.md`

**Current milestone:** `No active milestone route`
**Core value:** 把 `v1.22` archived baseline 与 `.planning/reviews/V1_22_EVIDENCE_INDEX.md` latest pull-only closeout pointer 作为下一轮协作与审查的唯一起点；不再把 contributor / maintainer / release contract 回退成隐性知识。
**Current mode:** `no active milestone route / latest archived baseline = v1.22`

## Current Position

- `v1.22` 已于 `2026-03-27` 完成 milestone audit、evidence-index closeout 与 archive promotion；当前仓库处于 archived-only route，默认下一步是 `$gsd-new-milestone`。
- latest archived baseline 固定为 `v1.22`；latest archived evidence index 继续是 `.planning/reviews/V1_22_EVIDENCE_INDEX.md`；`v1.21` 继续承担 previous archived baseline。
- `Phase 81`~`84` 已共同把 public-entry、release operations、community-health intake 与 milestone truth freeze 收口为单一 archived baseline；后续不得再回退成 undocumented maintainer folklore。

<!-- governance-route-contract:start -->
```yaml
contract_version: 1
contract_name: governance-route
active_milestone: null
latest_archived:
  version: v1.22
  name: Maintainer Entry Contracts, Release Operations Closure & Contributor Routing
  status: archived / evidence-ready (2026-03-27)
  phase: "84"
  phase_title: Governance/open-source guard coverage and milestone truth freeze
  phase_dir: 84-governance-open-source-guard-coverage-and-milestone-truth-freeze
  audit_path: .planning/v1.22-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_22_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.21
  name: Governance Bootstrap Truth Hardening & Planning Route Automation
  evidence_path: .planning/reviews/V1_21_EVIDENCE_INDEX.md
bootstrap:
  current_route: no active milestone route / latest archived baseline = v1.22
  default_next_command: $gsd-new-milestone
  latest_archived_evidence_pointer: .planning/reviews/V1_22_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->

## Latest Archived Baseline (v1.22)

- **Milestone:** `v1.22 Maintainer Entry Contracts, Release Operations Closure & Contributor Routing`
- **Phase range:** `81 -> 84`
- **Milestone status:** `archived / evidence-ready (2026-03-27)`
- **Milestone audit:** `.planning/v1.22-MILESTONE-AUDIT.md`
- **Evidence index:** `.planning/reviews/V1_22_EVIDENCE_INDEX.md`
- **Archived snapshots:** `.planning/milestones/v1.22-ROADMAP.md`, `.planning/milestones/v1.22-REQUIREMENTS.md`
- **Promoted closeout package:** `.planning/phases/81-contributor-onramp-route-convergence-and-public-entry-contract/{81-01-SUMMARY.md,81-02-SUMMARY.md,81-03-SUMMARY.md,81-SUMMARY.md,81-VERIFICATION.md,81-VALIDATION.md}`, `.planning/phases/82-release-operations-closure-and-evidence-chain-formalization/{82-01-SUMMARY.md,82-02-SUMMARY.md,82-03-SUMMARY.md,82-SUMMARY.md,82-VERIFICATION.md,82-VALIDATION.md}`, `.planning/phases/83-intake-templates-and-maintainer-stewardship-contract/{83-01-SUMMARY.md,83-02-SUMMARY.md,83-03-SUMMARY.md,83-SUMMARY.md,83-VERIFICATION.md,83-VALIDATION.md}`, `.planning/phases/84-governance-open-source-guard-coverage-and-milestone-truth-freeze/{84-01-SUMMARY.md,84-02-SUMMARY.md,84-03-SUMMARY.md,84-SUMMARY.md,84-VERIFICATION.md,84-VALIDATION.md}`

## Previous Archived Baseline (v1.21)

- **Milestone:** `v1.21 Governance Bootstrap Truth Hardening & Planning Route Automation`
- **Phase range:** `76 -> 80`
- **Milestone status:** `archived / evidence-ready (2026-03-26)`
- **Milestone audit:** `.planning/v1.21-MILESTONE-AUDIT.md`
- **Evidence index:** `.planning/reviews/V1_21_EVIDENCE_INDEX.md`
- **Archived snapshots:** `.planning/milestones/v1.21-ROADMAP.md`, `.planning/milestones/v1.21-REQUIREMENTS.md`
- **Promoted closeout package:** `.planning/phases/76-governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation/{76-01-SUMMARY.md,76-02-SUMMARY.md,76-03-SUMMARY.md,76-VERIFICATION.md,76-VALIDATION.md}`, `.planning/phases/77-governance-guard-topicization-bootstrap-smoke-coverage-and-literal-drift-reduction/{77-01-SUMMARY.md,77-02-SUMMARY.md,77-03-SUMMARY.md,77-VERIFICATION.md,77-VALIDATION.md}`, `.planning/phases/78-quality-gate-formalization-route-handoff-ergonomics-and-milestone-closeout-readiness/{78-01-SUMMARY.md,78-02-SUMMARY.md,78-03-SUMMARY.md,78-SUMMARY.md,78-VERIFICATION.md,78-VALIDATION.md}`, `.planning/phases/79-governance-tooling-hotspot-decomposition-and-release-contract-topicization/{79-01-SUMMARY.md,79-02-SUMMARY.md,79-03-SUMMARY.md,79-SUMMARY.md,79-VERIFICATION.md,79-VALIDATION.md}`, `.planning/phases/80-governance-typing-closure-and-final-meta-suite-hotspot-topicization/{80-01-SUMMARY.md,80-02-SUMMARY.md,80-03-SUMMARY.md,80-SUMMARY.md,80-VERIFICATION.md,80-VALIDATION.md}`

## Historical Archived Baseline (v1.20)

- **Milestone:** `v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement`
- **Phase range:** `72 -> 75`
- **Archive status:** `archived / evidence-ready (2026-03-25)`
- **Archive assets:** `.planning/v1.20-MILESTONE-AUDIT.md`, `.planning/reviews/V1_20_EVIDENCE_INDEX.md`, `.planning/milestones/v1.20-ROADMAP.md`, `.planning/milestones/v1.20-REQUIREMENTS.md`, `.planning/phases/72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement/{72-01-SUMMARY.md,72-02-SUMMARY.md,72-03-SUMMARY.md,72-04-SUMMARY.md,72-VERIFICATION.md,72-VALIDATION.md}`, `.planning/phases/73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization/{73-01-SUMMARY.md,73-02-SUMMARY.md,73-03-SUMMARY.md,73-04-SUMMARY.md,73-VERIFICATION.md,73-VALIDATION.md}`, `.planning/phases/74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout/{74-01-SUMMARY.md,74-02-SUMMARY.md,74-03-SUMMARY.md,74-04-SUMMARY.md,74-VERIFICATION.md,74-VALIDATION.md}`

## Recommended Next Command

1. `$gsd-new-milestone` —— 以 `v1.22` archived baseline 为起点开立下一轮 milestone
2. `$gsd-progress` —— 查看 archived-only route 与下一步路由状态
3. `uv run python scripts/check_file_matrix.py --check` —— 复核 planning / baseline / review / archive assets 契约
4. `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_promoted_phase_assets.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py tests/meta/test_governance_milestone_archives.py tests/meta/test_version_sync.py` —— 复核 archived-only route / release / intake / closeout 守卫

## Session Continuity

If resuming, read in this order:

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/PROJECT.md`
3. `.planning/ROADMAP.md`
4. `.planning/REQUIREMENTS.md`
5. `.planning/STATE.md`
6. `.planning/reviews/V1_22_EVIDENCE_INDEX.md`
7. `.planning/v1.22-MILESTONE-AUDIT.md`
8. `.planning/milestones/v1.22-ROADMAP.md`
9. `.planning/milestones/v1.22-REQUIREMENTS.md`
10. `.planning/reviews/V1_21_EVIDENCE_INDEX.md`
11. `.planning/v1.21-MILESTONE-AUDIT.md`
12. `.planning/milestones/v1.21-ROADMAP.md`
13. `.planning/milestones/v1.21-REQUIREMENTS.md`
14. `.planning/phases/84-governance-open-source-guard-coverage-and-milestone-truth-freeze/84-SUMMARY.md`
15. `.planning/phases/84-governance-open-source-guard-coverage-and-milestone-truth-freeze/84-VERIFICATION.md`
16. `.planning/phases/84-governance-open-source-guard-coverage-and-milestone-truth-freeze/84-VALIDATION.md`
17. `.planning/phases/83-intake-templates-and-maintainer-stewardship-contract/83-SUMMARY.md`
18. `.planning/phases/83-intake-templates-and-maintainer-stewardship-contract/83-VERIFICATION.md`
19. `.planning/phases/83-intake-templates-and-maintainer-stewardship-contract/83-VALIDATION.md`
20. `.planning/phases/82-release-operations-closure-and-evidence-chain-formalization/82-SUMMARY.md`
21. `.planning/phases/82-release-operations-closure-and-evidence-chain-formalization/82-VERIFICATION.md`
22. `.planning/phases/82-release-operations-closure-and-evidence-chain-formalization/82-VALIDATION.md`
23. `.planning/phases/81-contributor-onramp-route-convergence-and-public-entry-contract/81-SUMMARY.md`
24. `.planning/phases/81-contributor-onramp-route-convergence-and-public-entry-contract/81-VERIFICATION.md`
25. `.planning/phases/81-contributor-onramp-route-convergence-and-public-entry-contract/81-VALIDATION.md`

## Historical Continuity Anchors

`v1.1` 已完成全部计划执行：`15 phases / 58 plans` 全绿落表

- `Phase 17` 已完成：最终残留退役 / 类型契约收紧 / 里程碑收官。
- `Phase 24` 已完成并于 2026-03-17 重新验证。
- `Phase 46` 已于 `2026-03-20` 执行完成；follow-up route source = `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-REMEDIATION-ROADMAP.md`。
- `v1.21` archive anchors: `.planning/v1.21-MILESTONE-AUDIT.md`, `.planning/reviews/V1_21_EVIDENCE_INDEX.md`, `.planning/milestones/v1.21-ROADMAP.md`, `.planning/milestones/v1.21-REQUIREMENTS.md`
- `v1.20` archive anchors: `.planning/v1.20-MILESTONE-AUDIT.md`, `.planning/reviews/V1_20_EVIDENCE_INDEX.md`, `.planning/milestones/v1.20-ROADMAP.md`, `.planning/milestones/v1.20-REQUIREMENTS.md`
- `v1.19` archive anchors: `.planning/v1.19-MILESTONE-AUDIT.md`, `.planning/reviews/V1_19_EVIDENCE_INDEX.md`, `.planning/milestones/v1.19-ROADMAP.md`, `.planning/milestones/v1.19-REQUIREMENTS.md`
- `v1.16` archive anchors: `.planning/v1.16-MILESTONE-AUDIT.md`, `.planning/reviews/V1_16_EVIDENCE_INDEX.md`, `.planning/milestones/v1.16-ROADMAP.md`, `.planning/milestones/v1.16-REQUIREMENTS.md`
- `v1.13` archive anchors: `.planning/v1.13-MILESTONE-AUDIT.md`, `.planning/reviews/V1_13_EVIDENCE_INDEX.md`, `.planning/milestones/v1.13-ROADMAP.md`, `.planning/milestones/v1.13-REQUIREMENTS.md`
- `v1.6` archive anchors: `.planning/v1.6-MILESTONE-AUDIT.md`, `.planning/reviews/V1_6_EVIDENCE_INDEX.md`, `.planning/milestones/v1.6-ROADMAP.md`, `.planning/milestones/v1.6-REQUIREMENTS.md`
- `v1.5` archive anchors: `.planning/v1.5-MILESTONE-AUDIT.md`, `.planning/reviews/V1_5_EVIDENCE_INDEX.md`, `.planning/milestones/v1.5-ROADMAP.md`, `.planning/milestones/v1.5-REQUIREMENTS.md`

## Governance Truth Sources

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/PROJECT.md`
3. `.planning/ROADMAP.md`
4. `.planning/REQUIREMENTS.md`
5. `.planning/STATE.md`
6. `.planning/baseline/*.md` 与 `.planning/baseline/GOVERNANCE_REGISTRY.json`
7. `.planning/reviews/*.md`
8. `docs/developer_architecture.md`
9. `AGENTS.md`
10. `CLAUDE.md`（若使用 Claude Code）
11. 历史执行 / 审计 / 归档文档

## Phase Asset Promotion Contract

- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 是 `.planning/phases/**` 的显式 promoted allowlist。
- `Phase 72 / 73 / 74` 的 audited closeout bundles（`01..04-SUMMARY.md` + `VERIFICATION.md` + `VALIDATION.md`）现已正式提升为长期治理 / CI evidence。
- 未列入 allowlist 的 phase `PLAN / CONTEXT / RESEARCH / PRD` 与临时 closeout 文件默认保持执行痕迹身份；即使 `v1.20` 已归档，`Phase 75` 资产仍按 execution trace 处理，不作为长期治理 / CI 证据。
