# Phase 125: terminal residual eradication, runtime-types decomposition, adapter final thinning, and machine-readable governance extraction - Context

**Gathered:** 2026-04-01
**Status:** planning-ready
**Milestone:** `v1.35 Master Audit Closure, Public Surface Finalization & Release Traceability`
**Current route:** `v1.35 active milestone route / starting from latest archived baseline = v1.34`
**Requirements basket:** `ARC-37`, `HOT-56`, `GOV-84`, `TST-47`, `QLT-49`, `DOC-14`
**Default next command:** `$gsd-execute-phase 125`

<domain>
## Phase 目标

本 phase 不是扩张功能，而是在 v1.35 closeout 前把 remaining residual 彻底压回单一 formal route：

- 保留 `custom_components/lipro/runtime_types.py` 作为 sanctioned root-level outward home，但把其内部过厚的 cross-plane contract families inward decomposition，消除 duplicated alias、逆向类型耦合与 mega-port 趋势；
- 继续把 `custom_components/lipro/config_flow.py` 与 `custom_components/lipro/entry_auth.py` 压回 thin adapter / bootstrap home，把纯 pass-through orchestration、result shaping 与 transient auth helpers 下沉到 `flow/` 或更窄 helper；
- 把当前重复维护在 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 五份 planning docs 中的 `governance-route` truth 收口到既有 `.planning/baseline/GOVERNANCE_REGISTRY.json` 的单一 machine-readable section，再由 tests/tooling/docs 共同消费；
- 精简 `tests/meta` 与 checker 的 prose-heavy brittleness，让 current-route / governance / toolchain guard 优先依赖 machine-readable manifest 与更小的 focused suites；
- 同步 FILE_MATRIX / codebase docs / maintainer docs / active audit ledger，使 v1.35 的 closeout 不再带着“已知但未清零的 non-blocking residual”。
</domain>

<evidence>
## 输入证据

- 现行真源：`docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md`、`.planning/MILESTONES.md`
- runtime hotspot：`custom_components/lipro/runtime_types.py`、`custom_components/lipro/services/maintenance.py`、`custom_components/lipro/core/coordinator/runtime/command_runtime_support.py`、`custom_components/lipro/core/coordinator/services/protocol_service.py`
- flow/auth hotspot：`custom_components/lipro/config_flow.py`、`custom_components/lipro/entry_auth.py`、`custom_components/lipro/flow/*.py`
- governance/test hotspot：`tests/meta/governance_current_truth.py`、`tests/meta/test_governance_release_contract.py`、`tests/meta/toolchain_truth_testing_governance.py`、`scripts/check_file_matrix_registry_overrides.py`
- docs/projection：`docs/developer_architecture.md`、`.planning/reviews/FILE_MATRIX.md`、`.planning/reviews/V1_35_MASTER_AUDIT_LEDGER.md`、`.planning/codebase/TESTING.md`
- 审计输入：主代理的 repo-wide 架构审阅，以及 `runtime_types` / control / governance / meta-tooling 多份只读审计结论
</evidence>

<issues>
## 已知问题

- `runtime_types.py` 是 sanctioned outward home，但已变成“正确但偏厚”的 contract hub：多类 protocol/runtime/telemetry/service-facing contracts 聚于同一文件，且存在 duplicated alias 与逆向类型依赖。
- `config_flow.py` 仍承载过多 user / reauth / reconfigure pass-through state-machine glue；`entry_auth.py` 仍可继续剥离 transient helper 与 thin-adapter 外的细节。
- `governance-route` 当前虽然在五份 planning docs 中保持一致，但维护成本高；`tests/meta/governance_current_truth.py` 仍通过提取这五份 block 来建立 canonical truth，而仓库其实已有 `.planning/baseline/GOVERNANCE_REGISTRY.json` 这一更适合承载 machine-readable selector truth 的正式治理资产。
- `tests/meta` 与 checker 对 prose / wording 的依赖偏重，导致“语义不变但文案调整”也可能触发 brittle failures；`scripts/check_file_matrix_registry_overrides.py` 与相关治理脚本也开始呈现自身治理热点。
- 当前 route 已从 `Phase 124 closeout-ready` 诚实重开到 `Phase 125 execution-ready`；若本 phase 不完成，v1.35 不应归档。
</issues>

<non_goals>
## 非目标

- 不新增业务功能，不改 Home Assistant outward service names / config-entry key names / public integration identity。
- 不推翻 `runtime_types.py` 的 outward formal home，也不进行大规模目录迁移或引入新依赖。
- 不在本 phase 内重写 protocol/coordinator 主链，只做 inward decomposition、contract dedupe、governance extraction 与 guard slimming。
- 不把 machine-readable governance contract 扩张成新的 second story；它必须复用既有治理真源（优先 `.planning/baseline/GOVERNANCE_REGISTRY.json`），而不是再开平行 manifest。
</non_goals>

<validation_surface>
## 建议验证面

- `uv run pytest tests/meta/test_runtime_contract_truth.py tests/meta/public_surface_architecture_policy.py -q`
- `uv run pytest tests/flows/test_config_flow_user.py tests/flows/test_config_flow_reauth.py tests/flows/test_config_flow_reconfigure.py tests/core/test_token_persistence.py -q`
- `uv run pytest tests/meta/governance_current_truth.py tests/meta/test_governance_release_contract.py tests/meta/toolchain_truth_testing_governance.py tests/meta/test_governance_guards.py -q`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check .`
- `uv run pytest -q`
</validation_surface>
