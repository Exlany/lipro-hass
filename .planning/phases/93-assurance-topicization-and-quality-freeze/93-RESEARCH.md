# Phase 93: Assurance topicization and quality freeze - Research

**Researched:** 2026-03-28
**Confidence:** High

## Summary

- 当前失败不是架构根因未收敛，而是 **assurance / governance projections 没有跟上 Phase 92 的真实完成态**：route truth、testing counts、file-matrix header、verification header、focused guard literals 之间存在多处 textual drift。
- `tests_any_non_meta` 预算从 `156 -> 158` 不是新业务 debt，而是 diagnostics topicization 后 duplicated `Any` usage 带来的 incidental drift；应 burn down，而不是调高 guard 常量放过它。
- `ROADMAP.md` 的 `Phase 93` section 当前误写为 `Complete` 且引用 `Phase 92` closeout assets，这不是合法“预写”，而是 governance inconsistency；Phase 93 若要完成，必须生成真正的 `93-*` assets 并让 gsd-tools / tests/meta / docs 共同承认。

## Findings

### 1) FILE_MATRIX is structurally correct but numerically stale
- `scripts/check_file_matrix.py --check` 只报两类错误：header total mismatch 和 stale Python count。
- 差集校验表明 `FILE_MATRIX` 正文路径与仓库 inventory 完全一致；问题仅在 `**Python files total:** 692` 未刷新到当前 `705`。
- 这说明不需要重构 classifier registry；只需修复 derived total，并维持正文描述不漂。

### 2) TESTING.md is the main derived-doc hotspot
- `TESTING.md` 当前仍写旧统计：`372` Python / `293` runnable tests / `50` meta。
- 当前实际是 `386` Python files under `tests` / `306` runnable `test_*.py` / `51` meta / `5` integration / `4` snapshot / `4` benchmark / `5` fixture READMEs。
- `Phase 55` prose 仍写 `293`，触发 `public_surface_phase_notes.py`。

### 3) VERIFICATION_MATRIX header and route smoke lag behind Phase 92
- 顶部 current mutable story 仍是 `Phase 91 complete` + `$gsd-discuss-phase 92`。
- `Phase 92` section 已基本齐备，但 `tests/meta/test_phase92_redaction_convergence_guards.py` 没有以 **standalone full path** 出现，只在 brace expansion 中被包裹，导致 focused smoke guards 认为缺失。
- 这说明 verification truth 既要更新 header，也要显式写出 focused guard homes。

### 4) Route contract tests lag behind current governance truth
- `tests/meta/governance_current_truth.py` 已经是 `Phase 92 complete`，但 `tests/meta/governance_followup_route_current_milestones.py` 仍硬编码 `phase == 91`，属于测试自身滞后。
- 若 Phase 93 完成，route contract 还需要统一前推到 `Phase 93 complete / next = $gsd-complete-milestone v1.25`。

### 5) Typing drift is accidental and localized
- `tests/meta/test_phase31_runtime_budget_guards.py` 失败的 `158 vs 156` 来自 diagnostics topicization 后的 `Any`-bearing lines 增长。
- 最小 burn-down 可通过收紧 casts / annotations 完成，无需修改业务代码，也无需接受更高的 test-any budget。

## Recommended Execution Shape

### Plan 93-01
- 刷新 `FILE_MATRIX` / `TESTING` / `VERIFICATION_MATRIX` / route-contract docs / current-route guards，让当前 governance truth 先恢复一致。
- 同步把 `Phase 92` verification/validation 从 pending 改为 passed-ready 草稿。

### Plan 93-02
- 消除 diagnostics sibling suites 带来的 incidental `Any` 漂移。
- 为 `PUBLIC_SURFACES` / `DEPENDENCY_MATRIX` / `RESIDUAL_LEDGER` / `KILL_LIST` / `developer_architecture` 补写 Phase 93 assurance-freeze notes，并更新相关 meta guards。

### Plan 93-03
- 跑完整质量门：focused pytest、`tests/meta`、`check_file_matrix`、`ruff`、`mypy`。
- 生成 `93-01/02/03-SUMMARY.md`、`93-VERIFICATION.md`、`93-VALIDATION.md`，并把 current route 推进到 `Phase 93 complete` / milestone closeout-ready。

## Minimum Verification

- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta`
- `uv run pytest -q tests/services/test_services_diagnostics.py tests/services/test_services_diagnostics_support.py tests/services/test_services_diagnostics_feedback.py tests/services/test_services_diagnostics_capabilities.py tests/services/test_services_diagnostics_payloads.py`
- `uv run ruff check .`
- `uv run mypy`
