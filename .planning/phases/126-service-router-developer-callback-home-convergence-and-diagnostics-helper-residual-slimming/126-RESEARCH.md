# Phase 126 Research

## Audit Carry-Forward

- `services/diagnostics/helpers.py` 仍保留 stable shell + mechanics alias 混合形态；其中 `_collect_coordinator_capability_results` 与 `helper_support.py` 重复且未再被消费。
- `services/diagnostics/handlers.py` 仍通过 `helpers.py` 取用 `_coerce_service_*` 与 `_get_required_service_string` 这类 pure mechanics helper；这些 helper 的 canonical home 已在 `helper_support.py`。
- `developer_router_support.py` 在非 entry-specific branch 中仍手写一次 coordinators freeze + lambda iterator，语义与 `build_developer_runtime_coordinator_iterator()` 重复。

## Decision

- 本 phase 只做 low-risk inward thinning：不碰 public service router topology，不改 diagnostics public imports，不扩张 helper 抽象。
- 先把 handler-facing mechanics 指回 `helper_support.py`，删除未使用 duplicate helper，并统一 developer diagnostics runtime iterator builder。
- 更高风险的 `runtime_access` typed telemetry / de-reflection 收口留给 `Phase 127`，避免在同一 phase 混合两类 seam。
