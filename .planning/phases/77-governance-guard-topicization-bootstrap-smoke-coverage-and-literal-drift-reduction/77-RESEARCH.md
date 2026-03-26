# Phase 77 Research

## Inputs

- `.planning/phases/77-governance-guard-topicization-bootstrap-smoke-coverage-and-literal-drift-reduction/77-CONTEXT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `tests/meta/governance_current_truth.py`
- `tests/meta/governance_contract_helpers.py`
- `tests/meta/test_governance_closeout_guards.py`
- `tests/meta/test_governance_release_contract.py`
- `tests/meta/test_version_sync.py`
- `tests/meta/test_governance_milestone_archives.py`
- `tests/meta/governance_followup_route_current_milestones.py`
- `tests/meta/test_phase75_governance_closeout_guards.py`
- `tests/meta/toolchain_truth_docs_fast_path.py`
- `scripts/check_file_matrix_registry.py`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`

## Findings That Directly Drive Implementation

### 1. `test_governance_closeout_guards.py` 目前承担了错误的 helper-home 身份

当前多份 governance/topic suites 通过 `from .test_governance_closeout_guards import ...` 反向依赖测试文件里的私有 helper。这样会让：

- closeout suite 兼任共享 API 仓库；
- doc-facing / follow-up / phase-history suites 与 closeout guard 形成隐式内部耦合；
- 后续 topicization 无法形成单向 import 拓扑。

Phase 77 必须先把共享 helper 收口到正式 helper home，让 suite 依赖 helper，而不是 helper 依赖 suite。

### 2. bootstrap smoke 仍分散在多个大文件里，当前 failure localization 不够清晰

active-route / latest-archive / default-next / verification-pointer 相关 smoke 目前散落在：

- `tests/meta/test_governance_closeout_guards.py`
- `tests/meta/test_governance_release_contract.py`
- `tests/meta/test_version_sync.py`

这些断言本质上属于同一条 bootstrap story，但被分摊到不同 concern 文件中，导致：

- route activation drift 时失败位置不够直观；
- 维护者需要同时修改多个 suite 才能完成一条 governance story；
- docs/release/version concern 与 bootstrap concern 的边界继续混杂。

最优解不是新增更多 prose，而是建立 focused bootstrap smoke suite，把 route activation 的最小充分断言收口到单一测试 home。

### 3. route-truth 主真源已经建立，但 remaining literals 仍未完全收口

`tests/meta/governance_current_truth.py` 已承载 machine-readable active-route / latest-archive contract，但 historical closeout route truth、historical archive-transition route truth 与部分 next-command literal 仍在多个文件散写。

Phase 77 的 literal 去重应遵循“只收口反复出现的 route truth”原则：

- historical closeout route truth
- historical archive-transition route truth
- default next command / latest archived evidence pointer 相关 shared literal

不应为了零字面量而过度抽象一次性断言。

### 4. doc-facing boundary 需要与 internal bootstrap boundary 同步冻结

public docs 不能暴露 internal bootstrap folklore，这条边界目前主要靠 `closeout_guards` 中的 helper 维持；一旦 helper home 不诚实，doc-facing guard 的长期维护也会变脆弱。

因此 Phase 77 需要同时完成两件事：

- helper 迁移到诚实的 helper home；
- focused suites 与 doc-facing checks 继续保证 public docs 不出现 internal bootstrap story，而 `.planning/*` 与 governance suites 仍保持可审计 route truth。

### 5. topology 变更若不回写治理登记，会立刻产生第二轮 drift

当前 `scripts/check_file_matrix_registry.py`、`.planning/reviews/FILE_MATRIX.md`、`.planning/baseline/VERIFICATION_MATRIX.md` 仍把旧 topology 视作正式故事线。

如果先拆 helper / suite、后补治理登记，就会产生新的 meta drift：

- checker registry 仍把 `test_governance_closeout_guards.py` 当 helper home；
- FILE_MATRIX 仍把 route/bootstrap ownership 绑定在旧文件；
- VERIFICATION_MATRIX 仍缺少 focused bootstrap smoke 的正式 proof story。

所以本 phase 必须把 topology 变更与治理登记更新捆绑执行。

## Validation Architecture

### Focused Governance Regression

- `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py`
- `uv run pytest -q tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_phase75_governance_closeout_guards.py tests/meta/toolchain_truth_docs_fast_path.py`

这组命令负责验证：

- bootstrap smoke 已独立且覆盖 active-route / archive-transition / next-command / pointer drift；
- helper 迁移后各 suite 仍沿 concern boundary 通过；
- historical route truth 与 shared literals 仍由单一 helper/current-truth home 提供。

### Governance Registration Gate

- `uv run python scripts/check_file_matrix.py --check`

该命令必须确认：

- checker registry 不再把 `test_governance_closeout_guards.py` 记为 helper home；
- FILE_MATRIX / registry 对新 helper 与 focused suite 的身份描述一致；
- governance topology 变更已被正式登记。

### Expanded Governance Sweep

- `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_version_sync.py`

这组回归用于确认 topicization 没有在其它 governance suites 上留下 import 断裂或 route-truth 空洞。

## Rejected Alternatives

- **继续把 helper 留在 `test_governance_closeout_guards.py`，只补文档说明**：这会维持测试文件兼任 helper API 的反模式，没有从结构上解决 boundary leak。
- **把所有 route assertions 全塞进 `governance_current_truth.py`**：会让 current-truth 文件从 shared truth home 膨胀成 mega-helper，不符合“不要为了拆而拆”的原则。
- **只拆 bootstrap smoke，不同步 FILE_MATRIX / VERIFICATION_MATRIX / registry**：这样会制造新的治理登记漂移，Phase 77 会变成半收口。
- **按文件长度平均切块**：行数下降不代表维护性提升；本 phase 必须沿 bootstrap smoke / route truth / boundary freeze 三个 concern 拆分。
