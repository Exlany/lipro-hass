---
phase: 10-api-drift-isolation-core-boundary-prep
plan: "01"
status: completed
completed: 2026-03-14
requirements:
  - ISO-01
  - ISO-04
---

# Summary 10-01

## Outcome

- `custom_components/lipro/core/protocol/boundary/rest_decoder.py` 已新增并接线 `rest.device-list`、`rest.device-status`、`rest.mesh-group-status` 三个高漂移 REST family。
- `custom_components/lipro/core/protocol/contracts.py` 已提供 `normalize_device_list_page()`、`normalize_device_status_rows()`、`build_device_status_map()`、`normalize_mesh_group_status_rows()` 等 canonical helpers。
- runtime consumers 已迁出 vendor envelope 解析：`custom_components/lipro/core/coordinator/orchestrator.py` 与 `custom_components/lipro/core/coordinator/runtime/device/snapshot.py` 只消费 canonical page / rows / status map。
- `tests/fixtures/api_contracts/` 与 `tests/fixtures/protocol_replay/rest/` 已补齐对应 authority fixtures / replay manifests，让 drift 优先失败在 boundary proof。

## Verification

- `uv run pytest -q -x tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_protocol_replay_rest.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/test_coordinator_integration.py tests/core/api/test_api_status_endpoints.py tests/core/mqtt/test_protocol_replay_mqtt.py`
- Result: `72 passed`

## Governance Notes

- `LiproProtocolFacade.get_device_list` 仍保留显式 compat wrapper，但 authority truth 已切到 `rest.device-list@v1` + canonical catalog page。
- 本计划关闭的是 boundary leakage，不是一次性删除全部 compat helper；remaining seams 继续由 residual / kill gate 计数。
