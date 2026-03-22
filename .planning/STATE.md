---
gsd_state_version: 1.0
milestone: v1.13
milestone_name: Tooling Truth Decomposition, Formal-Home Slimming & Naming/Discoverability Convergence
status: active
last_updated: "2026-03-22T00:00:00Z"
progress:
  total_phases: 3
  completed_phases: 1
  total_plans: 3
  completed_plans: 3
---

# Project State

## Project Reference

See: `.planning/PROJECT.md`

**Current milestone:** `v1.13 Tooling Truth Decomposition, Formal-Home Slimming & Naming/Discoverability Convergence`
**Core value:** 以 `v1.12` 已归档的 localized verification baseline 为低噪声起点，继续 inward decomposition tooling truth、large-but-correct formal homes 与 naming/discoverability friction，而不重开第二主链。
**Current mode:** `Phase 60 complete`；`v1.12` 已 archive-ready，`v1.10` / `v1.11` 仍保留为 refreshed route 历史 seed，而 `v1.6` 继续承担 latest shipped archive baseline。

## Current Position

- `v1.13` 已于 `2026-03-22` 完成 `Phase 60`：`scripts/check_file_matrix.py` 已收敛成 thin checker root 并 outward 保留 CLI/import contract，`tests/meta/test_toolchain_truth.py` 已收敛成 thin daily root + `6` 个 truth-family modules，`FILE_MATRIX / VERIFICATION_MATRIX / TESTING / current-story docs` 也已冻结同一条 tooling no-growth story；下一步是规划 `$gsd-plan-phase 61`。
- `v1.12` 已于 `2026-03-22` 完成 archive-ready closeout：`.planning/v1.12-MILESTONE-AUDIT.md`、`.planning/reviews/V1_12_EVIDENCE_INDEX.md`、`.planning/milestones/v1.12-ROADMAP.md` 与 `.planning/milestones/v1.12-REQUIREMENTS.md` 已落盘；`59-SUMMARY.md` / `59-VERIFICATION.md` 继续作为 promoted closeout evidence。
- `v1.11` 已于 `2026-03-22` 完成 opening `Phase 58`：refreshed architecture/code audit、governance/open-source audit、`Phase 59+` remediation roadmap 与 current-story truth freeze 均已落盘；它继续作为 `v1.12 -> v1.13` 的 refreshed route baseline。
- `v1.10` 已于 `2026-03-22` 完成 opening `Phase 57`：typed command-result state / reason-code truth 已与 runtime sender、diagnostics query consumer 与 governance truth 对齐；当前保持 prior closeout-ready milestone 身份。
- `v1.9` 已于 `2026-03-22` 完成 opening `Phase 56`：generic exponential backoff primitive 已迁往 neutral helper home，并关闭 `Generic backoff helper leak` residual。
- `v1.8` 已于 `2026-03-21` 完成 `Phase 51 -> 55` closeout：continuity drill、registry projection、verify-only release rehearsal、formal-root sustainment、helper-hotspot formalization 与 mega-test/typing truth freeze 均已形成 promoted evidence。
- `v1.7` 已于 `2026-03-21` 完成 closeout：`Phase 46` audit package 与 `Phase 47 -> 50` promoted closeout evidence 继续构成 post-archive follow-up truth，但不再是 active milestone。
- `v1.6` 已完成 milestone audit、archive promotion 与 closeout evidence registration：`.planning/v1.6-MILESTONE-AUDIT.md`、`.planning/reviews/V1_6_EVIDENCE_INDEX.md`、`.planning/milestones/v1.6-ROADMAP.md` 与 `.planning/milestones/v1.6-REQUIREMENTS.md` 继续作为最新 shipped archive baseline。
- `v1.5` 仍保留为上一个 shipped archive baseline：`.planning/v1.5-MILESTONE-AUDIT.md`、`.planning/reviews/V1_5_EVIDENCE_INDEX.md` 与 `.planning/milestones/v1.5-*.md` 继续承担历史追溯 / continuity 身份，不再充当 latest pointer。
- `Phase 24` 已完成并于 2026-03-17 重新验证：host-neutral nucleus -> headless proof -> remaining-family completion -> replay / observability / governance / milestone closeout 全链条在 fresh gates 下再次收官。
- `Phase 46` 已于 `2026-03-20` 执行完成：file-level inventory、architecture/code audit、docs/toolchain/governance audit、master audit、score matrix、`46-REMEDIATION-ROADMAP.md`、summary 与 verification 均已落盘。
- `v1.1` 已完成全部计划执行：`15 phases / 58 plans` 全绿落表。
- `Phase 17` 已完成：final residual retirement、typed-contract tightening、governance closeout 与 final repo audit 均已形成稳定历史真相。

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
- 未列入 allowlist 的 phase `PLAN / CONTEXT / RESEARCH / PRD` 与临时 closeout 文件默认保持执行痕迹身份，不作为长期治理 / CI 证据。

## Current Milestone Status

- **Milestone:** `v1.13 Tooling Truth Decomposition, Formal-Home Slimming & Naming/Discoverability Convergence`
- **Phase range:** `60 -> 62`
- **Completed so far:** `milestone opened; Phase 60 completed (3/3 plans)`
- **Planned next:** `$gsd-plan-phase 61`（规划 formal-home slimming 的下一相位）
- **Starting baseline:** `.planning/v1.12-MILESTONE-AUDIT.md`, `.planning/reviews/V1_12_EVIDENCE_INDEX.md`, `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-REMEDIATION-ROADMAP.md`, `.planning/phases/59-verification-localization-and-governance-guard-topicization/59-SUMMARY.md`, `.planning/phases/59-verification-localization-and-governance-guard-topicization/59-VERIFICATION.md`
- **Historical archives:** `.planning/milestones/v1.1-ROADMAP.md`, `.planning/milestones/v1.1-REQUIREMENTS.md`, `.planning/milestones/v1.2-ROADMAP.md`, `.planning/milestones/v1.2-REQUIREMENTS.md`, `.planning/milestones/v1.4-ROADMAP.md`, `.planning/milestones/v1.4-REQUIREMENTS.md`, `.planning/milestones/v1.5-ROADMAP.md`, `.planning/milestones/v1.5-REQUIREMENTS.md`, `.planning/milestones/v1.6-ROADMAP.md`, `.planning/milestones/v1.6-REQUIREMENTS.md`, `.planning/milestones/v1.12-ROADMAP.md`, `.planning/milestones/v1.12-REQUIREMENTS.md`
- **Next focus:** `$gsd-plan-phase 61`——在已冻结的 tooling baseline 上规划 production formal-home slimming。

## Recommended Next Command

1. `$gsd-plan-phase 61` —— 规划 `anonymous_share` / diagnostics API / OTA candidate / `select` 的 formal-home slimming
2. `uv run python scripts/check_file_matrix.py --check` —— 复核 file-governance baseline 与 inventory truth
3. `uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py` —— 复核 toolchain / governance focused baseline
4. `$gsd-progress` —— 查看 `v1.13` 当前执行位置与 `Phase 61/62` 后续 route anchors

## Session Continuity

If resuming, read in this order:
1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/PROJECT.md`
3. `.planning/ROADMAP.md`
4. `.planning/REQUIREMENTS.md`
5. `.planning/STATE.md`
6. `.planning/v1.12-MILESTONE-AUDIT.md`
7. `.planning/reviews/V1_12_EVIDENCE_INDEX.md`
8. `.planning/milestones/v1.12-ROADMAP.md`
9. `.planning/milestones/v1.12-REQUIREMENTS.md`
10. `.planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/60-SUMMARY.md`
11. `.planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/60-VERIFICATION.md`
12. `.planning/phases/59-verification-localization-and-governance-guard-topicization/59-SUMMARY.md`
13. `.planning/phases/59-verification-localization-and-governance-guard-topicization/59-VERIFICATION.md`
14. `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-REMEDIATION-ROADMAP.md`
15. `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-SUMMARY.md`
16. `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-VERIFICATION.md`
