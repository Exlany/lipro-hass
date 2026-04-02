# Phase 141 Research

**Researched:** 2026-04-02
**Confidence:** HIGH
**Scope posture:** planning-ready only；不改生产代码，不改 current route docs。

## Executive Read

这批热点的共同特征，不是“架构方向错了”，而是“上一轮 phase 已把 formal home 说清楚，但 formal home 仍然过宽、过漏、过依赖历史语境”。`service_router` family 已在 `Phase 123` 完成 reconvergence，`runtime_types.py` 已在 `Phase 125/138` 解决 duplicate truth 与反向依赖，`entry_root_support.py` 已在 `Phase 103` 从根入口中抽出，`device.py` 也在 `Phase 137` 被识别为 outward relay wall。下一步不再是大重写，而是 second-pass narrowing。

从开源维护与双语文档角度看，这一步现在必须做：仓库已经公开承诺 bilingual docs first hop、contributor-facing change family map 与长期 governance guards；如果内部结构仍要求维护者理解 underscore patch seam、string module names 与 support/helper 的口头历史，外部贡献者与未来翻译/审阅者就无法低成本建立正确心智模型。

## Key Evidence

| Hotspot | 关键证据 | 结构成本 | 研究结论 |
| --- | --- | --- | --- |
| service-router layering | `custom_components/lipro/control/service_router.py:29-45` 在模块导入时绑定 `_SERIAL_PATTERN`、`_log_send_command_call`、`_get_device_and_coordinator`；`custom_components/lipro/control/service_router_handlers.py:42-53,58-83,210-225` 同时承接 diagnostics re-export、service collaborator casting 与 outward handlers。 | public shell / handler family / diagnostics family / support family 仍靠文件命名和历史记忆区分，认知成本高。 | 下一 phase 应继续 narrow，但必须保留 `Phase 123` 已冻结的 single non-diagnostics handler home，不回退到多 split shells。 |
| underscore helper leakage | `custom_components/lipro/control/service_router.py:226-245` 的 `__all__` 直接导出 `_get_device_and_coordinator`、`_summarize_service_properties`、`async_get_clientsession`、`get_anonymous_share_manager`；`tests/core/test_init_service_handlers_device_resolution.py:10` 与 `tests/services/test_services_registry.py:56-62` 已直接消费这些符号。 | underscore/private-ish seam 实际变成事实 public patch surface，测试与实现一起把 leakage 固化。 | 先收紧测试 seam，再收口 router outward exports；否则每次 refactor 都要保留更多 accidental API。 |
| `runtime_types.py` breadth | `custom_components/lipro/runtime_types.py` 长 `354` 行，`ProtocolServiceLike` 覆盖 schedules / diagnostics / OTA / city / cloud，`LiproCoordinator` 同时暴露 auth/device/schedule/mqtt/command/protocol/telemetry；全仓有 `35` 个 Python 文件直接导入 `runtime_types.py`。`.planning/codebase/CONCERNS.md:47-52` 还把它列为 strict typing 下的 typed boundary debt 主要集中点。 | formal home 正确，但 breadth 太宽，任何变更都会同时扰动 control、runtime、platform 与 services。 | 适合做 capability-family 拆分或 plane-local contract extraction，但必须保留 single sanctioned root story，不能简单复制协议。 |
| device aggregate 宽面 | `custom_components/lipro/core/device/device.py:86-170` 含 `76` 个 `_component_property()` / `_component_method()` relay；`device.py:55,68-72,187-195,202-214` 同时承接 `extra_data`、MQTT freshness、outlet-power legacy cleanup 与属性更新。另有 `28` 个测试/代码文件直接实例化 `LiproDevice`。 | aggregate 同时背负 domain truth、projection convenience、runtime freshness 与 side-car 兼容语义，改动 blast radius 大。 | Phase 141 应把 aggregate hardening 放在后段波次，先定义哪些 surface 必须保留，再削减 relay wall。 |
| entry-root lazy import tax | `custom_components/lipro/control/entry_root_support.py:84-210` 使用四个 string module constants、generic `load_module()` 与多层 builder wrapper；`custom_components/lipro/__init__.py:16-27,59-61,137-180` 又将这些 wrapper alias 成根模块 callable，并向 wiring 继续透传 `_load_module` 与 controller module name。 | 维护者需要在 root adapter / support / wiring 三层之间跳转，理解成本高；一旦文档或测试描述不清，就容易重新长出第二套 bootstrap story。 | 必须单独收敛，但要严格保住 `AGENTS.md` 要求的 factory-on-call 行为与 patch-friendly setup。 |

## Why Must This Be The Next Phase

### 1. 为什么现在必须做

- `.planning/ROADMAP.md:53-55` 已说明当前 active milestone 前半段完成 REST/protocol hotspot second pass，后半段只剩 docs/governance freshness；这批代码热点已经是下一个自然承接面，而不是遥远 backlog。
- `.planning/reviews/RESIDUAL_LEDGER.md:27,34,69,679` 多次把 `runtime_types.py`、`entry_auth.py` 一类宽面正式定义为 sanctioned hotspot breadth / carry-forward observation，而不是已关闭问题。继续只写审阅附注，会让“已知结构债”再次退化成 conversation-only TODO。
- `README.md:13-26`、`README_zh.md:13-26` 与 `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md:27-35,73-80` 已把项目对外描述成 docs-first、双语、contributor-routable 的开源入口。若内部仍保留难以命名和难以翻译的 layer/support/helper 迷雾，对未来公共维护者不公平。

### 2. 为什么不能继续混进 Phase 140

- `.planning/ROADMAP.md:90-100` 已把 `Phase 140` 的 success criteria 锁定为 verification path freshness、public changelog scope、support/runbook wording 与 meta guards；这是 docs/governance-only phase。
- 这批热点需要的验证面是 `tests/core/test_init_service_handlers_*.py`、`tests/core/test_entry_root_wiring.py`、`tests/core/device/**`、`tests/meta/test_runtime_contract_truth.py` 等 control/runtime/domain 测试，而不是仅靠 docs/meta guard 即可闭环。
- 若继续混入 `Phase 140`，结果只会有两种坏结果：
  - 让 docs/governance phase 偷偷变成 code refactor phase，route truth 失真；
  - 或为了维持 140 的 scope，只能把这些问题继续写成附注，planning 仍然不 ready。

## Open-source / 国际化维护视角

- bilingual public first hop 已是仓库契约。内部如果存在“`support` 其实是 formal bridge，但又不是 public root”“underscore helper 虽然以下划线命名，却要求测试直接 patch”“root adapter 真实依赖路径要靠 string module names 推理”这类故事，中文和英文文档都很难诚实、低噪声地表达。
- 未来若仓库进入更开放的协作模式，新贡献者首先接触的是 `README*.md`、`CONTRIBUTING.md`、`docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md`。这些入口要求结构命名能直接映射到代码 reality；否则 reviewer 只能靠 oral history 指导“这里虽然叫 support，但你要把它当 formal bridge”。
- maintainer continuity 也受影响。当前 private-access posture 已在文档中说得很诚实，下一步更需要把内部结构成本降下来，避免单维护者记忆成为唯一导航系统。

## Recommended Wave Order

### Wave 1: service-router public seam narrowing

先处理 `service_router.py` / `service_router_handlers.py` / `service_router_support.py` 的 layering 与 underscore leakage：

- 这是当前证据最直接、回报最高的一组热点；
- 可以先把 outward/public seam、test seam 与 inward support seam 讲清楚；
- 还能为后续 runtime/device narrowing 建立更稳的 control-plane contract。

### Wave 2: entry-root lazy import tax slimming

第二波处理 `entry_root_support.py` 与 `custom_components/lipro/__init__.py` 的 bootstrap indirection：

- 仍属 control-plane / root adapter 范畴，和 Wave 1 的 seam hygiene 同类；
- 但要与 service-router 分开，避免同一波同时改两条关键入口链；
- 重点是减少 string module name / wrapper layering，而不是破坏 factory semantics。

### Wave 3: `runtime_types.py` breadth decomposition

第三波进入 root-level contract narrowing：

- 在 control-plane seams 已清楚之后，再拆 `runtime_types.py` 更容易定义稳定 import direction；
- 这一波需要同步 dependency guards、runtime/control/platform importers 与 typing truth；
- 应优先切 capability-family / plane-local contracts，而不是机械按文件大小切碎。

### Wave 4: device aggregate hardening

最后处理 `core/device/device.py`：

- `LiproDevice` 的 blast radius 最大，且最依赖前面几波提供的更清晰 contract boundary；
- 只有在 runtime/control contracts 已变窄后，才能决定哪些 relay 应保留、哪些应退回 `state` / `extras` / runtime collaborator；
- 这一波需要最多 focused tests，因此放在 phase 末段最稳妥。

## Planning Guardrails

- 不要把 `service_router_support.py` 再次合法化为第二 public control root；`Phase 138` 已钉死它是 inward formal bridge home。
- 不要为了缩 `runtime_types.py` 而复制第二份 runtime coordinator protocol；single sanctioned root story 必须保留。
- 不要把 `LiproDevice` 的 narrowing 变成 inheritance / mixin comeback；仓库北极星是显式组合。
- 不要破坏 `AGENTS.md` 明确保护的 `__init__.py` factory-style setup；这不是“顺手可删”的 lazy indirection，而是测试与运行时 contract 的一部分。

## Suggested Validation Focus

- `uv run pytest tests/core/test_init_service_handlers_*.py tests/services/test_services_registry.py tests/core/test_control_plane.py -q`
- `uv run pytest tests/core/test_entry_root_wiring.py tests/core/test_init*.py -q`
- `uv run pytest tests/core/device tests/core/test_outlet_power*.py tests/platforms/test_sensor.py tests/platforms/test_entity_behavior.py -q`
- `uv run pytest tests/meta/test_runtime_contract_truth.py tests/meta/dependency_guards_service_runtime.py tests/meta/test_phase123_service_router_reconvergence_guards.py tests/meta/test_phase103_root_thinning_guards.py -q`
- `uv run ruff check custom_components/lipro/control custom_components/lipro/runtime_types.py custom_components/lipro/core/device tests`

## Confidence Breakdown

- service-router / underscore leakage: HIGH — 代码、`__all__` 与测试依赖都很直接。
- `runtime_types.py` breadth: HIGH — 文件角色、导入扇出与现有 concern ledger 一致。
- device aggregate narrowing: HIGH — relay wall、side-car 清理与测试覆盖面都可量化。
- entry-root lazy import tax: HIGH — root adapter / support / wiring 的分层与 string-module-name 证据明确。
