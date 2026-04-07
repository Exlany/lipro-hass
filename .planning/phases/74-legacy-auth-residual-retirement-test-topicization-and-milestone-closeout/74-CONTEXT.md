# Phase 74 Context

## Phase

- **Number:** `74`
- **Title:** `Legacy auth residual retirement, test topicization, and milestone closeout`
- **Milestone:** `v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement`
- **Starting baseline:** `v1.20 active / Phase 73 complete`
- **Archived reference:** `v1.19 archived / evidence-ready`

## Why This Phase Exists

`Phase 72` 与 `Phase 73` 已把 runtime bootstrap、lifecycle、`runtime_access` / runtime-access、service-family、diagnostics/helper 与 runtime-surface 主链收口到北极星正式路径，但仓库仍留有几类“非阻塞却不够诚实”的残口：

- auth legacy residual 的治理账本仍保留已物理退场的 `get_auth_data()` delete gate，当前故事与历史 closeout 互相打架
- `custom_components/lipro/services/registrations.py` 仍作为 compat import shell 留在树上，生产路径已不使用它，但测试 / 文档 / policy 仍承认它存在
- `docs/README.md` 仍混入当前治理状态、下一条 GSD 命令与 archive 索引，公开 docs map 与 maintainer governance appendix 边界不够干净
- `.gitignore` 继续保留只放行 `Phase 12` 的旧例外，与当前 `.planning/phases/**` execution-trace / promoted-allowlist 规则不一致
- `scripts/agent_worker.py` 与 `scripts/orchestrator.py` 虽保留为 fail-fast retired stubs，但文案与 delete gate 不够诚实
- `tests/core/test_share_client.py` 与 `tests/core/coordinator/runtime/test_command_runtime.py` 仍是 remaining large suites，failure radius 偏大，需要进一步 topicize

## In Scope

- `custom_components/lipro/services/registrations.py`
- `custom_components/lipro/control/service_registry.py`
- `custom_components/lipro/entry_auth.py`
- `scripts/agent_worker.py`
- `scripts/orchestrator.py`
- `README.md`
- `README_zh.md`
- `CONTRIBUTING.md`
- `SUPPORT.md`
- `docs/README.md`
- `docs/TROUBLESHOOTING.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `docs/developer_architecture.md`
- `.gitignore`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/GOVERNANCE_REGISTRY.json`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/ARCHITECTURE_POLICY.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `tests/core/test_share_client.py`
- `tests/core/coordinator/runtime/test_command_runtime.py`
- touched `tests/meta/**`, `tests/services/**`, `tests/core/**`

## Constraints

- 不重开第二条架构故事线；只做 inward convergence / residual retirement / topicization
- 删除 compat shell 时必须同步 policy、baseline、review、tests 与 public docs；不允许留下“代码删了，治理没删”的半收口状态
- auth residual 只能讲一条真话：`AuthSessionSnapshot` 是唯一正式 auth/session truth；已退场 fallback 不能继续挂在 active delete gate 上
- 公开 docs map 不能泄露 current-route / next-command / archive index 细节；这些属于 maintainer appendix / governance truth
- `.planning/phases/**` 可以继续被 Git 跟踪，但 authority 身份仍必须由 promoted/reference 规则决定，不能因为被 track 就自动升级为 truth
- 所有 Python / test / script 命令统一使用 `uv run ...`
