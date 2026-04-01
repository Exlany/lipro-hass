# Phase 124: config-entry auth seed normalization, config-flow adapter thinning, and schedule contract closure - Context

**Gathered:** 2026-04-01
**Status:** planning-ready
**Milestone:** `v1.35 Master Audit Closure, Public Surface Finalization & Release Traceability`
**Current route:** `v1.35 active milestone route / starting from latest archived baseline = v1.34`
**Requirements basket:** `ARC-35`, `HOT-55`, `ARC-36`, `GOV-83`, `TST-46`
**Default next command:** `$gsd-execute-phase 124`

<domain>
## Phase 目标

本 phase 不是扩张功能，而是把 `Phase 123` closeout 后仍留在 control-plane 上的两组高价值 carry-forward 一次收口：

- 把 `config-entry` auth seed / remembered password-hash / persisted `biz_id` 语义收敛到单一 formal helper，不再让 `config_flow.py`、`flow/submission.py` 与 `entry_auth.py` 各自解释；
- 继续把根层 `custom_components/lipro/config_flow.py` 压回 thin adapter：user / reauth / reconfigure 的 orchestration 下沉到 `flow/` home，根层只保留 HA entry-point glue；
- 给 `schedule` callback family 补齐 direct-call formal contract：registry schema 与直接调用 helper 共享同一 normalization / result typing，不再让 `services/schedule.py` 依赖 ad-hoc dict 与 handler-local payload assumptions；
- 同步 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`、FILE_MATRIX / RESIDUAL_LEDGER / KILL_LIST / codebase docs / testing docs，使 `Phase 124` 成为 v1.35 的诚实最终 closeout carry-forward。
</domain>

<evidence>
## 输入证据

- 现行真源：`docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md`
- flow/auth 热点：`custom_components/lipro/config_flow.py`、`custom_components/lipro/flow/login.py`、`custom_components/lipro/flow/submission.py`、`custom_components/lipro/entry_auth.py`
- runtime/service 热点：`custom_components/lipro/services/contracts.py`、`custom_components/lipro/services/schedule.py`、`tests/meta/test_runtime_contract_truth.py`
- focused tests：`tests/flows/test_config_flow_user.py`、`tests/flows/test_config_flow_reauth.py`、`tests/flows/test_config_flow_reconfigure.py`、`tests/flows/test_flow_submission.py`、`tests/core/test_token_persistence.py`、`tests/core/test_init_service_handlers_schedules.py`、`tests/services/test_services_schedule.py`
- governance/docs：`.planning/reviews/FILE_MATRIX.md`、`.planning/reviews/RESIDUAL_LEDGER.md`、`.planning/reviews/KILL_LIST.md`、`.planning/reviews/V1_35_MASTER_AUDIT_LEDGER.md`、`.planning/codebase/ARCHITECTURE.md`、`.planning/codebase/CONCERNS.md`、`.planning/codebase/TESTING.md`、`docs/developer_architecture.md`
</evidence>

<issues>
## 已知问题

- `config_flow.py` 仍然直接持有 user / reauth / reconfigure 多分支 orchestration，和“根层只做 thin adapter”的正式叙事还不够对齐。
- `remember_password_hash` / persisted password-hash / `biz_id` 的读写解释散落在 `flow/submission.py`、`flow/login.py` 与 `entry_auth.py`；其中 token persistence 对 cleared `biz_id` 仍可能保留旧值。
- `schedule` handler 仍只依赖注册层 schema；direct-call path 缺乏与 `send_command` 对等的 normalization contract，返回值也仍是 ad-hoc dict。
- 当前 planning/governance docs 虽已切到 `Phase 124 execution-ready`，但 phase assets 仍需压实为五计划 inventory，并为 closeout-ready 投影保留单一路径。
</issues>

<non_goals>
## 非目标

- 不重写 runtime/coordinator 整体 surface，不在本 phase 内处理 `runtime_types.py` 的全局瘦身。
- 不改变 Home Assistant service 名称、公开 service router outward surface 或 config-entry key 名称。
- 不触碰 protocol/auth bootstrap 的 host-neutral truth，仅收口 control-plane adapter / persisted-entry 解释。
</non_goals>

<validation_surface>
## 建议验证面

- `uv run pytest tests/flows/test_config_flow_user.py tests/flows/test_config_flow_reauth.py tests/flows/test_config_flow_reconfigure.py tests/flows/test_flow_submission.py tests/core/test_token_persistence.py -q`
- `uv run pytest tests/core/test_init_service_handlers_schedules.py tests/services/test_services_schedule.py tests/meta/test_runtime_contract_truth.py -q`
- `uv run pytest tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_release_contract.py tests/meta/test_public_surface_guards.py -q`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check .`
- `uv run pytest -q`
</validation_surface>
