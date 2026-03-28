---
phase: 94-typed-payload-contraction-and-domain-bag-narrowing
plan: "01"
status: completed
completed: 2026-03-28
---

# Summary 94-01

**`DomainData`、entry options snapshot、anonymous-share registry、entity coordinator generic 与 property normalization 已从 broad `Any` seam 收口到更诚实的 bag / object / formal-runtime contract。**

## Outcome

- `custom_components/lipro/domain_data.py` 现在把 domain bag 定义为 `dict[str, object]`，并通过显式 coercion 处理 `hass.data[DOMAIN]` 受污染场景。
- `custom_components/lipro/entry_options.py` 与 `custom_components/lipro/core/anonymous_share/registry.py` 不再隐式信任 `setdefault()` 返回值；snapshot store 与 scoped manager store 都通过局部 narrowing 读取。
- `custom_components/lipro/entities/base.py` 现在固定为 `CoordinatorEntity[LiproRuntimeCoordinator]`，不再向实体壳传播 `CoordinatorEntity[Any]`。
- `custom_components/lipro/core/utils/property_normalization.py` 现在公开 `object` / `NormalizedPropertyMap` 的诚实 contract，同时保持 canonical-key precedence 行为不变。

## Verification

- `uv run pytest -q tests/core/test_property_normalization.py tests/core/test_entry_update_listener.py tests/core/test_init_edge_cases.py`
- `uv run ruff check custom_components/lipro/domain_data.py custom_components/lipro/entry_options.py custom_components/lipro/core/anonymous_share/registry.py custom_components/lipro/entities/base.py custom_components/lipro/core/utils/property_normalization.py tests/core/test_property_normalization.py`

## Task Commits

- None — per user instruction, this workspace keeps the phase uncommitted.

## Deviations from Plan

- `DomainData` 没有被过度收紧为大 union；本轮只把 `Any` 退到诚实 bag contract，并把具体 narrowing 留在 access home，避免制造新一层 shadow truth。

## Next Readiness

- 94-02 可以在同一条 typed seam 基线上继续收口 diagnostics / REST mapping contract，而不必再回头修补 domain-bag honest story。
