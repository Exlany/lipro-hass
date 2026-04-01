# Phase 125 Research

**Status:** ready

## Research Verdict

- `runtime_types.py` 当前是 sanctioned outward formal home，不应粗暴搬家；最优解是保持 outward import truth 不变，只做 inward decomposition、duplicate contract cleanup 与 reverse-coupling 收口。
- `config_flow.py` / `entry_auth.py` 在 `Phase 124` 后已经明显瘦身，但根层仍残留较多 pass-through state-machine glue 与 bootstrap helper；closeout 前应继续压回 `flow/` 与更窄 auth helpers。
- `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 当前通过五份近似 `governance-route` block 维持 current truth；虽然一致，但维护成本偏高，且 `tests/meta/governance_current_truth.py` 仍需从五处提取 canonical truth。最佳做法不是再开新 manifest，而是把 current-route section 收口到既有 `.planning/baseline/GOVERNANCE_REGISTRY.json`。
- `tests/meta` 与 checker 具备很强的 guard 密度，但 prose-heavy wording guards、testing-map regex 与大体量治理脚本已形成新的可维护性热点。Phase 125 应把“语义守卫”与“文案投影”分离。
- 本 phase 的最优策略不是再开新 formal root，而是：先建立 governance contract 真源，再并行收 runtime_types 与 flow/auth residual，最后把 meta/tooling/docs/no-regrowth 全部冻结到新 topology 上。

## Recommended Scope

- 在既有 `.planning/baseline/GOVERNANCE_REGISTRY.json` 中新增/扩展 planning selector current-route section，并让 `tests/meta/governance_current_truth.py` 优先消费该 machine-readable truth，而不是继续以五份 docs block 互相比对作为 canonical source。
- 保留 `custom_components/lipro/runtime_types.py` 作为 outward formal home，但把其中过厚的 protocol/runtime/telemetry families inward 到更窄 support-only contract modules；同步清理 `services/maintenance.py`、`command_runtime_support.py` 等 duplicated truth。
- 继续瘦身 `custom_components/lipro/config_flow.py` 与 `custom_components/lipro/entry_auth.py`：根层只保留 HA adapter / bootstrap home，user/reauth/reconfigure branching 与 transient helper 再向 `flow/` 或更窄 helper 下沉。
- 让 `tests/meta` 与 toolchain guards 从 prose-heavy wording checks 迁移到 machine-readable contract / focused manifest 驱动，并为 `FILE_MATRIX` / `TESTING.md` / architecture policy 补齐更小更稳的验证面。
- 更新 FILE_MATRIX / maintainer docs / codebase maps / active audit ledger / phase evidence，使 v1.35 的 closeout 条件建立在新的 machine-readable truth 与 residual no-regrowth guard 之上。

## Risks and Guardrails

- 不引入第二个 runtime public root；`runtime_types.py` 仍是唯一 sanctioned outward home，任何拆分都必须 inward/private。
- 不更改 integration outward identity、HA service names、config-entry key names 或发布面语义。
- 不新增依赖；所有 manifest / contract / helper 均使用现有 Python/YAML/JSON/tooling 能力。
- machine-readable governance contract 必须是 single source，并复用现有治理 registry，而不是在五份 docs block 外再复制第六份近似 truth。
- meta/tooling slimming 只能减少 brittle wording guards，不能降低 route truth / public surface / release governance 的严谨度。

## Suggested Plan Split

### Plan 125-01
- 目标：建立 machine-readable governance current-route contract，并把 phase-125 planning assets / selector docs / loader helpers 切到同一真源。
- 依赖：无。
- 验证：`node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap get-phase 125`、focused governance route smoke、machine-readable contract loader tests。

### Plan 125-02
- 目标：对 `runtime_types.py` 做 inward decomposition 与 duplicate contract cleanup，保持 outward home 不变。
- 依赖：125-01。
- 验证：runtime contract truth、architecture policy、focused runtime/service suites。

### Plan 125-03
- 目标：继续压薄 `config_flow.py` / `entry_auth.py`，补 flow/auth focused regressions。
- 依赖：125-01。
- 验证：flow suites、token persistence、reauth/reconfigure focused tests。

### Plan 125-04
- 目标：把 `tests/meta` 与相关 checker 迁到 machine-readable contract / focused manifest 驱动，精简 prose-heavy brittleness。
- 依赖：125-01, 125-02, 125-03。
- 验证：meta/toolchain focused suites、`check_file_matrix.py --check`、testing-map truth guards。

### Plan 125-05
- 目标：同步 FILE_MATRIX / maintainer docs / codebase maps / active audit ledger / verification chain，冻结 residual no-regrowth truth，为 v1.35 closeout 提供最终证据。
- 依赖：125-02, 125-03, 125-04。
- 验证：focused governance/docs guards、`uv run ruff check .`、`uv run pytest -q`。
