# Phase 32 Context

**Phase:** `32 Truth convergence, gate honesty, and quality-10 closeout`
**Milestone:** `v1.3 Quality-10 Remediation & Productization`
**Date:** `2026-03-17`
**Status:** `planned — ready for execution`
**Source:** `ROADMAP` / `REQUIREMENTS` / `STATE` / `PROJECT` + full-repo final review conclusions + `v1.3` continuation closeout artifacts

## Why Phase 32 Exists

`Phase 25 -> 31` 已把 correctness、telemetry seam、trust chain、typed/exception budgets 与 hotspot follow-through 做到一个高位，但再次全仓终审后仍有一簇 **跨文档、跨门禁、跨 hotspot 的 final-closeout 问题** 尚未收束成单一 current story：

1. active planning truth 仍把 `25 -> 31` 写成 closeout-ready，而新的全仓终审要求已明确需要 `Phase 32` final tranche。
2. repo-wide `ruff` / `mypy` / CI / contributor docs 的 gate 口径还不够诚实，存在“文档强于现实”或“现实未被显式裁决”的风险。
3. release identity / code-scanning defer truth、maintainer continuity、PR template / contributor docs / public docs 仍有漂移点。
4. `.planning/codebase/*` 与 `docs/developer_architecture.md` 仍需要 freshness / disclaimer / authority-boundary 收口，避免 derived map 被误读成真源。
5. giant roots、giant tests、typed debt、broad-catch、fallback / legacy residue 仍需要最后一轮系统化 follow-through。

## Goal

1. 统一 `PROJECT` / `ROADMAP` / `REQUIREMENTS` / `STATE` 的 active planning truth，并诚实处理 retained handoff/audit pointer 的 supersession 边界。
2. 把 repo-wide gate story 收紧到 machine-checkable truth：`ruff` / `mypy` / CI / docs 讲同一条故事。
3. 统一 release identity、code-scanning defer、single-maintainer continuity 与 contributor/public docs template story。
4. 刷新 `.planning/codebase/*`、`docs/developer_architecture.md` 与双语 public docs 的 freshness / disclaimer / authority-boundary truth。
5. 继续切薄 giant roots/tests，并把 `Any` / broad-catch / fallback residue 从 no-growth 推进到 measurable burn-down 或 explicit defer truth。

## Decisions (Locked)

- 本 phase 不新建第二 root、第二 release story、第二 authority chain。
- gate honesty 优先于“纸面全绿”；若 gate 尚未 repo-wide blocking，就必须诚实收窄口径并机器化守护。
- `.planning/codebase/*.md` 继续只是 derived collaboration maps；若与 north-star / baseline / review truth 冲突，必须修 map 而不是倒逼真源。
- single-maintainer reality 必须制度化、可审计，但不得虚构 backup maintainer。
- 双语 public docs 视为同一组 surface；任何对外叙事变更都不能只改英文或只改中文。
- hotspot follow-through 只能沿 `protocol / control / runtime / services / tests / meta` 现有正式 seams 推进，不得重建新总线或新 façade root。
- reverse-engineered vendor `MD5` 登录路径继续按协议约束对待；除非上游可替换路径被证实，否则不把它伪装为仓库可独立消灭的密码学债。

## Non-Negotiable Constraints

- 必须继续复用 `.github/workflows/ci.yml` 与现有治理矩阵，而不是发明新门禁故事线。
- 不得把 attestation、provenance、signing、code scanning 混写成一个模糊概念。
- 不得把 `code scanning` defer truth 写丢，或把 single-maintainer 限制美化成不存在的冗余现实。
- 不得让 `fallback / legacy / phase` 历史语义重新合法化为 active public surface。
- 不得为了追求数值漂亮，把 `Any` / broad-catch debt 重新包装成新的 helper / wrapper 噪声层。

## Canonical References

- `.planning/ROADMAP.md` — `Phase 32` goal / success criteria / sequencing
- `.planning/REQUIREMENTS.md` — `GOV-24`, `QLT-05`, `GOV-25`, `GOV-26`, `HOT-07`, `TST-04`, `TYP-08`, `ERR-06`, `RES-06`
- `.planning/STATE.md` — current mode / next focus / continuity truth
- `.planning/PROJECT.md` — v1.3 route map, review routing promise, explicit clarifications
- `.planning/v1.3-HANDOFF.md` — `Phase 25 -> 31` historical closeout baseline to be superseded explicitly, not silently erased
- `.planning/v1.3-MILESTONE-AUDIT.md` — prior closeout-eligible judgment that now requires a Phase 32 truth-convergence pass
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/baseline/AUTHORITY_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/codebase/*.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `README.md`
- `README_zh.md`
- `CONTRIBUTING.md`
- `SUPPORT.md`
- `SECURITY.md`
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `.github/CODEOWNERS`
- `.github/pull_request_template.md`
- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/coordinator/coordinator.py`
- `tests/core/api/test_api.py`
- `tests/core/test_init.py`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_governance_closeout_guards.py`
- `scripts/check_file_matrix.py`

## Specifics To Lock During Planning

- `PROJECT / ROADMAP / REQUIREMENTS / STATE` 必须先对 `Phase 32` current truth 达成一致，再谈 execution。
- `QLT-05` 必须明确：repo-wide `mypy` 若仍非真实 blocking gate，就不能继续被文档暗示为已绿或已硬门禁。
- release identity / code scanning / signing / attestation 术语必须拆开讲清楚，既不夸大，也不弱化。
- `.planning/codebase/*.md` 必须显式声明 freshness、derived-map 身份与 authority boundary。
- hotspot/test/typed/exception burn-down 不能再汇总成“以后继续优化”的黑洞 phase；必须切成可执行簇并带验证命令。

## Expected Plan Shape

最优应为 `5 plans / 4 waves`：

1. `32-01` — planning truth convergence and requirement traceability repair
2. `32-02` — repo-wide gate honesty and toolchain reality alignment
3. `32-03` — release identity posture, maintainer continuity, and docs-template convergence
4. `32-04` — codebase-map freshness, authority disclaimers, and bilingual public-doc sync
5. `32-05` — hotspot slimming, mega-test topicization, typed/exception burn-down, and residual honesty closeout
