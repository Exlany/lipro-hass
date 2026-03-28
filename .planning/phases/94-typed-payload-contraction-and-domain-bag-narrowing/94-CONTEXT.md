# Phase 94: Typed payload contraction and domain-bag narrowing - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning

<domain>
## Phase Boundary

`Phase 94` 只处理 typed seam / mapping seam / domain bag honesty，不做大规模 hotspot 拆分：先把最容易继续扩散的 `Any` 与 broad mapping contract 收口，让后续 `Phase 95 -> 97` 的 inward split / sanitizer burn-down 建立在更诚实的类型边界之上。

当前 repo-wide audit 已确认以下 seam 仍值得立刻处理：
- `custom_components/lipro/domain_data.py` 仍以 `dict[str, Any]` 作为 domain bag。
- `custom_components/lipro/control/diagnostics_surface.py` 与 `custom_components/lipro/diagnostics.py` 仍保留宽口 diagnostics payload / redaction callback typing。
- `custom_components/lipro/entities/base.py` 仍使用 `CoordinatorEntity[Any]`。
- `custom_components/lipro/core/api/{command_api_service,status_fallback,transport_core}.py` 仍保留 broad mapping / callback / request context seam。
- `custom_components/lipro/core/utils/property_normalization.py` 仍以 `Mapping[str, Any] -> dict[str, Any]` 作为默认 contract。
</domain>

<decisions>
## Implementation Decisions
- **D-01:** 优先复用已有正式 typed contract（例如 `JsonObject` / `JsonValue` / runtime protocol surface），不要再造 shadow alias 或 helper-owned second story。
- **D-02:** `domain_data.py` 的目标不是把所有 value 强行变成超窄 union，而是先把 `Any` 退到 `object` / 诚实 bag contract，再由具体 access home 保持局部 narrowing。
- **D-03:** `entities/base.py` 的 generic 收窄必须围绕正式 `LiproRuntimeCoordinator` protocol，不得把 entity shell 与 coordinator internals 重新耦合。
- **D-04:** `transport_core.py` 的返回类型必须与实际 mapping-request contract 诚实对齐；若 contract 只接受 mapping，就在 transport core 内直接验证，而不是把不诚实 typing 留给上游。
- **D-05:** `status_fallback.py` 与 `command_api_service.py` 的 callback / payload alias 必须缩到 object / `JsonObject` / `logging.Logger` 这类明确 contract，不继续保留 `Any` 兜底。
- **D-06:** 至少补一条 focused regression 证明 `transport_core` / typed helper 的 contract 更诚实，避免只做静态收窄而无行为证明。
</decisions>

<canonical_refs>
## Canonical References
- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `custom_components/lipro/domain_data.py`
- `custom_components/lipro/control/diagnostics_surface.py`
- `custom_components/lipro/diagnostics.py`
- `custom_components/lipro/entities/base.py`
- `custom_components/lipro/core/api/command_api_service.py`
- `custom_components/lipro/core/api/status_fallback.py`
- `custom_components/lipro/core/api/transport_core.py`
- `custom_components/lipro/core/api/types.py`
- `custom_components/lipro/runtime_types.py`
- `custom_components/lipro/core/utils/property_normalization.py`
- `tests/core/api/test_api_command_service.py`
- `tests/core/api/test_api_status_service_fallback.py`
- `tests/core/api/test_api_transport_executor.py`
- `tests/core/test_property_normalization.py`
- `tests/core/test_diagnostics.py`
- `tests/core/test_diagnostics_config_entry.py`
- `tests/core/test_diagnostics_device.py`
</canonical_refs>
