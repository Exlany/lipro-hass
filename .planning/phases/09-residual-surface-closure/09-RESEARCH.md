# Phase 9 Research

**Phase:** `9 Residual Surface Closure`
**Source inputs:** `docs/archive/COMPREHENSIVE_AUDIT_2026-03-13.md`, `.planning/reviews/RESIDUAL_LEDGER.md`, `.planning/baseline/PUBLIC_SURFACES.md`
**Date:** 2026-03-14

## Findings

### 1. `Phase 9` 的核心不是“再做一轮 cleanup”，而是把 residual surface 变成可裁决 contract

审查报告里剩下的问题并非随机散点，而是同一类架构偏航：
- protocol root 仍允许 child surface 反向定义 formal contract；
- concrete transport 与 legacy public names 仍在 formal public surface 边缘游走；
- runtime 仍把 live mutable state 直接暴露给上层；
- outlet power 仍使用 `extra_data` 旁写，而不是正式 primitive。

因此 `09` 的最佳定位是：
- **surface narrowing**（收窄 formal surface）
- **compat quarantine**（把 compat seam 收进显式过渡家园）
- **runtime truth normalization**（让 power/runtime 读写路径回到正式 primitive）
- **governance enforcement**（让 residual 不会再次扩散）

### 2. protocol root 的正确修复方向是“显式 surface + 显式 child access”，而不是继续依赖委托魔法

`custom_components/lipro/core/protocol/facade.py` 当前的 `__getattr__` / `__dir__` 让 `LiproProtocolFacade` 的 formal contract 由 `LiproRestFacade` 的 child members 隐式决定，这与“唯一正式 root 可裁决”冲突。

最优修复方向：
- `LiproProtocolFacade` 只暴露显式声明的 root-level contract；
- REST child 通过 `.rest`，MQTT child 通过 `.mqtt` 访问；
- 若短期必须保留少量 legacy entrypoint，应把它们收进显式 compat home，而不是继续让 root class 自动透传；
- `LiproMqttFacade.raw_client` 若继续保留，也只能是明确标注的 compat/test seam，不能再出现在 formal public-surface 叙事里。

### 3. compat export 清理必须与 PUBLIC_SURFACES / KILL_LIST 一起做，否则“删了代码，没删语义”

报告中指出的 compat export 残留位于：
- `custom_components/lipro/__init__.py`
- `custom_components/lipro/config_flow.py`
- `custom_components/lipro/core/api/__init__.py`
- `custom_components/lipro/core/__init__.py`
- `custom_components/lipro/core/mqtt/__init__.py`

这些入口并不一定都要在 `09` 完全物理删除，但必须完成至少一项：
1. 从 formal public surface 中移除；
2. 降级到显式 compat alias / compat module；
3. 在治理真源中登记 remaining delete gate。

否则即便生产路径已切到 `LiproProtocolFacade`，历史名字仍会继续定义外界认知。

### 4. runtime 最优解不是“返回一个 dict 拷贝”，而是稳定的只读 view / service contract

`Coordinator.devices` 目前直接返回 `self._state.devices`，这意味着上层可直接拿到 live mutable dict。

短期最优策略应满足两点：
- 上层 consumers 还能高效遍历、索引设备；
- 但不能通过 public property 直接修改 runtime registry。

因此优先级建议：
1. **正式 service / read-only view**（最佳）
2. `MappingProxyType` / read-only mapping wrapper（可接受）
3. 每次返回 dict copy（最保守，但可能破坏 identity / 性能预期）

本 phase 应先收口 formal public contract；是否引入更强 typed view，可作为实现细节在计划内裁决。

### 5. outlet power 必须摆脱 `extra_data` formal-path 身份，但需要迁移桥接

`sensor.py`、`diagnostics_surface.py`、测试和 coordinator 现都以 `device.extra_data["power_info"]` 为读取基础。

因此最优实施顺序不是“一刀删掉 `extra_data`”，而是：
- 先建立 formal primitive（例如 device-level/property-level runtime primitive）；
- 把 coordinator/outlet-power runtime 的写路径切到该 primitive；
- 把 sensor / diagnostics / tests 的读路径切到同一 primitive；
- 只在必要的迁移桥接期保留 `extra_data` read adapter 或同步镜像；
- 最终由 governance residual / kill gate 决定何时彻底删除桥接。

### 6. `Phase 9` 的 governance/test hooks 必须与代码改动同步，不可延后到“下一轮文档 cleanup”

至少需要同步的治理真源：
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/baseline/AUTHORITY_MATRIX.md`（若 outlet power truth home 发生变化）
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`

至少需要同步的回归/守卫：
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_governance_guards.py`
- protocol / MQTT / coordinator / outlet power / sensor 的 targeted tests

### 7. 哪些问题应在 `09` 真修，哪些只能继续作为显式 residual

**本 phase 必须真修：**
- `LiproProtocolFacade` root contract 的 implicit delegation
- `Coordinator.devices` live mutable 暴露
- outlet power 正式路径仍靠 `extra_data` 旁写
- formal public surfaces 与 compat exports 的不一致

**本 phase 可保留为显式 residual：**
- `LiproClient` / `LiproMqttClient` 作为历史 compat name 的极小范围保留（若仍有 tests / specific seams 依赖）
- `raw_client` 若无法一步删除，可下沉为仅限 tests/compat adapters 的受控 seam

**必须与实现同步移动的 hooks：**
- public surface guard
- governance ledger / kill gate
- diagnostics / sensor / helper 读取路径
- integration tests 中直接依赖 `raw_client` 或 `coordinator.devices` 语义的断言

## Recommended Outputs

### 1. Planning artifacts

建议生成：
- `09-01-PLAN.md` — protocol root + compat surface narrowing
- `09-02-PLAN.md` — runtime read-only view + outlet power primitive
- `09-03-PLAN.md` — governance residual sync + regression guards
- `09-ARCHITECTURE.md`
- `09-VALIDATION.md`

### 2. Likely production files

高概率涉及：
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/protocol/__init__.py`
- `custom_components/lipro/__init__.py`
- `custom_components/lipro/config_flow.py`
- `custom_components/lipro/core/api/__init__.py`
- `custom_components/lipro/core/__init__.py`
- `custom_components/lipro/core/mqtt/__init__.py`
- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/core/coordinator/outlet_power.py`
- `custom_components/lipro/sensor.py`
- `custom_components/lipro/control/diagnostics_surface.py`
- `custom_components/lipro/helpers/platform.py`

### 3. Likely tests / guards

高概率涉及：
- `tests/core/mqtt/test_mqtt.py`
- `tests/integration/test_mqtt_coordinator_integration.py`
- `tests/core/test_coordinator.py`
- `tests/core/test_outlet_power.py`
- `tests/platforms/test_sensor.py`
- `tests/test_coordinator_public.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_governance_guards.py`

## Validation Architecture

### Validation dimensions

1. **Protocol surface**：formal root 是否只暴露显式 contract，child members 不再隐式定义 root
2. **Compat quarantine**：legacy names / raw transport 是否被限制在显式 compat seam
3. **Runtime immutability**：public runtime access 是否不再暴露 live mutable dict
4. **Power truth convergence**：outlet power 写入与读取是否统一到同一 primitive
5. **Governance sync**：public surfaces / residual / delete gate / verification evidence 是否与代码一致

### Recommended quick run

- `uv run pytest -q tests/core/mqtt/test_mqtt.py tests/core/test_coordinator.py tests/core/test_outlet_power.py tests/platforms/test_sensor.py tests/test_coordinator_public.py tests/meta/test_public_surface_guards.py`

### Recommended full suite

- `uv run ruff check <touched-paths>`
- `uv run pytest -q`

### Phase-specific proof expectations

- protocol surface 改动必须有 targeted tests + public-surface guard proof
- runtime read-only 改动必须证明 consumers 仍可读取，但无法通过 public contract 改写 registry
- outlet power primitive 改动必须证明 coordinator / sensor / diagnostics 看到的是同一 truth
- governance 回写必须让 `RESIDUAL_LEDGER / KILL_LIST / PUBLIC_SURFACES / VERIFICATION_MATRIX` 与代码事实对齐

## Final Arbitration

`Phase 9` 的最佳实现不是“把所有 compat 一次删光”，而是：
- 先把 formal root / formal runtime / formal truth path 收口正确；
- 把确实删不掉的历史名字压缩到显式 compat seam；
- 用治理与守卫把这些 seam 变成可计数、可删除、不可回流的过渡层。

这比“继续保留隐式 delegation + live mutable dict + extra_data 旁写”更符合北极星，也比“激进删除导致大面积回归”更稳健。
