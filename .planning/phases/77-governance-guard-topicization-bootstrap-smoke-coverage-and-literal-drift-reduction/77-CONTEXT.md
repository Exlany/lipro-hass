# Phase 77: Governance guard topicization, bootstrap smoke coverage, and literal-drift reduction - Context

**Gathered:** 2026-03-26
**Status:** Ready for planning
**Source:** `$gsd-next` 从 `Phase 76` 自动前推 + repo-local governance scan

<domain>
## Phase Boundary

本 phase 是一次 **governance test topology refinement**，不是新的 runtime / control / protocol 架构迁移。

必须只处理与 `current-route / latest-archive / next-step bootstrap` 直接相关的治理守卫与共享真源：

1. 把 active-route bootstrap、archive transition、docs/private-boundary drift 从巨型治理套件中切成 focused suites；
2. 把 cross-file 反复出现的 route literals 与 historical route truth 收口到单一 shared truth home；
3. 让 doc-facing suite、current-milestone follow-up suite、closeout suite 回到各自 concern boundary；
4. 同步治理矩阵、file-matrix 与 checker registry，使新的测试拓扑成为正式可审计真相；
5. 不得借 topicization 新建第二套 governance story、helper folklore 或 public-facing bootstrap narrative。

本 phase 不处理：

- 外部 GSD 工具源码修改；
- public docs 新增 internal bootstrap folklore；
- 与当前 route truth 无关的生产代码重构；
- 仅为降行数而进行的机械切块。

</domain>

<decisions>
## Locked Decisions

- split 采用 **topic-first / concern-first** 原则：按 bootstrap smoke、route-truth sharing、doc-facing boundary 三条故事线切，不按文件长度平均分块。
- `tests/meta/test_governance_closeout_guards.py` 必须降回 closeout smoke anchor；共享 helper 不再继续寄生在测试文件中。
- 现有跨文件复用的 route/doc 辅助逻辑，应迁入正式 helper home；优先扩展 `tests/meta/governance_contract_helpers.py`，必要时新增一个仅服务 promoted-assets truth 的窄 helper 模块，但禁止把 helper 再做成第二套 truth root。
- active-route / latest-archive / next-command / verification-pointer 的 bootstrap smoke 要聚焦成独立 focused suite；`release_contract`、`version_sync` 与 `closeout_guards` 里只保留各自 concern 必需的断言。
- `tests/meta/governance_current_truth.py` 继续作为 route-truth 主真源；historical closeout route truth、historical archive-transition route truth 与 remaining shared literals 优先收口到这里，只允许增加极小、可复用、不会反客为主的 helper/constant。
- `tests/meta/test_governance_milestone_archives.py`、`tests/meta/governance_followup_route_current_milestones.py`、`tests/meta/test_phase75_governance_closeout_guards.py` 中重复散写的 historical route truth 必须去重，不再允许三地同步维护同一字面量。
- public docs 必须继续隐藏 internal bootstrap folklore；但 contributor / maintainer governance truth 仍需在 `.planning/*`、verification matrix 与 focused tests 中保持可审计、可回归。
- `.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/reviews/FILE_MATRIX.md` 与 `scripts/check_file_matrix_registry.py` 必须同步到新的 topology；不能出现“测试已拆，治理登记仍把旧文件当 helper home”的失真。
- 若新增 focused suite 或 helper，命名必须直指 concern，例如 `bootstrap smoke`、`route truth`、`promoted assets`；不要再用含混 mega-guard 命名。

### Claude's Discretion

- 可把纯 bootstrap smoke 断言从现有大文件中搬迁到新 topic suite，只要不改变治理真相。
- 可在 `governance_current_truth.py` 中补充 small constants / assertions，以替代 scattered literals。
- 可将 helper 重定位到更诚实的 helper home，并统一 import 面；但不要为了“抽象优雅”而增加多余层级。
- 可顺手把 focused suite 纳入验证矩阵与 file-matrix，只要保持 authority story 单一且清晰。

</decisions>

<canonical_refs>
## Canonical References

- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/phases/76-governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation/76-CONTEXT.md`
- `.planning/phases/76-governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation/76-VERIFICATION.md`
- `.planning/phases/59-verification-localization-and-governance-guard-topicization/59-CONTEXT.md`
- `tests/meta/governance_current_truth.py`
- `tests/meta/governance_contract_helpers.py`
- `tests/meta/test_governance_closeout_guards.py`
- `tests/meta/test_governance_release_contract.py`
- `tests/meta/test_version_sync.py`
- `tests/meta/test_governance_milestone_archives.py`
- `tests/meta/governance_followup_route_current_milestones.py`
- `tests/meta/test_phase75_governance_closeout_guards.py`
- `scripts/check_file_matrix_registry.py`
- `scripts/check_file_matrix.py`

## Hotspot Observations

- `tests/meta/test_governance_closeout_guards.py` 当前既是测试文件，又承担共享 helper 仓库职责；这让 closeout suite、follow-up suite、docs fast-path suite 之间形成隐式内部 API。
- `tests/meta/test_governance_release_contract.py` 与 `tests/meta/test_version_sync.py` 都仍承载部分 bootstrap smoke；职责并不纯，且让 route activation story 横跨多个大文件。
- `tests/meta/governance_current_truth.py` 已有 machine-readable route contract，但 historical route truth 与 remaining literals 仍未完全统一收口。
- `tests/meta/test_governance_milestone_archives.py`、`tests/meta/governance_followup_route_current_milestones.py` 与 `tests/meta/test_phase75_governance_closeout_guards.py` 仍重复维护 historical closeout / archive-transition route truth 文案。
- `scripts/check_file_matrix_registry.py` 与 `.planning/reviews/FILE_MATRIX.md` 目前仍把旧拓扑视为当前真相；若先拆测试、后补治理登记，会再次制造 drift。
- 本 phase 的最佳收益点不是再写 route prose，而是把 bootstrap smoke / shared route truth / doc-facing boundary 三个 concern 从巨型治理套件里剥离出来。

</canonical_refs>

<execution_shape>
## Recommended Execution Shape

- `77-01`：先建立 focused bootstrap smoke suite，收口 active-route、latest-archive、next-command 与 verification-pointer 的最小充分断言。
- `77-02`：再扩展 `governance_current_truth.py`，把 historical route truth 与 remaining shared literals 去重，并替换 scattered hard-coded assertions。
- `77-03`：最后剥离 `test_governance_closeout_guards.py` 的 helper 身份，冻结 doc-facing / internal-bootstrap boundary，并同步 `VERIFICATION_MATRIX`、`FILE_MATRIX` 与 checker registry。

## Minimum Validation Intent

- focused governance regression 至少覆盖：bootstrap smoke、milestone archives、current-milestone follow-up、release contract、version sync。
- helper 重定位后，所有历史 `from .test_governance_closeout_guards import ...` 依赖必须被消除或显著收敛。
- `uv run python scripts/check_file_matrix.py --check` 必须承认新的 topology，而不是继续引用旧 helper home。
- public docs 仍不得出现 internal bootstrap folklore；`.planning/*` 与 focused suites 必须继续保留可审计 route truth。

## Migration Guardrails

- 允许新增 focused suite，但不允许把原有 mega-suite 直接清空成无意义转发壳；每个剩余文件都必须保留清晰 concern。
- 允许抽出共享 helper，但 helper home 必须描述“共享 contract / promoted-assets truth / route-truth truth”，而不是继续藏在 `test_*.py` 中。
- 允许把 version-sync 或 release-contract 中的 bootstrap 断言迁走，但迁走后原文件仍要保留其各自 domain truth，不得造成 coverage 空洞。
- 新 helper / suite 的 import 方向必须单向收敛：suite 依赖 helper，helper 不依赖 suite。
- 如果某个 literal 只在一个文件出现且没有复用收益，不必强行抽象；本 phase 的目标是减少 drift tax，而不是追求零字面量。

## Expected Outputs For Planning

- 一个 focused bootstrap smoke test home，负责 active-route / archive-transition / next-command / pointer smoke。
- 一个更诚实的 shared helper topology，替代当前对 `test_governance_closeout_guards.py` 的反向 helper 依赖。
- 一个扩展后的 `governance_current_truth.py`，覆盖 remaining historical route truth literals。
- 一次同步后的 governance registration 更新，使 verification matrix、file matrix 与 checker registry 与新 topology 同步。
- 一组最小充分的 targeted test commands，能让后续 phase execution 在不跑全仓的情况下快速验证 route-truth 回归。


## Non-Goals Reminder

- 不改写 milestone prose 的历史正文风格；只修正它们与 current-route bootstrap 的边界关系。
- 不在 public docs 中新增 maintainer-only command hints。
- 不为了 topicization 引入新依赖或生成脚本。

</execution_shape>
