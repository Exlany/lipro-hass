# Phase 68 PRD — Master Audit Follow-Through, Hotspot Finalization & Docs Contract Hardening

**Created:** 2026-03-24
**Source:** refreshed repo-wide audit + cross-surface manual review
**Status:** ready for `$gsd-plan-phase`

## Goal

在不重开第二条正式主链的前提下，把本轮终极审阅确认仍然存在的剩余问题统一收口：

1. 继续 inward decompose production hotspots，降低 decision density、局部 compat/cycle/alias 残留与维护噪音。
2. 把 `README* / manifest / pyproject / CHANGELOG / .github/* / docs` 的 first-hop、version、release-example 与 docs navigation 收口到同一 current truth。
3. 强制通过 `$gsd-review` 把 plan 做 cross-AI peer review，再将 review 结论显式回灌到执行计划，不让“审阅意见”继续停留在口头层。

## In Scope

### A. Production hotspots

- `custom_components/lipro/core/telemetry/models.py`
- `custom_components/lipro/core/mqtt/message_processor.py`
- `custom_components/lipro/core/anonymous_share/share_client_flows.py`
- `custom_components/lipro/core/api/diagnostics_api_ota.py`
- `custom_components/lipro/runtime_infra.py`
- 必要时触达其直接 collaborator / tests / guards / review ledgers

### B. Residual cleanup

- localized import cycle / alias / bool-only compat wrapper / stale fallback story
- 仅限 audit 中已确认仍会制造维护噪音或 current-story 误导的对象

### C. Public docs / metadata / release contract

- `README.md`
- `README_zh.md`
- `custom_components/lipro/manifest.json`
- `pyproject.toml`
- `CHANGELOG.md`
- `docs/README.md`
- `.github/ISSUE_TEMPLATE/*`
- `.github/pull_request_template.md`
- `.github/workflows/*`（仅在需要 machine-checkable guard 时触达）

## Requirements

### Locked decisions

- 必须继续 obey 北极星：`keep formal home + split inward + freeze guard`。
- 不新增 public root、compat shell、helper-owned second story。
- 不虚构 maintainer delegate / backup maintainer；组织性限制只能诚实记录。
- plan 产物必须经过 `$gsd-review 68` 审查后再回灌 `$gsd-plan-phase 68 --reviews`。
- 本轮不是 aesthetic cleanup：所有 touched changes 必须有 focused verification 与 governance/doc truth sync。

### The agent's discretion

- 允许选择最小必要的 inward helper / builder / policy extraction 形式。
- 允许为 docs/version drift 新增 focused guard/test/script，只要不引入新依赖。
- 允许对 duplicated troubleshooting/release guidance 做摘要化与 canonical-link 收敛。

## Acceptance Criteria

1. Hotspot files 的主要长流程被拆薄；变更后 formal-home 仍清晰，测试能命中具体 concern，而不是继续依赖 mega guards 兜底。
2. 至少处理一项真实 localized residual（如 import cycle、bool compat wrapper、stale alias 或 duplicate docs story），并把相关 truth 回写到 code/tests/docs。
3. Public docs / metadata surfaces 对外只讲一条 docs/version/release story；stale tag example、beta-vs-stable drift、manifest docs-entry drift 与 duplicate troubleshooting story 被修复或 guard 住。
4. 形成 `plan -> review -> replan -> execute -> verify` 的完整 phase evidence。
5. `uv run ruff check .`、`uv run mypy --follow-imports=silent .`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check` 与 touched focused pytest 通过；如改动面足够广，再跑 `uv run pytest -q`。

## Canonical References

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 北极星终态与禁止回流规则
- `.planning/PROJECT.md` — 当前 active/archived baseline 与里程碑目标
- `.planning/ROADMAP.md` — `v1.16 / Phase 68` 路由真源
- `.planning/REQUIREMENTS.md` — `GOV-52 / ARC-15 / HOT-24 / HOT-25 / OSS-08 / TST-18 / QLT-26`
- `.planning/STATE.md` — 当前执行位置与 continuity
- `.planning/baseline/PUBLIC_SURFACES.md` — public surface / formal root 仲裁
- `.planning/baseline/DEPENDENCY_MATRIX.md` — plane dependency 仲裁
- `.planning/baseline/VERIFICATION_MATRIX.md` — 必跑验证矩阵
- `.planning/reviews/FILE_MATRIX.md` — touched files 的 formal-home / role truth
- `.planning/reviews/RESIDUAL_LEDGER.md` — remaining residual disposition
- `.planning/reviews/KILL_LIST.md` — delete-gate / future retirements
- `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-REMEDIATION-ROADMAP.md` — refreshed audit 的 follow-through seed
- `.planning/phases/67-typed-contract-convergence-toolchain-hardening-and-mypy-closure/67-SUMMARY.md` — 最近 closeout baseline

## Explicit Audit Inputs

### Highest-value code findings

- `custom_components/lipro/core/telemetry/models.py` — 598 LOC，typed contracts / taxonomy / view payload / snapshot 聚合过厚
- `custom_components/lipro/core/mqtt/message_processor.py:112` — `process_message()` 126 行，混合 topic decode、payload validation、logging、callback dispatch、error mapping
- `custom_components/lipro/core/anonymous_share/share_client_flows.py:110` / `:249` — 两条 90+ 行关键流程仍偏厚
- `custom_components/lipro/core/api/diagnostics_api_ota.py:251` — OTA query outcome 流程仍偏厚
- `custom_components/lipro/runtime_infra.py:80` — device-registry listener setup/cleanup 编排仍偏厚

### Docs / metadata findings

- `custom_components/lipro/manifest.json` 的 docs 入口与 `docs/README.md` / `pyproject.toml` / issue templates 不一致
- `README.md` / `README_zh.md` 有 stale release-tag example 与 duplicated troubleshooting story
- `pyproject.toml` 的 `Development Status :: 4 - Beta` 与 `1.0.0` 稳定版本信号不一致
- 当前 CI / pre-commit 未对 docs entry / stale tag example / version-signal drift 做 focused machine-checkable guard

## Out of Scope

- 虚构或承诺新的 maintainer delegate / backup maintainer
- 全量清理 `.planning/phases/**` 历史资产
- 改写整个 milestone archive 历史或重开已关闭的 `v1.14 / v1.15` 架构路线
- 与本轮 audit 无直接关系的 broad rewrite
