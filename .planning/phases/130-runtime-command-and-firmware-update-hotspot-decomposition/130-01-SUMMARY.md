---
phase: 130-runtime-command-and-firmware-update-hotspot-decomposition
plan: "01"
summary: true
---

# Plan 130-01 Summary

## Completed

- `custom_components/lipro/core/coordinator/runtime/command_runtime.py` 已把 `get_runtime_metrics()`、`_build_trace_for_request()`、`_handle_command_dispatch_result()` 与 `_verify_delivery()` 收薄为 orchestration wrapper，root 继续只承担单一 `CommandRuntime` 正式主链。
- `custom_components/lipro/core/coordinator/runtime/command_runtime_support.py` 现吸收 request-trace、dispatch normalization 与 runtime metrics shaping；`custom_components/lipro/core/coordinator/runtime/command_runtime_outcome_support.py` 现吸收 verify-delivery result normalization 与 canonical failure recording。
- 新增 `tests/core/coordinator/runtime/test_command_runtime_support_helpers.py`，并扩 `tests/core/coordinator/runtime/test_command_runtime_orchestration.py` / `tests/core/coordinator/runtime/test_command_runtime_outcome_support.py`，直接冻结 push-failed、missing `msgSn`、auth/generic API error、verify-failed 与 success-finalize seams。

## Outcome

- `CommandRuntime` 仍是唯一 outward runtime orchestration home；本轮只做 inward split，没有引入第二条 runtime story、compat shell 或额外 public surface。
- runtime-half 已满足本 phase 的 `ARC-41` / `HOT-60` 范围：multi-topic failure/trace/verify 逻辑被压回更窄 helper seam，且 focused proofs 已能直接拦截回胖或漂移。
