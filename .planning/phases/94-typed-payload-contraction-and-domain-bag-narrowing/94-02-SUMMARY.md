---
phase: 94-typed-payload-contraction-and-domain-bag-narrowing
plan: "02"
status: completed
completed: 2026-03-28
---

# Summary 94-02

**diagnostics surface 与 REST helper mapping surface 已统一回到 JSON-like / `JsonObject` / `logging.Logger` 的正式契约，transport 现在会诚实拒绝非 mapping JSON 响应。**

## Outcome

- `custom_components/lipro/control/diagnostics_surface.py` 与 `custom_components/lipro/diagnostics.py` 现在围绕 `JsonObject` / JSON-like diagnostics value 构建 payload，不再公开 `dict[str, Any]` / callback-return-`Any` 作为正式 surface。
- `custom_components/lipro/core/api/command_api_service.py` 与 `custom_components/lipro/core/api/status_fallback.py` 统一复用 `JsonObject` / `object` / `logging.Logger`，并保持 fallback 行为不变。
- `custom_components/lipro/core/api/transport_core.py` 现在在 `execute_request()` 内部直接调用 `require_mapping_response()`，把 formal mapping contract 与真实运行行为对齐。
- `tests/core/api/test_api_transport_executor.py` 新增 focused regression，证明 list-shaped JSON 会被 transport 层显式拒绝，而不是靠上游默默兜底。

## Verification

- `uv run pytest -q tests/core/api/test_api_command_service.py tests/core/api/test_api_status_service_fallback.py tests/core/api/test_api_transport_executor.py tests/core/test_diagnostics.py tests/core/test_diagnostics_config_entry.py tests/core/test_diagnostics_device.py`
- `uv run ruff check custom_components/lipro/control/diagnostics_surface.py custom_components/lipro/diagnostics.py custom_components/lipro/core/api/command_api_service.py custom_components/lipro/core/api/status_fallback.py custom_components/lipro/core/api/transport_core.py tests/core/api/test_api_transport_executor.py`

## Task Commits

- None — per user instruction, this workspace keeps the phase uncommitted.

## Deviations from Plan

- diagnostics redaction implementation本体没有被大规模改写；本轮只收口正式 surface typing，并通过 adapter 级 coercion/cast 保持现有 redaction 行为与输出形状稳定。

## Next Readiness

- 94-03 现在可以把 Phase 94 的 typed seam shrink 冻结成 focused guard、verification proof 与 route-truth closeout，而不再担心 transport / diagnostics surface 仍有宽口残留。
