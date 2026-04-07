# 52-01 Summary

## Outcome

- `custom_components/lipro/core/protocol/rest_port.py` 已从单一宽口 `_RestFacadePort` 收口为 concern-local port family，并新增 `ProtocolRestPortFamily` / `bind_protocol_rest_port_family()` 作为 protocol root 的 child-facing contract binder。
- `custom_components/lipro/core/protocol/facade.py` 不再直接承载整串 REST forwarding methods；这些 formal methods 已迁到 support-only `custom_components/lipro/core/protocol/protocol_facade_rest_methods.py`，而 `LiproProtocolFacade` 继续保留唯一 protocol-plane root 身份与稳定 public surface。
- `custom_components/lipro/core/protocol/mqtt_facade.py` 新增 protocol-owned MQTT bind 与 diagnostics snapshot helper，使 MQTT attach / diagnostics 的机械拼装从 root body inward localization，但 formal entrypoints 仍留在 `LiproProtocolFacade`。
- `tests/core/api/test_protocol_contract_matrix.py` 已补上 Wave 1 结构守卫，锁定 protocol root 不再回到单一宽口 `_RestFacadePort` 故事。

## Validation

- `uv run pytest tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_transport_and_schedule.py tests/meta/test_public_surface_guards.py -q`

## Notes

- 本计划只收窄 protocol root 对 child façade 的可见面，不引入新 façade / wrapper / root。
- 新增 `custom_components/lipro/core/protocol/protocol_facade_rest_methods.py` 仍是 support-only seam；public exports 尚未变化，后续治理回写留给 `52-03` 统一冻结。
