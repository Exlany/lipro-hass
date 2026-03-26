---
gsd_state_version: 1.0
milestone: v1.21
milestone_name: Governance Bootstrap Truth Hardening & Planning Route Automation
status: active
last_updated: "2026-03-26T00:00:00Z"
progress:
  total_phases: 5
  completed_phases: 5
  total_plans: 15
  completed_plans: 15
---

# Project State

## Project Reference

See: `.planning/PROJECT.md`

**Current milestone:** `v1.21 Governance Bootstrap Truth Hardening & Planning Route Automation`
**Core value:** 以 `v1.20` archived baseline 与 `.planning/reviews/V1_20_EVIDENCE_INDEX.md` latest archived evidence index 作为 active route 的稳定 seed，把 `v1.21` 的 current route 前推到 `Phase 80 complete`，并把默认下一步固定到 `$gsd-complete-milestone v1.21`。
**Current mode:** `Phase 80 complete`

## Current Position

- `v1.21` 已于 `2026-03-26` 完成 `Phase 76 -> 80` 全部执行；当前里程碑已进入 `closeout-ready`，下一步是 `$gsd-complete-milestone v1.21`。
- latest archived baseline 固定为 `v1.20`；latest archived evidence index 继续是 `.planning/reviews/V1_20_EVIDENCE_INDEX.md`；`v1.19` 继续承担 previous archived baseline。
- recent bootstrap drift、typing regressions 与 final meta-suite hotspots 已被 machine-readable contract、focused smoke、topicized governance suites、verification matrix、file-matrix registry 与 review ledgers 共同冻结；后续 archive promotion 不再需要补 current-story handoff。

## Current Milestone (v1.21)

- **Milestone:** `v1.21 Governance Bootstrap Truth Hardening & Planning Route Automation`
- **Phase range:** `76 -> 80`
- **Milestone status:** `closeout-ready (2026-03-26)`
- **Seed input:** `.planning/v1.20-MILESTONE-AUDIT.md`, `.planning/reviews/V1_20_EVIDENCE_INDEX.md`, `.planning/MILESTONES.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `tests/meta/governance_current_truth.py`, `tests/meta/test_governance_milestone_archives.py`
- **Default next command:** `$gsd-complete-milestone v1.21`

<!-- governance-route-contract:start -->
```yaml
contract_version: 1
contract_name: governance-route
active_milestone:
  version: v1.21
  name: Governance Bootstrap Truth Hardening & Planning Route Automation
  status: closeout-ready (2026-03-26)
  phase: "80"
  phase_title: Governance typing closure and final meta-suite hotspot topicization
  route_mode: Phase 80 complete
latest_archived:
  version: v1.20
  name: Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement
  status: archived / evidence-ready (2026-03-25)
  phase: "75"
  phase_title: Access-mode truth closure, evidence promotion formalization, and thin-adapter typing hardening
  phase_dir: 75-access-mode-truth-closure-evidence-promotion-formalization-and-thin-adapter-typing-hardening
  audit_path: .planning/v1.20-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_20_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.19
  name: Audit-Driven Final Hotspot Decomposition & Governance Truth Projection
  evidence_path: .planning/reviews/V1_19_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.21 active route / Phase 80 complete / latest archived baseline = v1.20
  default_next_command: $gsd-complete-milestone v1.21
  latest_archived_evidence_pointer: .planning/reviews/V1_20_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->

## Latest Archived Baseline (v1.20)

- **Milestone:** `v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement`
- **Phase range:** `72 -> 75`
- **Milestone status:** `archived / evidence-ready (2026-03-25)`
- **Route seed:** `.planning/reviews/V1_19_TERMINAL_AUDIT.md`
- **Starting baseline:** `.planning/v1.19-MILESTONE-AUDIT.md`, `.planning/reviews/V1_19_EVIDENCE_INDEX.md`, `.planning/milestones/v1.19-ROADMAP.md`, `.planning/milestones/v1.19-REQUIREMENTS.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-SUMMARY.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VERIFICATION.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VALIDATION.md`
- **Milestone audit:** `.planning/v1.20-MILESTONE-AUDIT.md`
- **Evidence index:** `.planning/reviews/V1_20_EVIDENCE_INDEX.md`
- **Archived snapshots:** `.planning/milestones/v1.20-ROADMAP.md`, `.planning/milestones/v1.20-REQUIREMENTS.md`

## Previous Archived Baseline (v1.19)

- **Milestone:** `v1.19 Audit-Driven Final Hotspot Decomposition & Governance Truth Projection`
- **Phase range:** `71`
- **Archive status:** `archived / evidence-ready (2026-03-25)`
- **Archive assets:** `.planning/v1.19-MILESTONE-AUDIT.md`, `.planning/reviews/V1_19_EVIDENCE_INDEX.md`, `.planning/milestones/v1.19-ROADMAP.md`, `.planning/milestones/v1.19-REQUIREMENTS.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-SUMMARY.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VERIFICATION.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VALIDATION.md`

## Historical Archived Baseline (v1.18)

- **Milestone:** `v1.18 Support-Seam Slimming, OTA Resolver Consolidation & Governance Test Topicization`
- **Phase range:** `70`
- **Archive status:** `archived / evidence-ready (2026-03-24)`
- **Archive assets:** `.planning/v1.18-MILESTONE-AUDIT.md`, `.planning/reviews/V1_18_EVIDENCE_INDEX.md`, `.planning/milestones/v1.18-ROADMAP.md`, `.planning/milestones/v1.18-REQUIREMENTS.md`, `.planning/phases/70-support-seam-slimming-ota-resolver-consolidation-and-governance-test-topicization/70-SUMMARY.md`, `.planning/phases/70-support-seam-slimming-ota-resolver-consolidation-and-governance-test-topicization/70-VERIFICATION.md`, `.planning/phases/70-support-seam-slimming-ota-resolver-consolidation-and-governance-test-topicization/70-VALIDATION.md`

## Recommended Next Command

1. `$gsd-complete-milestone v1.21` —— 执行当前 closeout-ready route 的 milestone audit / archive closeout
2. `$gsd-next` —— 让 GSD 自动前推到当前里程碑的正式收官动作
3. `$gsd-progress` —— 查看 current route / latest archived baseline / next command 是否保持一致
4. `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress` —— 复核 fast-path 是否只承认 `Phase 80 complete`
5. `uv run python scripts/check_file_matrix.py --check` —— 复核 planning / baseline / review / promoted-asset 契约
6. `uv run pytest -q tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py tests/meta/governance_followup_route_current_milestones.py` —— 复核 closeout-ready / fast-path / matrix drift guards

## Session Continuity

If resuming, read in this order:

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/PROJECT.md`
3. `.planning/ROADMAP.md`
4. `.planning/REQUIREMENTS.md`
5. `.planning/STATE.md`
6. `.planning/reviews/V1_20_EVIDENCE_INDEX.md`
7. `.planning/v1.20-MILESTONE-AUDIT.md`
8. `.planning/milestones/v1.20-ROADMAP.md`
9. `.planning/milestones/v1.20-REQUIREMENTS.md`
10. `.planning/reviews/V1_19_TERMINAL_AUDIT.md`
11. `.planning/reviews/V1_19_EVIDENCE_INDEX.md`
12. `.planning/milestones/v1.19-REQUIREMENTS.md`
13. `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-SUMMARY.md`
14. `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VERIFICATION.md`
15. `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VALIDATION.md`
16. `.planning/v1.18-MILESTONE-AUDIT.md`
17. `.planning/reviews/V1_18_EVIDENCE_INDEX.md`

## Historical Continuity Anchors

`v1.1` 已完成全部计划执行：`15 phases / 58 plans` 全绿落表

- `Phase 17` 已完成：最终残留退役 / 类型契约收紧 / 里程碑收官。
- `Phase 24` 已完成并于 2026-03-17 重新验证。
- `Phase 46` 已于 `2026-03-20` 执行完成；follow-up route source = `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-REMEDIATION-ROADMAP.md`。
- `v1.13` archive anchors: `.planning/v1.13-MILESTONE-AUDIT.md`, `.planning/reviews/V1_13_EVIDENCE_INDEX.md`, `.planning/milestones/v1.13-ROADMAP.md`, `.planning/milestones/v1.13-REQUIREMENTS.md`
- `v1.12` archive anchors: `.planning/v1.12-MILESTONE-AUDIT.md`, `.planning/reviews/V1_12_EVIDENCE_INDEX.md`, `.planning/milestones/v1.12-ROADMAP.md`, `.planning/milestones/v1.12-REQUIREMENTS.md`
- `v1.20` archive anchors: `.planning/v1.20-MILESTONE-AUDIT.md`, `.planning/reviews/V1_20_EVIDENCE_INDEX.md`, `.planning/milestones/v1.20-ROADMAP.md`, `.planning/milestones/v1.20-REQUIREMENTS.md`
- `v1.19` archive anchors: `.planning/v1.19-MILESTONE-AUDIT.md`, `.planning/reviews/V1_19_EVIDENCE_INDEX.md`, `.planning/milestones/v1.19-ROADMAP.md`, `.planning/milestones/v1.19-REQUIREMENTS.md`
- `v1.16` archive anchors: `.planning/v1.16-MILESTONE-AUDIT.md`, `.planning/reviews/V1_16_EVIDENCE_INDEX.md`, `.planning/milestones/v1.16-ROADMAP.md`, `.planning/milestones/v1.16-REQUIREMENTS.md`
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
