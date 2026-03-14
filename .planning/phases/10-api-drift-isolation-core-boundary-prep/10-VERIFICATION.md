---
phase: 10
status: passed
updated: 2026-03-14
---

# Phase 10 Verification

## Scope

本轮验证覆盖 `10-01` ~ `10-04` 的完整执行结果：

- protocol boundary 对高漂移 REST family 的 canonicalization 收口
- auth/session formal contract 与 HA adapter 降耦
- `core` formal surface 与 HA runtime home 的继续分离
- roadmap / requirements / state / baseline / review docs / replay / meta guards 的同轮同步

## Commands

- `uv run ruff check custom_components/lipro tests`
- `uv run pytest -q -x tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/core/test_auth.py tests/core/test_init.py tests/flows/test_config_flow.py tests/meta/test_modularization_surfaces.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_governance_guards.py tests/meta/test_protocol_replay_assets.py tests/test_coordinator_public.py tests/core/test_diagnostics.py tests/core/test_system_health.py`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`

## Result

- `10-01` 已验证：`rest.device-list`、`rest.device-status`、`rest.mesh-group-status` 的 canonical contract / replay evidence 均已建立，API drift 优先打在 boundary proof。
- `10-02` 已验证：`AuthSessionSnapshot` 成为 formal auth/session truth，`config_flow.py` / `entry_auth.py` 不再直接依赖 raw login dict。
- `10-03` 已验证：`custom_components/lipro/core/__init__.py` 已不再导出 `Coordinator`，`coordinator_entry.py` 保持唯一 runtime-home public surface，control adapters 继续通过 `runtime_access` 协作。
- `10-04` 已验证：`ROADMAP.md`、`REQUIREMENTS.md`、`STATE.md`、baseline / review docs、phase docs、fixture README 与 meta guards 已全部切到 completed / passed 口径。
- `ruff`、targeted regression suite、architecture policy check 与 file-matrix check 全部通过。

## Requirement Mapping

- `ISO-01`：`rest.device-list@v1`、`rest.device-status@v1`、`rest.mesh-group-status@v1` 已在 `custom_components/lipro/core/protocol/boundary/rest_decoder.py` 与 `custom_components/lipro/core/protocol/contracts.py` 固定 canonical truth；`tests/core/api/test_protocol_contract_matrix.py`、`tests/core/api/test_protocol_replay_rest.py`、`tests/core/mqtt/test_protocol_replay_mqtt.py` 覆盖。
- `ISO-02`：`custom_components/lipro/core/auth/manager.py::AuthSessionSnapshot` 成为 formal contract；`tests/core/test_auth.py`、`tests/core/test_init.py`、`tests/flows/test_config_flow.py` 覆盖。
- `ISO-03`：`custom_components/lipro/core/__init__.py` 不再把 `Coordinator` 作为 core truth 输出；`tests/meta/test_modularization_surfaces.py`、`tests/meta/test_public_surface_guards.py`、`tests/test_coordinator_public.py` 覆盖。
- `ISO-04`：governance docs、replay README、meta guards 与 phase summaries 已同步；`tests/meta/test_governance_guards.py`、`tests/meta/test_protocol_replay_assets.py`、`tests/meta/test_dependency_guards.py` 覆盖。

## Final Verdict

## VERIFICATION PASSED

Phase 10 已完成 north-star 所要求的 boundary-first hardening：
未来若真的做 CLI / other host，可直接复用 formal boundary/auth/device nucleus，
而不需要把 HA runtime 再次拆成新的正式 root。
