# Lipro-HASS 全量审查报告（2026-03-13）

> 审查对象：`git ls-files '*.py'` 锁定的 `443` 个 Python 文件  
> 审查基线：`docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`docs/developer_architecture.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md`  
> 审查方式：仓库级守卫与全量测试 + 分区子代理复核 + 主代理重点手审 + 架构/依赖模式扫描  
> 注意：本报告基于**当前工作树**，其中已包含未提交的 `Phase 8` 相关工件与规划文档变更。

## 1. 结论先行

- 北极星单一主链**总体保持成立**：正式 protocol root 仍是 `LiproProtocolFacade`，正式 runtime root 仍是 `Coordinator`，`Phase 8` evidence-pack 代码与治理工件在当前工作树中已具备完成态。
- 本轮未发现新的“立即导致主线不可运行”的开放性 P0；但在审查过程中确认并修复了 **3 处高风险真实缺陷**：
  1. MQTT 重连退避在成功连接后未真正复位；
  2. live unsubscribe 失败后不会在同一会话内重试，可能遗留过订阅；
  3. REST 状态轮询绕过 `Coordinator._apply_properties_update()`，跳过命令确认过滤链。
- 自动化证据强：`uv run pytest -q` 当前通过 `2128` 项；架构/治理守卫与 `Phase 8` 专项测试均通过。
- 仍有若干**中低优先级架构残留**需要后续收口，主要集中在：protocol 包出口面过宽、compat 名称暴露仍多、少量状态旁写与异常吞噬。

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

- 全量回归：`uv run pytest -q` → `2128 passed`
- 架构守卫：
  - `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py` → `18 passed`
  - `uv run pytest -q tests/meta/test_external_boundary_authority.py tests/meta/test_external_boundary_fixtures.py tests/meta/test_firmware_support_manifest_repo_asset.py` → `7 passed`
- 审查中修复后的定向回归：
  - `uv run pytest -q tests/core/mqtt/test_connection_manager.py tests/core/mqtt/test_mqtt.py tests/core/test_coordinator.py` → `113 passed`
  - `uv run pytest -q tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py` → `7 passed`
- Repo 级 lint：`uv run ruff check .` 仍报 `145` 项，主要为 docstring/import-order/脚本输出与个别测试清洁度问题；本轮未把它们当作运行时 blocker。
- 二次模式扫描：针对 compat surface、状态旁写、catch-all 异常与危险关键字做了仓库级 `rg` 复查；未发现超出本报告已登记残留范围之外的新 P0/P1。
- 2026-03-14 复跑确认：`uv run pytest -q` 再次通过 `2128` 项；`scripts/export_ai_debug_evidence_pack.py` 的双目录烟测已生成并核验 JSON/index 产物，随后临时文件已删除。

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

- protocol 包级出口面仍偏宽，削弱“唯一正式 root”的可仲裁性。
- compat 名称 `LiproClient` / `LiproMqttClient` 仍在多个公开入口继续可见，虽已不再是正式主链，但仍放大历史语义。
- 少量 runtime 状态更新与 `extra_data` 写入仍未完全收口到统一 public primitive。

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

### 5.1 `Medium`：protocol 包出口面过宽

- `custom_components/lipro/core/protocol/__init__.py:7`
- `custom_components/lipro/core/protocol/facade.py:202`
- `custom_components/lipro/core/protocol/facade.py:206`

问题：`LiproProtocolFacade` 之外，还公开导出/透传了 `LiproMqttFacade`、`ProtocolTelemetry`、`ProtocolSessionState`、`CanonicalProtocolContracts` 等对象；同时 `__getattr__` / `__dir__` 让 root 的外部 contract 实际继续由 REST child 隐式定义。  
裁决：这更像**架构残留**而非立刻崩溃缺陷，但确实削弱“单一 protocol root”的正式性。

### 5.2 `Medium`：`raw_client` concrete transport 暴露仍在

- `custom_components/lipro/core/protocol/facade.py:79`

问题：`raw_client` 继续把 `LiproMqttClient` concrete transport 暴露给外层，放大 compat/export seam。  
裁决：建议未来仅保留显式测试 seam 或删除 gate，不再让其作为稳定公开面长期存在。

### 5.3 `Medium`：mutable device map 仍可外泄

- `custom_components/lipro/core/coordinator/coordinator.py:210`
- `custom_components/lipro/core/coordinator/services/state_service.py:20`
- `custom_components/lipro/core/coordinator/services/device_refresh_service.py:23`

问题：`Coordinator.devices` 直接返回 live dict，外层可获得可变状态引用。  
裁决：当前未见真实误用，但这与 runtime public surface “显式、可仲裁、避免内部可变结构泄漏”的方向不完全一致。

### 5.4 `Medium`：outlet power 仍是额外状态旁写

- `custom_components/lipro/core/coordinator/outlet_power.py:19`
- `custom_components/lipro/core/coordinator/coordinator.py:485`

问题：`power_info` 直接写入 `device.extra_data`，未经过统一状态更新 primitive。  
裁决：功能上目前可用，但从北极星角度看仍属于“旁路扩展状态”。

### 5.5 `Medium/Low`：compat 名称继续在多个公开入口放大

- `custom_components/lipro/__init__.py:49`
- `custom_components/lipro/config_flow.py:52`
- `custom_components/lipro/core/api/__init__.py:10`
- `custom_components/lipro/core/__init__.py:4`
- `custom_components/lipro/core/mqtt/__init__.py:5`

问题：`LiproClient` / `LiproMqttClient` 虽然已不再承载正式 root 语义，但仍被多个 public/export 点重新可见化。  
裁决：属于 residual cleanup，需结合 delete gate 与外部兼容面谨慎收口。

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

- 当前 meta guards 与 governance truth 在当前工作树里是自洽的；`Phase 8` summary / verification / state / roadmap 已更新到完成态。
- 当前 `Phase 8` 相关文件已存在并通过专项测试，说明“代码实现”与“治理登记”在工作树中已基本闭环。
- repo 级 `ruff` 仍有较多遗留，但它们暂未表现为运行时风险；如果后续要追求更高整洁度，可单开 hygiene 清扫轮次。

## 7. 当前建议优先级

1. **已完成**：MQTT 退避复位、unsubscribe 重试、status 回写统一主链。
2. **下一优先级**：收口 protocol 出口面与 compat export seam。
3. **其后**：把 `outlet_power` / mutable `devices` surface 收回更正式的 runtime public primitive。
4. **治理型低优先级**：清理 broad exception / 全局缓存 / schedule codec 依赖残留 / repo-wide lint 噪音。

## 8. 审查边界声明

本轮已经做到：

- 用仓库级守卫与全量测试确认当前工作树主链稳定；
- 用分区子代理、重点手审与模式扫描尽可能逼近“逐文件全覆盖”；
- 对确认存在的高风险真实缺陷做根因修复并补回归。

但**不能诚实地宣称“数学意义上的完美无瑕”**：任何静态/半静态审查都只能显著降低风险，不能证明仓库绝对不存在未来场景缺陷。当前结论应理解为：**主链稳定、关键高危点已修、剩余问题以架构收口与治理整洁为主**。
