# Lipro-HASS 全量审查报告（2026-03-13，Phase 9 refreshed 2026-03-14）

> 审查对象：`git ls-files '*.py'` 锁定的 `443` 个 Python 文件  
> 审查基线：`docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`docs/developer_architecture.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md`  
> 审查方式：仓库级守卫与全量测试 + 分区子代理复核 + 主代理重点手审 + 架构/依赖模式扫描  
> 注意：本报告基于**当前工作树**，其中已包含未提交的 `Phase 8` / `Phase 9` 相关工件与治理文档变更。

## 0. 2026-03-14 Phase 9 Closeout Update

- `Phase 9` 已执行完成：`LiproProtocolFacade` / `LiproMqttFacade` 的 implicit delegation 已关闭，protocol formal surface 改为显式 contract。
- `custom_components/lipro/__init__.py`、`config_flow.py`、`core/__init__.py` 与 `core/mqtt/__init__.py` 的 legacy public-name 再导出已收口；`LiproClient` 只剩 `core.api` 显式 compat shell，`LiproMqttFacade.raw_client` 只剩显式 compat/test seam。
- runtime `devices` public surface 已改为 read-only mapping；outlet power 已迁到 `LiproDevice.outlet_power_info` formal primitive，sensor / diagnostics / runtime 统一读取。
- 因此本报告第 `5.1`、`5.3`、`5.4`、`5.5` 节登记的 residual 已在 `Phase 9` 收口或显著缩窄；后续剩余开放项主要是 low-priority hygiene 与显式 delete-gated compat seam。

## 1. 结论先行

- 北极星单一主链**总体保持成立**：正式 protocol root 仍是 `LiproProtocolFacade`，正式 runtime root 仍是 `Coordinator`，`Phase 8` evidence-pack 代码与治理工件在当前工作树中已具备完成态。
- 本轮未发现新的“立即导致主线不可运行”的开放性 P0；但在审查过程中确认并修复了 **3 处高风险真实缺陷**：
  1. MQTT 重连退避在成功连接后未真正复位；
  2. live unsubscribe 失败后不会在同一会话内重试，可能遗留过订阅；
  3. REST 状态轮询绕过 `Coordinator._apply_properties_update()`，跳过命令确认过滤链。
- 自动化证据强：`uv run pytest -q` 当前通过 `2133` 项；架构/治理守卫与 `Phase 9` 收口专项回归均通过。
- 已登记的 protocol/runtime residual surface 已在 `Phase 9` 收口；当前剩余开放项以低优先级 hygiene、模块级缓存/异常可观测性与显式 delete-gated compat seam 为主。


## 1.1 Phase 09 Refresh（2026-03-14）

- `LiproProtocolFacade` / `LiproMqttFacade` 已移除 `__getattr__` / `__dir__`，protocol root contract 改为显式 public surface；protocol 包级 export 也已收窄。
- `custom_components/lipro/__init__.py`、`config_flow.py`、`core/__init__.py` 与 `core/mqtt/__init__.py` 的 compat exports 已关闭；`core.api.LiproClient` 是唯一仍登记的显式 compat shell。
- `Coordinator.devices` 已收口为 read-only mapping；`LiproDevice.outlet_power_info` 已成为正式 primitive，`extra_data["power_info"]` 退出正式写路径。
- 最新 targeted Phase 9 regression 已通过：`uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/integration/test_mqtt_coordinator_integration.py tests/meta/test_public_surface_guards.py tests/core/test_outlet_power.py tests/test_coordinator_public.py tests/platforms/test_sensor.py tests/core/test_diagnostics.py` → `295 passed`。
- 本报告第 5.1 / 5.3 / 5.4 与 5.5 中关于 implicit protocol delegation、live mutable runtime map、outlet power side-write、root/config-flow/core/mqtt compat export 扩散的发现，已由 Phase 9 修复并回写治理真源；剩余 residual 以 `09-VERIFICATION.md`、`RESIDUAL_LEDGER.md` 与 `KILL_LIST.md` 为准。

## 2. 方法与证据

### 2.1 范围锁定

- 以 `git ls-files '*.py'` 统计，当前仓库共有 `443` 个 tracked Python 文件。
- 生产代码主要分布：
  - `custom_components/lipro/core/**`
  - `custom_components/lipro/control/**`
  - `custom_components/lipro/services/**`
  - `custom_components/lipro/entities/**`
  - `custom_components/lipro/flow/**`
  - 仓库根平台入口与 helpers
- 测试/治理代码主要分布：
  - `tests/**`
  - `scripts/**`

### 2.2 证据链

- 全量回归：`uv run pytest -q` → `2133 passed`
- 架构守卫：
  - `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py` → `23 passed`
  - `uv run pytest -q tests/meta/test_external_boundary_authority.py tests/meta/test_external_boundary_fixtures.py tests/meta/test_firmware_support_manifest_repo_asset.py` → `7 passed`
- 审查中修复后的定向回归：
  - `uv run pytest -q tests/core/mqtt/test_connection_manager.py tests/core/mqtt/test_mqtt.py tests/core/test_coordinator.py` → `113 passed`
  - `uv run pytest -q tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py` → `7 passed`
- Repo 级 lint：`uv run ruff check .` 仍报 `145` 项，主要为 docstring/import-order/脚本输出与个别测试清洁度问题；本轮未把它们当作运行时 blocker。
- 二次模式扫描：针对 compat surface、状态旁写、catch-all 异常与危险关键字做了仓库级 `rg` 复查；未发现超出本报告已登记残留范围之外的新 P0/P1。
- 2026-03-14 复跑确认：`uv run pytest -q` 再次通过 `2133` 项；Phase 9 policy/governance hardening 回归 `150 passed`，`scripts/export_ai_debug_evidence_pack.py` 烟测临时产物未留在当前工作树。

### 2.3 子代理与主代理复核

- MQTT 分区：子代理完整核读并给出明确结论（100% 覆盖该分区）。
- Protocol 分区：子代理完整核读并给出明确结论（100% 覆盖该分区）。
- Coordinator / 平台入口分区：子代理给出部分覆盖结论，主代理结合模式扫描与重点手审复核。
- 其余区域：主代理通过仓库级守卫、全量测试、依赖扫描、异常/状态旁写扫描与关键文件手审补齐。

## 3. 顶层架构审查

### 3.1 通过项

- `LiproProtocolFacade` 仍是生产主链的 protocol-plane root；`config_flow.py` 登录路径也已走 `LiproProtocolFacade`。
- `Coordinator` 仍是唯一 runtime orchestration root；HA 根模块总体保持 thin adapter 形态。
- protocol boundary family 仍实际承接 REST/MQTT canonical decode；未发现新的 raw vendor payload 直接穿透到 runtime/entity。
- `Phase 8` evidence-pack 代码、专项测试与 closeout 工件在当前工作树中已经齐备，并且其定位仍是 assurance/tooling only。

### 3.2 主要残留

- protocol 包级出口仍偏宽，但 child-defined implicit delegation 已在 Phase 9 关闭；当前残留主要是 collaborator/helper type surface 的治理宽度。
- `core.api.LiproClient`、`LiproProtocolFacade.get_device_list` 与 `LiproMqttFacade.raw_client` 已压缩为显式、可计数、可删除的 compat seam。
- 仍开放的后续工作以 low-priority hygiene、模块级缓存/异常可观测性，以及 formal primitive 的进一步不可变性加固为主。

## 4. 本轮已确认并修复的问题

### 4.1 MQTT 重连退避未真正复位

- 根因：`custom_components/lipro/core/mqtt/connection_manager.py:116` 使用局部 `reconnect_delay`，而 `custom_components/lipro/core/mqtt/client_runtime.py:129` 对 `_reconnect_delay` 的复位不会影响真实重连等待。
- 影响：成功连接一段时间后再次断开，等待时间会沿用历史失败放大的退避值。
- 修复：仅在失败后继续指数放大；成功完成一次 `connect_and_listen()` 后，下一轮等待恢复到最小退避。
- 证据：`tests/core/mqtt/test_connection_manager.py:146` 新增回归。

### 4.2 live unsubscribe 失败后缺少同会话重试

- 根因：`custom_components/lipro/core/mqtt/subscription_manager.py:161` 在 connected 分支里先把设备从 `subscribed_devices` 移除，再尝试 unsubscribe；若 broker 调用失败，后续同一会话不会再次计算到 `to_remove`。
- 影响：旧 topic 可在当前连接内持续残留，形成过订阅、额外消息与 broker/client 状态漂移。
- 修复：connected 分支改为**只在 unsubscribe 成功后**移除 `subscribed_devices`；失败时保留在 `pending_unsubscribe`，后续 `sync_subscriptions()` 与重连握手都会继续重试。
- 证据：`tests/core/mqtt/test_mqtt.py:1123` 与 `tests/core/mqtt/test_mqtt.py:1142` 已校正并新增回归。

### 4.3 REST 状态轮询绕过 Coordinator 确认过滤链

- 根因：`custom_components/lipro/core/coordinator/orchestrator.py:145` 原本把 `StatusRuntime` 的 `apply_properties_update` 直接接到 `state_runtime.apply_properties_update()`，绕过 `Coordinator._apply_properties_update()` 中的 pending-state filter 与 confirmation observe。
- 影响：REST status 回写与 MQTT/command 确认链语义不一致，存在覆盖乐观状态/确认学习失真风险。
- 修复：改为通过 `RuntimeContext` 回调统一走 `Coordinator._apply_properties_update()`。
- 证据：`tests/core/test_coordinator.py:352` 新增回归。

## 5. 仍需后续收口的发现

### 5.1 `Medium/Low`：protocol 包出口仍偏宽，但 implicit child-defined contract 已关闭

- `custom_components/lipro/core/protocol/__init__.py:7`
- `custom_components/lipro/core/protocol/facade.py:202`
- `custom_components/lipro/core/protocol/facade.py:206`

问题：`LiproProtocolFacade` 之外，protocol 包仍公开导出 `LiproMqttFacade`、`ProtocolTelemetry`、`ProtocolSessionState`、`CanonicalProtocolContracts` 等 collaborator/type surface。Phase 9 已关闭 `__getattr__` / `__dir__` 隐式扩面，因此这里剩下的是**包级治理宽度**，不是 child surface 重新定义 root contract。  
裁决：属于后续可继续收口的架构 hygiene，不是当前主链 blocker。

### 5.2 `Medium`：`raw_client` concrete transport 暴露仍在

- `custom_components/lipro/core/protocol/facade.py:79`

问题：`raw_client` 继续把 `LiproMqttClient` concrete transport 暴露给外层，放大 compat/export seam。  
裁决：建议未来仅保留显式测试 seam 或删除 gate，不再让其作为稳定公开面长期存在。

### 5.3 `Resolved in Phase 9 / Low`：mutable device map public leak 已收口

- `custom_components/lipro/core/coordinator/coordinator.py:210`
- `custom_components/lipro/core/coordinator/services/state_service.py:20`
- `custom_components/lipro/core/coordinator/services/device_refresh_service.py:23`

历史问题：`Coordinator.devices` 曾直接返回 live dict，外层可获得可变状态引用。  
当前状态：Phase 9 已把 `Coordinator.devices` 收口为 read-only mapping；剩余风险仅是设备对象本身仍为浅可变，这符合当前 contract，但后续可再加固。

### 5.4 `Resolved in Phase 9 / Low`：outlet power side-write 已迁到 formal primitive

- `custom_components/lipro/core/coordinator/outlet_power.py:19`
- `custom_components/lipro/core/coordinator/coordinator.py:485`

历史问题：`power_info` 曾直接写入 `device.extra_data`，未经过统一状态更新 primitive。  
当前状态：Phase 9 已把正式写路径迁到 `LiproDevice.outlet_power_info`；`extra_data["power_info"]` 只剩 legacy read fallback，不再承担正式 truth。

### 5.5 `Resolved in Phase 9 / Medium/Low`：多入口 compat export 扩散已收口为显式 seam

- `custom_components/lipro/__init__.py:49`
- `custom_components/lipro/config_flow.py:52`
- `custom_components/lipro/core/api/__init__.py:10`
- `custom_components/lipro/core/__init__.py:4`
- `custom_components/lipro/core/mqtt/__init__.py:5`

历史问题：`LiproClient` / `LiproMqttClient` 曾被多个 public/export 点重新可见化。  
当前状态：Phase 9 已关闭 root / flow / core / mqtt 包级 compat exports；remaining delete-gated seam 只剩 `core.api.LiproClient`、`LiproProtocolFacade.get_device_list` 与 `LiproMqttFacade.raw_client`。

### 5.6 `Low`：模块级缓存/弱可观测点

- `custom_components/lipro/firmware_manifest.py:48`：远端 firmware advisory 使用模块级缓存与锁，不按 HA 实例隔离。
- `custom_components/lipro/domain_data.py:20`：`ensure_domain_data()` 遇到污染的 `hass.data[DOMAIN]` 只返回 `None`，上游容易静默跳过。
- `custom_components/lipro/runtime_infra.py:26`：device-registry listener 只按 key 存在判断，损坏值时不会自愈重建。
- `custom_components/lipro/entry_auth.py:161`：`clear_entry_runtime_data()` 用 `suppress(Exception)` 吞掉生命周期异常。
- `custom_components/lipro/config_flow.py:139`：广义 `except Exception` 统一折叠成 `unknown`，降低 reauth/login 失败可诊断性。

### 5.7 `Low/Medium`：service plane 仍有少量 protocol helper 直引

- `custom_components/lipro/services/schedule.py:13`

问题：service 层直接引入 `core.api.schedule_codec.coerce_int_list`。  
裁决：这不是当前运行 bug，但从依赖矩阵角度更像历史便利性残留，建议未来迁移到更中立的 domain/service helper。

## 6. 测试与治理面判断

- 当前 meta guards 与 governance truth 在当前工作树里是自洽的；`Phase 9` summary / validation / verification / state / roadmap 已更新到完成态。
- 当前 `Phase 8` / `Phase 9` 相关文件已存在并通过专项测试，说明“代码实现”与“治理登记”在工作树中已形成闭环。
- repo 级 `ruff` 仍有较多遗留，但它们暂未表现为运行时风险；如果后续要追求更高整洁度，可单开 hygiene 清扫轮次。

## 7. 当前建议优先级

1. **已完成**：MQTT 退避复位、unsubscribe 重试、status 回写统一主链。
2. **下一优先级**：继续收窄 `core.api.LiproClient`、`LiproProtocolFacade.get_device_list` 与 `LiproMqttFacade.raw_client` 这些 delete-gated compat seam。
3. **其后**：若继续加固，可评估 `outlet_power_info` 的深层只读语义与 protocol package collaborator export 的进一步收口。
4. **治理型低优先级**：清理 broad exception / 全局缓存 / schedule codec 依赖残留 / repo-wide lint 噪音。

## 8. 审查边界声明

本轮已经做到：

- 用仓库级守卫与全量测试确认当前工作树主链稳定；
- 用分区子代理、重点手审与模式扫描尽可能逼近“逐文件全覆盖”；
- 对确认存在的高风险真实缺陷做根因修复并补回归。

但**不能诚实地宣称“数学意义上的完美无瑕”**：任何静态/半静态审查都只能显著降低风险，不能证明仓库绝对不存在未来场景缺陷。当前结论应理解为：**主链稳定、关键高危点已修、剩余问题以架构收口与治理整洁为主**。
