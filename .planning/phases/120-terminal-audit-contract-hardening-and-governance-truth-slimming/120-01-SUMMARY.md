# Plan 120-01 Summary

## What changed

- `custom_components/lipro/runtime_types.py` 新增命名 typed carrier（`CommandProperties`、`ProtocolDiagnosticsSnapshot`），让 runtime/service-facing protocol 不再暴露裸 `list[dict[str, str]]` folklore。
- `custom_components/lipro/services/contracts.py` 现在承载 `send_command` strict normalization helper；`custom_components/lipro/services/command.py` 删除平行手写类型闸门，只调用 schema-owned truth。
- `custom_components/lipro/control/runtime_access.py` 的 snapshot/device degradation fallback 收回 formal helper（`get_runtime_device_mapping()` / `is_runtime_device_mapping_degraded()`），不再直接依赖 raw coordinator device field。
- focused regressions 已同步到 `tests/core/test_runtime_access.py`、`tests/services/test_service_resilience.py`、`tests/meta/test_runtime_contract_truth.py`。

## Outcome

- `ARC-32`：runtime/service contract 收紧完成，public protocol carrier 更明确。
- `HOT-52`：`send_command` validation 已回到单一 schema 真源。
- `TST-42`：focused runtime/service regressions 全绿。
