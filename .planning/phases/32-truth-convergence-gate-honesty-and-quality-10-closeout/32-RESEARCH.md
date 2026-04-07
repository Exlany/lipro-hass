# Phase 32 Research

**Status:** `research complete`
**Date:** `2026-03-17`
**Requirement:** `GOV-24`, `QLT-05`, `GOV-25`, `GOV-26`, `HOT-07`, `TST-04`, `TYP-08`, `ERR-06`, `RES-06`

## Executive Judgment

`Phase 32` 最优仍是 `5 plans / 4 waves`，而不是继续塞回一个“最终杂项 cleanup 巨相”。原因很直接：planning truth、gate honesty、release/docs governance、derived-map freshness 与 hotspot/typed/exception/residue follow-through 分属不同风险模型；若再混成一个 tranche，会重新制造 silent defer。

## Current Truth-Gap Snapshot

### 1. planning truth / traceability 漂移已经是 active debt

- `.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md` 当前仍残留“`25 -> 31` 已 closeout-ready”的叙事，与最新终审要追加 `Phase 32` 的现实冲突。
- `Seed Coverage` 仍停留在旧数值，且没有把 `Phase 32` 需要承接的 cross-cutting debt 正式入账。
- `v1.3-HANDOFF.md` 与 `v1.3-MILESTONE-AUDIT.md` 应保留历史身份，但必须被 active truth 显式 supersede，而不是继续默认等于 current state。

### 2. repo-wide gate honesty 是最容易再次漂移的质量债

- `uv run ruff check .` 可以被当场验证并已重新修绿，但 repo-wide `mypy` / CI / docs / runbook 是否讲同一条故事，仍需要统一裁决。
- 问题不只是在“工具是否通过”，更在于“仓库是否诚实表达哪些工具是 blocking gate、哪些只是 target truth、哪些仍在执行态待收口”。
- `QLT-05` 必须优先锁清口径，否则后续 docs 与 guards 会再次分叉。

### 3. release identity / maintainer continuity / templates 仍有接缝

- release posture 已显著强化，但 signing、attestation、provenance、code scanning 的对外叙事仍容易产生概念漂移。
- 仓库已经诚实表达 single-maintainer reality，但 maintainer continuity、release custody、security backup / escalation 与 contributor templates 仍需更一致的制度化表达。
- 这类 debt 若不再统一，很容易在 README / README_zh / CONTRIBUTING / PR template / runbook 间再次飘散。

### 4. `.planning/codebase/*` 与双语 public docs 需要 freshness / disclaimer 收口

- `.planning/codebase/*.md` 目前已被裁决为 derived collaboration maps，但 freshness、authority boundary、与 active truth 的同步责任还不够机器化。
- `docs/developer_architecture.md`、`README.md`、`README_zh.md` 等 public/docs surfaces 也仍可能滞留旧 phase 叙事或缺失 bilingual convergence discipline。
- 这部分应单独成 wave，而不是顺手在 hotspot cleanup 时“带过”。

### 5. hotspot / tests / typed / exception / residue 仍需最终 follow-through

- `Coordinator`、`LiproRestFacade`、`LiproProtocolFacade` 与 `scripts/check_file_matrix.py` 一类热点依旧值得继续切薄。
- mega-tests（如 `tests/core/api/test_api.py`、`tests/core/test_init.py`、`tests/meta/test_governance_guards.py`）仍有专题化拆分空间。
- `TYP-08` / `ERR-06` / `RES-06` 的关键不是“归零幻想”，而是从 no-growth 进一步推进 measurable burn-down 或 explicit defer truth。

## Recommended Plan Structure

### Plan 32-01 — planning truth convergence and requirement traceability repair

**Primary focus:**
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `tests/meta/test_governance_closeout_guards.py`

### Plan 32-02 — repo-wide gate honesty and toolchain reality alignment

**Primary focus:**
- `.github/workflows/ci.yml`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `CONTRIBUTING.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `tests/meta/test_toolchain_truth.py`

### Plan 32-03 — release identity posture, maintainer continuity, and docs-template convergence

**Primary focus:**
- `.github/workflows/release.yml`
- `.github/CODEOWNERS`
- `.github/pull_request_template.md`
- `README.md`
- `README_zh.md`
- `SUPPORT.md`
- `SECURITY.md`
- `CONTRIBUTING.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`

### Plan 32-04 — codebase-map freshness, authority disclaimers, and bilingual public-doc sync

**Primary focus:**
- `.planning/codebase/STACK.md`
- `.planning/codebase/STRUCTURE.md`
- `.planning/codebase/INTEGRATIONS.md`
- `.planning/codebase/TESTING.md`
- `docs/developer_architecture.md`
- `docs/README.md`
- `README.md`
- `README_zh.md`

### Plan 32-05 — hotspot slimming, mega-test topicization, typed/exception burn-down, and residual honesty closeout

**Primary focus:**
- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/runtime_types.py`
- `custom_components/lipro/core/command/dispatch.py`
- `tests/core/api/test_api.py`
- `tests/core/test_init.py`
- `tests/meta/test_governance_guards.py`
- `scripts/check_file_matrix.py`

## Validation Architecture

- quick gate 必须至少包含：`uv run ruff check .` + governance smoke suites。
- full phase gate 必须包含：`uv run ruff check .`、`uv run mypy`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run python scripts/check_translations.py`、relevant meta guards。
- `repo-wide mypy` 若在 execution 中仍无法 repo-wide 通过，必须把 docs / CI / runbook / verification matrix 的口径显式收窄并机器化说明；不能继续保留假 repo-wide green story。

## High-Risk Truths To Lock

- `Phase 32` 是 active current route，不是“也许以后再做”的附注。
- `v1.3-HANDOFF.md` 与 `v1.3-MILESTONE-AUDIT.md` 是历史 closeout baseline，不应继续被误读为当前活跃 planning 真源。
- `MD5` 登录路径继续按协议约束记录，不得在 `Phase 32` 中被重新误报为仓库可独立消灭的弱密码学债。
- `.planning/codebase/*.md` 必须带 freshness / disclaimer / authority-boundary truth；否则派生图谱会再次挤占真源位置。
- hotspot cleanup 仍不得引入第二 root / 第二 release story / 第二治理大对象。
