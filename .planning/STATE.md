---
gsd_state_version: 1.0
milestone: v1.22
milestone_name: Maintainer Entry Contracts, Release Operations Closure & Contributor Routing
status: active
last_updated: "2026-03-27T00:00:00Z"
progress:
  total_phases: 4
  completed_phases: 1
  total_plans: 12
  completed_plans: 3
---

# Project State

## Project Reference

See: `.planning/PROJECT.md`

**Current milestone:** `v1.22 Maintainer Entry Contracts, Release Operations Closure & Contributor Routing`
**Core value:** 把 `v1.21` archived baseline 与 `.planning/reviews/V1_21_EVIDENCE_INDEX.md` latest pull-only closeout pointer 外化为 maintainer / contributor / release 的单一协作路线；不再把下一轮增量浪费在重开内部治理第二故事线。
**Current mode:** `Phase 81 complete`

## Current Position

- `v1.22` 已于 `2026-03-27` 从 `v1.21` archived baseline 正式开立；`Phase 81` 现已完成 contributor-route convergence 与 architecture change-map 冻结，下一步是 `$gsd-discuss-phase 82`。
- latest archived baseline 固定为 `v1.21`；latest archived evidence index 继续是 `.planning/reviews/V1_21_EVIDENCE_INDEX.md`；`v1.20` 继续承担 previous archived baseline。
- 当前最高价值工作集中在 contributor / maintainer first-hop、release evidence chain、intake templates 与 ownership / triage contract，不再重开 production runtime hotspot surgery。

<!-- governance-route-contract:start -->
```yaml
contract_version: 1
contract_name: governance-route
active_milestone:
  version: v1.22
  name: Maintainer Entry Contracts, Release Operations Closure & Contributor Routing
  status: Phase 81 complete (2026-03-27)
  phase: "81"
  phase_title: Contributor onramp route convergence and public entry contract
  route_mode: Phase 81 complete
latest_archived:
  version: v1.21
  name: Governance Bootstrap Truth Hardening & Planning Route Automation
  status: archived / evidence-ready (2026-03-26)
  phase: "80"
  phase_title: Governance typing closure and final meta-suite hotspot topicization
  phase_dir: 80-governance-typing-closure-and-final-meta-suite-hotspot-topicization
  audit_path: .planning/v1.21-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_21_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.20
  name: Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement
  evidence_path: .planning/reviews/V1_20_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.22 active route / Phase 81 complete / latest archived baseline = v1.21
  default_next_command: $gsd-discuss-phase 82
  latest_archived_evidence_pointer: .planning/reviews/V1_21_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->

## Latest Archived Baseline (v1.21)

- **Milestone:** `v1.21 Governance Bootstrap Truth Hardening & Planning Route Automation`
- **Phase range:** `76 -> 80`
- **Milestone status:** `archived / evidence-ready (2026-03-26)`
- **Milestone audit:** `.planning/v1.21-MILESTONE-AUDIT.md`
- **Evidence index:** `.planning/reviews/V1_21_EVIDENCE_INDEX.md`
- **Archived snapshots:** `.planning/milestones/v1.21-ROADMAP.md`, `.planning/milestones/v1.21-REQUIREMENTS.md`
- **Promoted closeout package:** `.planning/phases/76-governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation/{76-01-SUMMARY.md,76-02-SUMMARY.md,76-03-SUMMARY.md,76-VERIFICATION.md,76-VALIDATION.md}`, `.planning/phases/77-governance-guard-topicization-bootstrap-smoke-coverage-and-literal-drift-reduction/{77-01-SUMMARY.md,77-02-SUMMARY.md,77-03-SUMMARY.md,77-VERIFICATION.md,77-VALIDATION.md}`, `.planning/phases/78-quality-gate-formalization-route-handoff-ergonomics-and-milestone-closeout-readiness/{78-01-SUMMARY.md,78-02-SUMMARY.md,78-03-SUMMARY.md,78-SUMMARY.md,78-VERIFICATION.md,78-VALIDATION.md}`, `.planning/phases/79-governance-tooling-hotspot-decomposition-and-release-contract-topicization/{79-01-SUMMARY.md,79-02-SUMMARY.md,79-03-SUMMARY.md,79-SUMMARY.md,79-VERIFICATION.md,79-VALIDATION.md}`, `.planning/phases/80-governance-typing-closure-and-final-meta-suite-hotspot-topicization/{80-01-SUMMARY.md,80-02-SUMMARY.md,80-03-SUMMARY.md,80-SUMMARY.md,80-VERIFICATION.md,80-VALIDATION.md}`

## Previous Archived Baseline (v1.20)

- **Milestone:** `v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement`
- **Phase range:** `72 -> 75`
- **Archive status:** `archived / evidence-ready (2026-03-25)`
- **Archive assets:** .planning/v1.20-MILESTONE-AUDIT.md, .planning/reviews/V1_20_EVIDENCE_INDEX.md, .planning/milestones/v1.20-ROADMAP.md, .planning/milestones/v1.20-REQUIREMENTS.md, .planning/phases/72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement/{72-01-SUMMARY.md,72-02-SUMMARY.md,72-03-SUMMARY.md,72-04-SUMMARY.md,72-VERIFICATION.md,72-VALIDATION.md}, .planning/phases/73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization/{73-01-SUMMARY.md,73-02-SUMMARY.md,73-03-SUMMARY.md,73-04-SUMMARY.md,73-VERIFICATION.md,73-VALIDATION.md}, .planning/phases/74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout/{74-01-SUMMARY.md,74-02-SUMMARY.md,74-03-SUMMARY.md,74-04-SUMMARY.md,74-VERIFICATION.md,74-VALIDATION.md}

## Historical Archived Baseline (v1.19)

- **Milestone:** `v1.19 Audit-Driven Final Hotspot Decomposition & Governance Truth Projection`
- **Phase range:** `71`
- **Archive status:** `archived / evidence-ready (2026-03-25)`
- **Archive assets:** `.planning/v1.19-MILESTONE-AUDIT.md`, `.planning/reviews/V1_19_EVIDENCE_INDEX.md`, `.planning/milestones/v1.19-ROADMAP.md`, `.planning/milestones/v1.19-REQUIREMENTS.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/{71-SUMMARY.md,71-VERIFICATION.md,71-VALIDATION.md}`

## Recommended Next Command

1. `$gsd-discuss-phase 82` —— 为 `Phase 81` 收集上下文、界定 public entry / architecture change-map / docs route 的精确边界
2. `$gsd-plan-phase 81` —— 若无需讨论，直接把 `Phase 81` 细化成可执行计划
3. `$gsd-progress` —— 查看 `v1.22 active route / Phase 81 complete / latest archived baseline = v1.21` 的当前状态
4. `uv run python scripts/check_file_matrix.py --check` —— 复核 planning / baseline / review / archive assets 契约
5. `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py tests/meta/test_version_sync.py` —— 复核 active route / public entry / release continuity 守卫

## Session Continuity

If resuming, read in this order:

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/PROJECT.md`
3. `.planning/ROADMAP.md`
4. `.planning/REQUIREMENTS.md`
5. `.planning/STATE.md`
6. `.planning/reviews/V1_21_EVIDENCE_INDEX.md`
7. `.planning/v1.21-MILESTONE-AUDIT.md`
8. `.planning/milestones/v1.21-ROADMAP.md`
9. `.planning/milestones/v1.21-REQUIREMENTS.md`
10. `.planning/reviews/V1_20_EVIDENCE_INDEX.md`
11. `.planning/v1.20-MILESTONE-AUDIT.md`
12. `.planning/milestones/v1.20-ROADMAP.md`
13. `.planning/milestones/v1.20-REQUIREMENTS.md`
14. `.planning/reviews/V1_19_TERMINAL_AUDIT.md`
15. `.planning/reviews/V1_19_EVIDENCE_INDEX.md`
16. `.planning/milestones/v1.19-REQUIREMENTS.md`
17. `.planning/phases/81-contributor-onramp-route-convergence-and-public-entry-contract/81-SUMMARY.md`
18. `.planning/phases/81-contributor-onramp-route-convergence-and-public-entry-contract/81-VERIFICATION.md`
19. `.planning/phases/81-contributor-onramp-route-convergence-and-public-entry-contract/81-VALIDATION.md`
20. `.planning/phases/80-governance-typing-closure-and-final-meta-suite-hotspot-topicization/80-SUMMARY.md`
21. `.planning/phases/80-governance-typing-closure-and-final-meta-suite-hotspot-topicization/80-VERIFICATION.md`
22. `.planning/phases/80-governance-typing-closure-and-final-meta-suite-hotspot-topicization/80-VALIDATION.md`

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


## Recommended Next Command

1. `$gsd-discuss-phase 82` —— 为 `Phase 81` 收集上下文、界定 public entry / architecture change-map / docs route 的精确边界
2. `$gsd-plan-phase 81` —— 若无需讨论，直接把 `Phase 81` 细化成可执行计划
3. `$gsd-progress` —— 查看 `v1.22 active route / Phase 81 complete / latest archived baseline = v1.21` 的当前状态
4. `uv run python scripts/check_file_matrix.py --check` —— 复核 planning / baseline / review / archive assets 契约
5. `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py tests/meta/test_version_sync.py` —— 复核 active route / public entry / release continuity 守卫

## Session Continuity

If resuming, read in this order:

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/PROJECT.md`
3. `.planning/ROADMAP.md`
4. `.planning/REQUIREMENTS.md`
5. `.planning/STATE.md`
6. `.planning/reviews/V1_21_EVIDENCE_INDEX.md`
7. `.planning/v1.21-MILESTONE-AUDIT.md`
8. `.planning/milestones/v1.21-ROADMAP.md`
9. `.planning/milestones/v1.21-REQUIREMENTS.md`
10. `.planning/reviews/V1_20_EVIDENCE_INDEX.md`
11. `.planning/v1.20-MILESTONE-AUDIT.md`
12. `.planning/milestones/v1.20-ROADMAP.md`
13. `.planning/milestones/v1.20-REQUIREMENTS.md`
14. `.planning/reviews/V1_19_TERMINAL_AUDIT.md`
15. `.planning/reviews/V1_19_EVIDENCE_INDEX.md`
16. `.planning/milestones/v1.19-REQUIREMENTS.md`
17. `.planning/phases/81-contributor-onramp-route-convergence-and-public-entry-contract/81-SUMMARY.md`
18. `.planning/phases/81-contributor-onramp-route-convergence-and-public-entry-contract/81-VERIFICATION.md`
19. `.planning/phases/81-contributor-onramp-route-convergence-and-public-entry-contract/81-VALIDATION.md`
20. `.planning/phases/80-governance-typing-closure-and-final-meta-suite-hotspot-topicization/80-SUMMARY.md`
21. `.planning/phases/80-governance-typing-closure-and-final-meta-suite-hotspot-topicization/80-VERIFICATION.md`
22. `.planning/phases/80-governance-typing-closure-and-final-meta-suite-hotspot-topicization/80-VALIDATION.md`

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
