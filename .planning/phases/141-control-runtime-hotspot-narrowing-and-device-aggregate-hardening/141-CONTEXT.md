# Phase 141 Context

**Gathered:** 2026-04-02
**Status:** planning-ready candidate / route-pending
**Current route note:** 当前 active route 仍停在 `Phase 140 planning-ready`；本目录只把下一阶段的代码结构热点整理成可规划资产，不回写 `.planning/ROADMAP.md`、`.planning/STATE.md` 或其他 route selector。

## Goal

把 repo-wide 深审已经反复浮现、但尚未被正式 phase charter 化的结构热点，收敛为一个单独的 code-facing narrowing phase：

- 继续收窄 `service_router` family 的 layering，不重开第二 control root；
- 停止 `service_router.py` 的 underscore helper / imported collaborator outward leakage；
- 把 `runtime_types.py` 的 breadth 从“sanctioned formal home”继续压回更窄、可解释、可验证的 contract topology；
- 收紧 `core/device/device.py` 的 aggregate 宽面与 side-car 清理语义；
- 降低 `entry_root_support.py` 的 lazy import / string-module-name 维护税，同时保住 `__init__.py` 现有的按调用时取依赖工厂语义与测试 patchability。

## Why This Exists Now

- `Phase 140` 的 context 已把这批问题登记为 additional audit findings，但 `.planning/ROADMAP.md` 已明确把 `Phase 140` 锁定为 release/governance/docs freshness；再把 control/runtime/device refactor 混入其中，会直接污染当前 route truth。
- `Phase 123`、`Phase 125`、`Phase 138`、`Phase 103` 与 `Phase 137` 分别解决了 `service_router` family reconvergence、`runtime_types` duplicate truth、support naming guard、root adapter thinning 与 device/observability 第一轮热点；现在剩下的是“正确架构已存在，但 formal homes 仍过宽”的 second-pass narrowing。
- `README.md`、`README_zh.md` 与 `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md` 已把仓库定位成 bilingual public-first-hop + contributor-routable 项目。若内部仍依赖 underscore seam、string module names 与 helper folklore，未来开源维护与双语说明都要继续背“只能靠口头历史解释”的税。

## Inputs

- `.planning/ROADMAP.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/codebase/ARCHITECTURE.md`
- `.planning/codebase/CONCERNS.md`
- `docs/developer_architecture.md`
- `README.md`
- `README_zh.md`
- `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md`
- `custom_components/lipro/control/service_router.py`
- `custom_components/lipro/control/service_router_handlers.py`
- `custom_components/lipro/control/service_router_support.py`
- `custom_components/lipro/runtime_types.py`
- `custom_components/lipro/core/device/device.py`
- `custom_components/lipro/control/entry_root_support.py`
- `custom_components/lipro/__init__.py`
- `tests/core/test_init_service_handlers_device_resolution.py`
- `tests/core/test_init_schema_validation.py`
- `tests/services/test_services_registry.py`
- `tests/core/test_entry_root_wiring.py`

## Structural Targets

### 1. Service-router layering 再收窄

- `service_router.py` 仍在模块导入时绑定 logger、redaction、serial pattern、device getter 与 developer getter。
- `service_router_handlers.py` 同时承担 public callback family、service-layer collaborator casting、diagnostics family re-export。
- `service_router_support.py` 继续同时暴露 raw helper、builder helper 与 iterator helper。

本 phase 应把“public shell / non-diagnostics family / diagnostics family / inward support”四层的边界再次讲清楚，但不能推翻 `Phase 123` 已冻结的 single non-diagnostics handler home。

### 2. Underscore helper leakage 清点并收口

- `service_router.py` 的 `__all__` 仍导出 `_get_device_and_coordinator`、`_summarize_service_properties`、`async_get_clientsession`、`get_anonymous_share_manager`。
- 现有测试已直接 import 或 patch 这些名字，说明 helper seam 已从“内部实现细节”退化成事实上的 outward patch surface。

本 phase 需要把测试依赖迁回更诚实的 sanctioned seam，而不是继续扩大 router root 的 patch API。

### 3. `runtime_types.py` breadth 再拆分

- `runtime_types.py` 仍同时承接 runtime coordinator、schedule mesh、command service、protocol diagnostics、telemetry facade、auth service 等多类 protocol。
- 它已不是 duplicated truth，但仍是跨 control / runtime / platform / services 的宽面 formal home。

本 phase 应研究并执行“缩 breadth 但不制造第二份真源”的拆分策略，尤其要避免重新引入循环依赖或 shadow contracts。

### 4. Device aggregate 宽面与 side-car 语义收紧

- `LiproDevice` 仍提供大面积 `_component_property()` / `_component_method()` outward relay。
- aggregate 内仍混合 canonical state、extra-data side-car、MQTT freshness timestamp 与 `outlet_power_info` legacy 清理逻辑。

本 phase 不追求重写 device model，而是把“哪些仍应属于 aggregate formal surface、哪些应退回 state/extras/runtime collaborator”正式收紧。

### 5. Entry-root lazy import tax 下降

- `entry_root_support.py` 仍以 string module names + generic `load_module()` + builder wrappers 形式承接 root adapter wiring。
- `custom_components/lipro/__init__.py` 再把这些 builder alias 成模块级 callable，并继续向 `entry_root_wiring.py` 传 `load_module` 与 controller module name。

本 phase 需要减少维护者在 root entry path 上的跨文件跳跃和字符串推理成本，但不能破坏 `AGENTS.md` 明确保护的 factory-style setup 语义。

## Non-Goals

- 不在本次 planning-ready 准备中修改任何生产代码。
- 不回写 `.planning/ROADMAP.md`、`.planning/STATE.md`、`.planning/REQUIREMENTS.md`、`.planning/MILESTONES.md` 等 route 文档。
- 不把 `service_router_diagnostics_handlers.py` 压回主 handlers 文件。
- 不把 `runtime_types.py` 简单切碎成多份 owner 不明的 helper 文件。
- 不把 `LiproDevice` 改成新的 inheritance / mixin 叙事。

## Exit Truth

- `Phase 141` 的 plan 能明确拆成若干 code-facing waves，而不是继续以 audit footnote 形式漂浮在 `Phase 140` 附注里。
- service-router family 的 outward/public seam、support seam、test patch seam 有明确边界与成功标准。
- `runtime_types.py` 的 narrowing 目标不再停留在“文件太宽”，而是明确到可执行的 contract family 拆分顺序与 dependency guard 要求。
- `LiproDevice` 的 aggregate narrowing 不再停留在“device 太大”，而是明确到 delegate wall、extra-data side-car、MQTT freshness 与 outlet-power cleanup 的取舍边界。
- `entry_root_support.py` / `__init__.py` 的 lazy import tax 被定义成可验证问题，而不是继续依赖历史语境解释。
- 当前 route truth 维持不变；只有当后续显式接受 `Phase 141` 进入 roadmap 时，才更新 selector docs。

## Suggested Validation Surface For Future Planning

- `uv run pytest tests/core/test_init_service_handlers_*.py tests/services/test_services_registry.py tests/core/test_control_plane.py -q`
- `uv run pytest tests/core/test_entry_root_wiring.py tests/core/test_init*.py -q`
- `uv run pytest tests/core/device tests/core/test_outlet_power*.py tests/platforms/test_sensor.py tests/platforms/test_entity_behavior.py -q`
- `uv run pytest tests/meta/test_runtime_contract_truth.py tests/meta/dependency_guards_service_runtime.py tests/meta/test_phase123_service_router_reconvergence_guards.py tests/meta/test_phase103_root_thinning_guards.py -q`
- `uv run ruff check custom_components/lipro/control custom_components/lipro/runtime_types.py custom_components/lipro/core/device tests`
