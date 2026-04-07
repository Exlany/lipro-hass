# 35-02 Summary

## Outcome

- `LiproProtocolFacade` 现通过 `rest_port.py` 与 `mqtt_facade.py` 组合 child façades；`_rest_port` forwarding ballast 已从 root body 退出。
- touched public-surface / dependency / residual truth 已同步回写，single protocol-root story 保持不变。

## Validation

- `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/meta/test_public_surface_guards.py`
