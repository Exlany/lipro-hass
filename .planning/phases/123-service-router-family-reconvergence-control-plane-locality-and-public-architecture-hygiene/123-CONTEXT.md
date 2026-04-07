# Phase 123: service-router family reconvergence, control-plane locality tightening, and public architecture hygiene - Context

**Gathered:** 2026-04-01
**Status:** planning-ready
**Milestone:** `v1.35 Master Audit Closure, Public Surface Finalization & Release Traceability`
**Current route:** `v1.35 active milestone route / starting from latest archived baseline = v1.34`
**Requirements basket:** `ARC-34`, `HOT-54`, `DOC-13`, `GOV-82`, `TST-45`
**Default next command:** `$gsd-execute-phase 123`

<domain>
## Phase 目标

本 phase 的目标不是再发明新的 control-plane story，而是把 master audit 第二轮暴露的拓扑漂移一次收口：

- 将 `service_router` family 的 non-diagnostics callbacks 收回 `custom_components/lipro/control/service_router_handlers.py`，避免四个过薄 split shell 继续合法化 current topology；
- 保留 `custom_components/lipro/control/service_router_diagnostics_handlers.py` 作为 developer / diagnostics 语义较重的独立 collaborator；
- 同步 `docs/developer_architecture.md`、`CHANGELOG.md`、`.planning/codebase/ARCHITECTURE.md`、`docs/architecture_archive.md`、FILE_MATRIX 与 focused guards，使 current-topology 与 predecessor-history 叙事分层清楚；
- 将 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 从 `Phase 122 closeout-ready` 诚实 reopen 到 `Phase 123 complete; closeout-ready`。
</domain>

<evidence>
## 输入证据

- master audit ledger：`.planning/reviews/V1_35_MASTER_AUDIT_LEDGER.md`
- 当前 planning selector truth：`.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md`、`.planning/MILESTONES.md`
- 生产热点：`custom_components/lipro/control/service_router.py`、`custom_components/lipro/control/service_router_handlers.py`、`custom_components/lipro/control/service_router_diagnostics_handlers.py`、`custom_components/lipro/control/service_router_support.py`
- predecessor proof：`tests/meta/test_phase104_service_router_runtime_split_guards.py`、`docs/architecture_archive.md`
- governance/file-matrix truth：`scripts/check_file_matrix_registry_classifiers.py`、`scripts/check_file_matrix_registry_overrides.py`、`.planning/reviews/FILE_MATRIX.md`
- 文档漂移面：`docs/developer_architecture.md`、`CHANGELOG.md`、`.planning/codebase/ARCHITECTURE.md`、`.planning/codebase/TESTING.md`
</evidence>

<issues>
## 已知问题

- `service_router_handlers.py` 当前只剩 family index，但四个非 diagnostics split files 已薄到难以支撑持续独立存在。
- `docs/developer_architecture.md` 仍停留在 `v1.34 archived-only baseline` 叙事，与当前 live route 不一致。
- FILE_MATRIX / focused guards / archive note 仍把 Phase 104 的 split 讲成 current topology，而非 predecessor decomposition。
- 当前 planning docs 仍宣称 `Phase 122` 已是 v1.35 最终 closeout-ready 状态，尚未诚实吸纳第二轮 carry-forward。
</issues>

<non_goals>
## 非目标

- 不触碰 `config_flow.py`、`runtime_types.py`、`entry_auth.py` 的更高风险 structural slimming；这些保留为后续 potential carry-forward。
- 不把 `service_router_diagnostics_handlers.py` 也压回同一文件，避免 developer/diagnostics 语义再次与 public callback family 混杂。
- 不重写 `service_router.py` outward callback surface，不改变 Home Assistant service registrations。
</non_goals>

<validation_surface>
## 建议验证面

- `uv run pytest tests/meta/test_phase69_support_budget_guards.py tests/meta/test_phase104_service_router_runtime_split_guards.py tests/meta/test_phase123_service_router_reconvergence_guards.py tests/meta/test_governance_route_handoff_smoke.py -q`
- `uv run pytest tests/core/test_init_service_handlers_commands.py tests/core/test_init_service_handlers_schedules.py tests/core/test_init_service_handlers_share_reports.py tests/core/test_init_runtime_registry_refresh.py -q`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check .`
- `uv run pytest -q`
</validation_surface>
