# Phase 128 Research

## 背景与目标

`Phase 127` 已完成 `runtime_access` typed telemetry seam 收口、support-view de-reflection 与 route/governance 投影同步。`Phase 128` 的 remaining scope 不再是运行时热点本身，而是把仓库当前已部分具备、但尚未完全 machine-checkable 的 open-source readiness / benchmark / coverage / maintainer continuity truth 收束成可执行治理合同。

本 phase 对应需求：`OSS-17`, `GOV-86`, `QLT-51`。

## 现状盘点

### 已有能力

- current-route selector family 已以 `.planning/baseline/GOVERNANCE_REGISTRY.json::planning_route` 为 machine-readable 真源，`PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 作为投影目标。
- 发布链路已具备较强 hardening：`.github/workflows/release.yml` 复用 `ci.yml`，并叠加 tagged `pip-audit`、tagged CodeQL、SBOM、GitHub artifact attestation、`cosign sign-blob` / `verify-blob --bundle` 与 release identity manifest。
- coverage 已有 blocking total floor + changed-surface file floor：`ci.yml` 调用 `scripts/coverage_diff.py coverage.json --minimum 95 --changed-files .coverage-changed-files --changed-minimum 95`。
- benchmark 已治理化：`tests/benchmarks/benchmark_baselines.json` + `scripts/check_benchmark_baseline.py` + CI benchmark lane + artifact upload。
- support / security / maintainer continuity 的 honesty wording 已大量存在于 `README.md`、`SUPPORT.md`、`SECURITY.md`、runbook、issue/PR 模板与 registry 中。

### 当前缺口

#### 高风险 / 高优先级

1. **open-source readiness 仍未过线**
   - 仓库当前仍是 `private-access`。
   - `single-maintainer` 模式仍无 documented delegate。
   - 当前没有已文档化、保证可达的 non-GitHub private security fallback。
   - 这些事实已被诚实记录，但还没有形成统一、首屏可见、不可误读的 readiness contract。

2. **coverage diff gate 仍缺 baseline truth**
   - `scripts/coverage_diff.py` 已支持 `--baseline`，但 CI 未启用 baseline compare。
   - changed-surface coverage 当前只按“文件级 percent_covered”判定，没有主分支 baseline 回退证据。
   - PR 场景没有 coverage artifact 上传，审计体验弱于 benchmark lane。

3. **benchmark gate 仍偏离线治理，不是 PR 近线反馈**
   - benchmark 仅在 `schedule` / `workflow_dispatch` 运行。
   - PR lane 没有轻量热点 perf smoke。
   - `scripts/check_benchmark_baseline.py` 当前使用 `mean` 且对 manifest 外 benchmark 只做提示，不形成更强约束。

#### 中风险 / 中优先级

4. **minimum Home Assistant version 真源口径分叉**
   - registry / README / SUPPORT / CONTRIBUTING / runbook 使用的是：`hacs.json` 为 canonical source，`pyproject.toml` 为 sync source/dev pin。
   - `SECURITY.md` 与 `.github/ISSUE_TEMPLATE/bug.yml` 仍写成 `pyproject.toml` 为 canonical source。
   - 对开源协作者来说，这类看似小的口径漂移会削弱“哪个文件才是正式真源”的信任。

5. **pytest marker 治理偏弱**
   - benchmark 已使用 `@pytest.mark.benchmark`，但 `pyproject.toml` 的 pytest 配置未开启 `--strict-markers`，也未显式声明 `benchmark` marker。

6. **runbook / docs 仍可能复写 current-route prose**
   - `Phase 127` 已修正 selector docs 与 review ledger，但 maintainer-only runbook 仍需进一步压回“投影而非手写 current-route prose”的姿态。

## 已具备能力 vs 需诚实记录的不可自动化项

### 可自动化项

- PR / push / schedule / workflow_dispatch 下的 coverage baseline compare gate
- coverage artifact 上传与 contract smoke
- benchmark PR smoke 子集 + baseline compare
- pytest `--strict-markers` 与 marker registry
- CI / meta guards 对上述 contract 的 machine verification
- registry / docs / templates 的 wording drift guards

### 必须诚实记录、不可伪自动化项

- documented delegate 是否存在
- non-GitHub private security fallback 是否存在
- maintainer unavailable 时是否 freeze new tagged releases and new release promises
- readiness 是否真正达到“可持续开源协作”，还是仅达到“honesty on current limits”

这些项不能通过伪造脚本“自动变绿”；正确做法是把未闭环状态写成明确 contract，并在 README / SUPPORT / SECURITY / runbook / registry 中保持一致。

## 建议的计划拆分

### Plan 128-01：open-source readiness honesty contract 与 selector projection 收口

**目标**
- 统一 current-route / continuity / private-access / minimum HA version 真源口径。
- 把 `continuity readiness not achieved yet` 的 honest contract 写清楚，避免从不同文档读出不同答案。

**建议文件**
- `README.md`
- `CONTRIBUTING.md`
- `SUPPORT.md`
- `SECURITY.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `.github/ISSUE_TEMPLATE/bug.yml`
- `.github/pull_request_template.md`
- `.planning/baseline/GOVERNANCE_REGISTRY.json`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`

**建议 proof chain**
- `uv run pytest -q tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_release_contract.py tests/meta/toolchain_truth_ci_contract.py tests/meta/toolchain_truth_testing_governance.py`

### Plan 128-02：coverage baseline diff gate 与 evidence artifact formalization

**目标**
- 在 PR / push lane 中启用 baseline-aware coverage contract，而不只是 current-run absolute floor。
- 上传 coverage artifacts，使 coverage 证据沉淀层级不低于 benchmark。

**建议文件**
- `.github/workflows/ci.yml`
- `scripts/coverage_diff.py`
- `scripts/lint`
- `tests/meta/toolchain_truth_ci_contract.py`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/codebase/TESTING.md`
- `CONTRIBUTING.md`

**建议 proof chain**
- `uv run pytest -q tests/meta/toolchain_truth_ci_contract.py tests/meta/toolchain_truth_testing_governance.py`
- `uv run python scripts/coverage_diff.py --help`（或 focused smoke）

### Plan 128-03：benchmark PR smoke、strict markers 与 final governance freeze

**目标**
- 为 PR 提供轻量 benchmark smoke，不再只依赖 schedule/manual lane。
- 在 pytest 配置中启用 strict markers，并显式声明 benchmark marker。
- 冻结本 phase 的 governance/docs/testing map truth，生成 summary / verification / validation 资产。

**建议文件**
- `.github/workflows/ci.yml`
- `pyproject.toml`
- `scripts/check_benchmark_baseline.py`
- `tests/meta/toolchain_truth_ci_contract.py`
- `tests/meta/test_governance_release_contract.py`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/codebase/TESTING.md`

**建议 proof chain**
- `uv run pytest -q tests/meta/toolchain_truth_ci_contract.py tests/meta/test_governance_release_contract.py tests/meta/toolchain_truth_testing_governance.py`
- `uv run pytest -q tests/benchmarks/test_command_benchmark.py tests/benchmarks/test_mqtt_benchmark.py tests/benchmarks/test_device_refresh_benchmark.py`（视 smoke 设计而定）

## 风险与回滚/守卫建议

- **风险 1：baseline coverage compare 实现过重**
  - 建议优先选择 CI 内可自举的 baseline 方案（例如 merge-base worktree / second coverage pass / explicit artifact），不要引入依赖外部平台的脆弱逻辑。
- **风险 2：PR benchmark smoke 噪音过高**
  - 建议只跑 2~3 个热点 smoke benchmark，且保持宽松 no-regression 阈值；完整 benchmark lane 继续保留 schedule/manual。
- **风险 3：honesty wording 与 automation contract 混写**
  - 建议把“可自动验证的 gate”和“诚实记录但未闭环的现实限制”拆成两个小节，避免用户误读“文档写了就等于能力已具备”。
- **风险 4：把 current-route prose 再写散**
  - 一切 current-route wording 继续以 `.planning/baseline/GOVERNANCE_REGISTRY.json::planning_route` 为唯一 machine-readable selector，其他文档只投影，不自立 current story。

## 裁决

`Phase 128` 应继续沿当前 roadmap 执行，不必为了治理/质量问题临时重开 `Phase 127`。但 architecture 审计提出的 deeper boundary / de-API / canonical-contract debt 需要在本轮 closeout 后登记为后续 active route，而不是被 governance hardening 掩盖。
