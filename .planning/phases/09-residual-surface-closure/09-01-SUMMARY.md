---
phase: 09-residual-surface-closure
plan: "01"
status: completed
completed: 2026-03-14
requirements:
  - RSC-01
  - RSC-02
---

# Summary 09-01

## Outcome

- `LiproProtocolFacade` 与 `LiproMqttFacade` 已移除 `__getattr__` / `__dir__`，protocol root contract 改为显式 wrapper + child façade 组合，不再由 REST child 隐式定义 formal root surface。
- `custom_components/lipro/__init__.py`、`config_flow.py`、`core/__init__.py` 与 `core/mqtt/__init__.py` 的 legacy protocol exports 已关闭；`core.api.LiproClient` 仍保留为显式 compat shell。
- MQTT integration tests 已改为显式访问 `raw_client` compat seam，避免再用隐式 fallback 把 concrete transport 合法化为 formal public surface。

## Verification

- `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/integration/test_mqtt_coordinator_integration.py tests/meta/test_public_surface_guards.py`

## Governance Notes

- `LiproProtocolFacade.get_device_list` 仍保留为显式 compat wrapper，后续 cleanup phase 可继续删除。
- `LiproMqttFacade.raw_client` 已降级为显式 test/compat seam，并在 kill list 中继续计数。
