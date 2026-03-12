# Lipro 重构收口残留审查报告（Legacy / Compat Residual Audit）

> **生成日期**：2026-03-11
> **最后更新**：2026-03-12
> **审查范围**：`lipro-hass/custom_components/lipro/` + `lipro-hass/tests/`（仅静态审阅，不做代码修改）
> **目标**：识别”新架构（RuntimeContext + Orchestrator + Runtime 组件 + Service 层）”落地后，仍残留的旧接口、兼容层、影子模块（tests-only / 无生产路径引用 / 生产路径未接回）。
> **完成状态**：✅ P0 全部修复，✅ P2 影子模块清理完成，⚠️ P1 部分修复（详见更新说明）

---

## 0. TL;DR（最关键结论）

### ✅ P0（高风险：真实运行可能直接报错 / 核心链路断裂）— 已全部修复

**修复日期**: 2026-03-12
**Commit**: `8d846bc` - fix(services): resolve P0 interface mismatches from refactor residual audit

- ✅ `send_command` service → 改用 `coordinator.command_service`
- ✅ `refresh_devices` service → 改用 `coordinator.device_refresh_service`
- ✅ `_trigger_reauth` 签名 → 移除 `**placeholders`，只接受 `reason: str`
- ✅ diagnostics → 改用 `coordinator.mqtt_service.connected`
- ✅ MQTT on_message 回调 → 通过 async bridge 绑定到 `mqtt_runtime.handle_message()`
- ✅ MQTT 订阅 fallback → 使用 `build_mqtt_subscription_device_ids()`

### ✅ P2（低风险但噪音大：影子模块 / tests-only surface）— 已清理完成

**修复日期**: 2026-03-12
**Commit**: `49ead4f` - refactor: clean up shadow modules and unused methods per residual audit

- ✅ 删除影子模块：mqtt/policy.py, mqtt/polling.py, coordinator_runtime.py（123 行）
- ✅ 删除 Coordinator 重复方法：_query_device_status_batch(), _async_trigger_reauth()（53 行）
- ✅ 更新 system_health.py → 使用 `mqtt_service.connected`
- ✅ 删除相关测试文件（3 个文件，335 行）

### ⚠️ P1（中风险：架构漂移/链路未接回）— 部分修复，部分标记为设计意图

**修复日期**: 2026-03-12
**Commit**: `61822bf` - docs: clarify StatusRuntime/TuningRuntime as Phase H4 incomplete features

- ✅ **StatusRuntime/TuningRuntime 未消费** → 已确认为 **Phase H4 未完成功能**（非过度设计）
  - 添加文档注释说明这是新架构的设计意图
  - 等待 Phase H4（Service 层升级为 Saga-lite 编排器）实现
  - 参考：docs/refactor_completion_plan.md Section 8 Phase H4

- ✅ **device_refresh_service 回写逻辑** → 已修复
  - 改用 `coordinator.async_request_refresh()` 触发完整更新循环
  - 保持 Service 层薄代理设计（正确的职责分离）

- ⚠️ **其他 P1 问题** → 保留现状（需要真实用户需求驱动）
  - MQTT 轮询放宽链路：等待 Phase H4 实现
  - developer_report 服务：标记为 experimental，等待需求验证
  - 平台层绕过统一写路径：需要逐个评估，非紧急

---

## 1. P0 残留明细（接口不一致 / 真实运行风险）— ✅ 已全部修复

### 1.1 `send_command` 服务：旧签名/旧字段残留 — ✅ 已修复

**修复方案**：
- ✅ 更新 Protocol 定义：`CommandCoordinator` → `command_service: CommandService`
- ✅ 更新调用方式：`coordinator.command_service.async_send_command()`
- ✅ 更新失败读取：`coordinator.command_service.last_failure`

**原问题描述**：

- 旧调用点：`custom_components/lipro/services/command.py:65` 调用 `coordinator.async_send_command(..., fallback_device_id=...)`。
- 旧字段：失败时读取 `coordinator.last_command_failure`（`custom_components/lipro/services/command.py:74`）。
- 当前新 Coordinator：`custom_components/lipro/core/coordinator/coordinator.py:281` 的 `async_send_command(self, device, command, properties)` 不支持 `fallback_device_id`。

**新架构替代**

- 支持 `fallback_device_id` 的稳定边界：`custom_components/lipro/core/coordinator/services/command_service.py:43`（`CoordinatorCommandService.async_send_command(..., fallback_device_id=...)`）。
- 失败上下文对应概念：`custom_components/lipro/core/coordinator/services/command_service.py:39`（`command_service.last_failure`）。

**风险形态（真实运行）**

- 传 `fallback_device_id=` 将在 `Coordinator.async_send_command()` 处触发 `TypeError`（unexpected keyword argument）。
- 即便绕过签名问题，读取 `coordinator.last_command_failure` 也会触发 `AttributeError`（Coordinator 未暴露该字段）。

**测试掩盖点**

- 旧签名断言：`tests/core/test_init.py:2108`（`fallback_device_id=device.serial`）。
- 旧字段注入：`tests/core/test_init.py:2162`（`coordinator.last_command_failure = ...`）。

### 1.2 `refresh_devices` 服务：调用不存在的 `coordinator.async_refresh_devices()` — ✅ 已修复

**修复方案**：
- ✅ 更新调用方式：`coordinator.device_refresh_service.async_refresh_devices()`

**原问题描述**：

- 调用点：`custom_components/lipro/services/maintenance.py:65`。
- 当前 Coordinator 未实现 `async_refresh_devices()`（生产代码仅命中 services/tests）。

**新架构替代**

- `custom_components/lipro/core/coordinator/services/device_refresh_service.py:45`（`CoordinatorDeviceRefreshService.async_refresh_devices()`）。

**风险形态（真实运行）**

- `refresh_devices` service 在生产将触发 `AttributeError`。

**测试掩盖点**

- `tests/core/test_init.py:1272` 通过 `MagicMock(async_refresh_devices=AsyncMock())` 伪造旧方法。

### 1.3 Service 执行器：`_trigger_reauth` 旧签名残留 — ✅ 已修复

**修复方案**：
- ✅ 更新 Protocol 定义：`_trigger_reauth(self, reason: str)`（移除 `**placeholders`）
- ✅ 更新调用方式：`_trigger_reauth(coordinator, f"auth_error: {safe_error}")`

**原问题描述**：

- 旧契约声明：`custom_components/lipro/services/execution.py:21`（`_trigger_reauth(self, key: str, **placeholders)`）。
- 实际调用点：`custom_components/lipro/services/execution.py:70`（`trigger_reauth(key, **placeholders)`），并在 `LiproAuthError` 分支传入 `error=...`（`custom_components/lipro/services/execution.py:89`）。
- 新 Coordinator 回调：`custom_components/lipro/core/coordinator/coordinator.py:135`（`_trigger_reauth(self, reason: str)`）。

**风险形态（真实运行）**

- 当云端鉴权异常需要 reauth 时，将在 `_trigger_reauth(..., error=...)` 处触发 `TypeError`。

**测试掩盖点**

- `tests/services/test_execution.py:75` 使用 `AsyncMock()` 接管 `_trigger_reauth`，不会对签名差异报警。

### 1.4 diagnostics：直接读取 `coordinator.mqtt_connected` — ✅ 已修复

**修复方案**：
- ✅ 更新 diagnostics.py：使用 `coordinator.mqtt_service.connected`（2 处）
- ✅ 更新 system_health.py：使用 `mqtt_service.connected`
- ✅ 更新 test_diagnostics.py：修复所有 mock 结构（5 处）

**原问题描述**：

- 调用点：`custom_components/lipro/diagnostics.py:252`、`custom_components/lipro/diagnostics.py:286`。
- 新架构可用信息源：
  - `custom_components/lipro/core/coordinator/services/mqtt_service.py:36`（`mqtt_service.connected`）
  - `custom_components/lipro/core/coordinator/coordinator.py:142`（`_is_mqtt_connected()` 回调）

**风险形态（真实运行）**

- 调用 diagnostics 时触发 `AttributeError`。

**测试掩盖点**

- `tests/core/test_diagnostics.py:231`（以及同文件多处）直接注入 `coordinator.mqtt_connected = True/False`。

**对比**

- `custom_components/lipro/system_health.py:64` 使用 `getattr(coordinator, "mqtt_connected", None)`，因此不会崩溃，但也会长期拿不到该字段。


### 1.5 MQTT 生命周期：未绑定 `on_message` 回调 — ✅ 已修复

**修复方案**：
- ✅ 创建 async bridge 函数：`_on_message_bridge(topic, payload)`
- ✅ 使用 `asyncio.create_task()` 桥接同步回调到异步 handler
- ✅ 绑定到 `LiproMqttClient(on_message=_on_message_bridge)`

**原问题描述**：

- 现状：`mqtt_lifecycle` 创建 `LiproMqttClient` 时未传 `on_message`（`custom_components/lipro/core/coordinator/mqtt_lifecycle.py:159`）。
- `core/mqtt` 的消息处理链路只会把解析后的消息转发给 `self._on_message`（`custom_components/lipro/core/mqtt/client_runtime.py:94`）。
- 但新架构实际的“消息入口”是 `MqttRuntime.handle_message()`（`custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py:249`），目前没有任何生产代码把两者接起来。

**新架构替代/对应位置**

- `MqttRuntime.handle_message()`：`custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py:249`。
- `LiproMqttClient` 回调参数：`custom_components/lipro/core/mqtt/mqtt_client.py:32`（`on_message/on_connect/on_disconnect`）。

**风险形态（真实运行）**

- MQTT 即便连接成功，实时 push 也不会驱动设备属性更新，状态可能长期停留在“上次设备列表刷新/命令乐观更新”的快照上。
- 即便未来补上 wiring，也需要“同步回调 → 协程”的桥接：`LiproMqttClient` 的 `on_message` 类型是同步回调（`custom_components/lipro/core/mqtt/mqtt_client.py:32`），而 `MqttRuntime.handle_message()` 是 `async def`（`custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py:249`）。

**测试掩盖点**

- `tests/core/coordinator/runtime/test_mqtt_runtime.py:226` 直接调用 `mqtt_runtime.handle_message(...)` 测逻辑，但未覆盖“MQTT 客户端 → runtime”的 wiring。

### 1.6 MQTT 生命周期：订阅 targets 仅 mesh group — ✅ 已修复

**修复方案**：
- ✅ 使用 `build_mqtt_subscription_device_ids()` helper 函数
- ✅ 自动 fallback 到所有设备（当无 mesh group 时）

**原问题描述**：

- 现状：`mqtt_lifecycle` 只对 `device.is_group` 构造订阅列表（`custom_components/lipro/core/coordinator/mqtt_lifecycle.py:184`）。
- 若账号下没有 mesh group，则不会调用 `mqtt_runtime.connect()`，但随后仍会检查 `mqtt_runtime.is_connected` 并直接返回失败（`custom_components/lipro/core/coordinator/mqtt_lifecycle.py:198`）。
- 同类逻辑也出现在 `CoordinatorMqttService.async_sync_subscriptions()`（仅同步 group：`custom_components/lipro/core/coordinator/services/mqtt_service.py:54`）。

**新架构替代/对应位置**

- 订阅 target fallback：`custom_components/lipro/core/coordinator/mqtt/setup.py:51`（`build_mqtt_subscription_device_ids()`）。

**风险形态（真实运行）**

- 在“没有 mesh group 设备”的家庭环境下，MQTT 可能永远无法启用，导致实时状态与部分命令确认链路退化。

**测试掩盖点**

- `tests/core/mqtt/test_mqtt_setup.py:62` 覆盖了 `build_mqtt_subscription_device_ids()` 的 fallback 行为，但生产路径目前未复用该函数。

---

## 2. P2 影子模块对照表 — ✅ 已清理完成

**修复日期**: 2026-03-12
**Commit**: `49ead4f` - refactor: clean up shadow modules and unused methods per residual audit

说明：此处”影子模块”指 **仅 tests 引用 / 或生产路径完全未引用 / 生产链路未接回** 的模块（含旧实现保留的纯策略函数）。

### 2.1 功能影子模块（tests-only 或生产未接回）— ✅ 已清理

| 影子模块 | 主要职责 | 清理状态 |
|---|---|---|
| `mqtt/policy.py` | MQTT 断连时间/通知/放宽轮询策略 | ✅ 已删除（43 行） |
| `mqtt/polling.py` | MQTT connect/disconnect 时轮询策略 | ✅ 已删除（47 行） |
| `coordinator_runtime.py` | 设备刷新/MQTT setup 决策函数 | ✅ 已删除（33 行） |
| `test_mqtt_lifecycle.py` | 测试已删除的 policy.py | ✅ 已删除（96 行） |
| `test_mqtt_polling.py` | 测试已删除的 polling.py | ✅ 已删除（101 行） |
| `test_coordinator_runtime.py` | 测试已删除的 coordinator_runtime.py | ✅ 已删除（138 行） |

**Coordinator 重复方法清理**：
- ✅ `_query_device_status_batch()` - 与 orchestrator 闭包重复（42 行）
- ✅ `_async_trigger_reauth()` - 与 `_trigger_reauth()` 回调重复（11 行）

**总计清理**：516 行代码

### 2.1 功能影子模块（tests-only 或生产未接回）— ⚠️ 保留待评估

以下模块保留现状，等待真实用户需求驱动：

| 影子模块 | 主要职责 | 当前引用情况 | 新架构替代/对应位置 | 建议（删/并/接回） |
|---|---|---|---|---|
| `custom_components/lipro/core/coordinator/mqtt/policy.py` | MQTT 断连时间/通知/放宽轮询策略（纯函数） | 仅 tests 引用（`tests/core/mqtt/test_mqtt_lifecycle.py:5`） | 轮询放宽：`custom_components/lipro/core/coordinator/runtime/mqtt/connection.py:72`；断连通知入口：`custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py:282` | **删**（已被 runtime 覆盖；但注意 runtime 的 updater 注入仍未接回，见 3.4） |
| `custom_components/lipro/core/coordinator/mqtt/polling.py` | 从 options 解析 scan interval；MQTT connect/disconnect 时轮询策略（纯函数） | 仅 tests 引用（`tests/core/coordinator/mqtt/test_polling.py:7`） | scan interval 读取：`custom_components/lipro/__init__.py:110`；放宽轮询实现：`custom_components/lipro/core/coordinator/runtime/mqtt/connection.py:79` | **删/并**（如仍需纯函数测试，可并入 `connection.py`） |
| `custom_components/lipro/core/coordinator/mqtt/setup.py`（部分 helper：`extract_mqtt_encrypted_credentials/build_mqtt_subscription_device_ids/iter_mesh_group_serials`） | MQTT credential 提取 + 订阅目标选择（纯函数） | 生产引用 `resolve_mqtt_biz_id`（`custom_components/lipro/core/coordinator/mqtt_lifecycle.py:151`）；其余 helper 仅 tests 引用（`tests/core/mqtt/test_mqtt_setup.py:6`） | 生产逻辑目前内联在 `custom_components/lipro/core/coordinator/mqtt_lifecycle.py:142`（解密） + `custom_components/lipro/core/coordinator/mqtt_lifecycle.py:184`（订阅列表），未复用这些 helper | **并/接回**（让生产复用 helper 或把 tests 迁移到实际实现后删除 helper） |
| `custom_components/lipro/core/coordinator/runtime/coordinator_runtime.py` | 是否刷新设备列表、是否应调度 MQTT setup 的纯决策函数 | 仅 tests 引用（`tests/core/test_coordinator_runtime.py:8`） | 设备刷新判定：`custom_components/lipro/core/coordinator/runtime/device_runtime.py:150`；MQTT setup：`custom_components/lipro/core/coordinator/coordinator.py:419` / `custom_components/lipro/core/coordinator/coordinator.py:421` | **删**（逻辑已迁移且重复） |
| `custom_components/lipro/core/coordinator/runtime/connect_status_runtime.py` | connect-status 查询间隔与 stale window 自适应（旧设计） | 仅 tests 引用（`tests/core/coordinator/runtime/test_connect_status_runtime.py:8`） | **无完整替代**；仅存在简化版 interval：`custom_components/lipro/core/coordinator/runtime/tuning/algorithm.py:92` + “近似 stale”判断：`custom_components/lipro/core/device/device.py:86`（被 `custom_components/lipro/core/coordinator/runtime/status/strategy.py:79` 使用） | **接回或删**（若需要 connect-status 轮询，需补齐消费链路；否则删） |
| `custom_components/lipro/core/coordinator/runtime/status_strategy.py` | connect-status candidates + 自适应 batch size（旧设计） | tests 引用（`tests/core/test_status_strategy.py:8`）；另被 `state_batch_runtime` 引用（`custom_components/lipro/core/coordinator/runtime/state_batch_runtime.py:5`，该模块本身也仅 tests 引用） | 状态查询策略（更简化）：`custom_components/lipro/core/coordinator/runtime/status/strategy.py:14`；自适应 batch size（仅 latency 维度）：`custom_components/lipro/core/coordinator/runtime/tuning_runtime.py:93` | **删/并**（若继续要该自适应策略，建议并入 tuning/status 现实现，并接回生产） |
| `custom_components/lipro/core/coordinator/runtime/state_batch_runtime.py` | state batch metric 归一化与统计 | 仅 tests 引用（`tests/core/test_state_batch_runtime.py:5`） | 近似替代：`custom_components/lipro/core/coordinator/runtime/tuning/metrics.py:41` + `custom_components/lipro/core/coordinator/runtime/tuning_runtime.py:60` | **删/并**（若 tuning 真要用，建议合并并接回生产链路） |
| `custom_components/lipro/core/coordinator/outlet_power.py` | outlet power 写入 `device.extra_data["power_info"]` + 错误升级策略 | 仅 tests 引用（`tests/core/test_outlet_power.py:8`） | **无生产替代**；仅有 API endpoint：`custom_components/lipro/core/api/endpoints/misc.py:45`（`fetch_outlet_power_info`） | **接回或删**（不接回则功耗相关实体/选项长期无效，见下方“生产消费者”） |
| `custom_components/lipro/core/coordinator/runtime/outlet_power_runtime.py` | 并发查询 outlet 功耗并回写 | 仅 tests 引用（`tests/core/test_outlet_power_runtime.py:16`） | **无生产替代**；`StatusRuntime` 仅保留 scheduler 切片能力：`custom_components/lipro/core/coordinator/runtime/status_runtime.py:71`（但生产未调用） | **接回或删** |
| `custom_components/lipro/core/coordinator/runtime/product_config_runtime.py` | 匹配 `get_product_configs()` 并覆盖设备模型（色温/风档） | 仅 tests 引用（`tests/core/coordinator/runtime/test_product_config_runtime.py:8`） | **无生产替代**；仅有 endpoint：`custom_components/lipro/core/api/endpoints/devices.py:32`；静态默认：`custom_components/lipro/core/device/profile.py:15` | **接回或删**（不接回则实体能力/匿名上报长期退化，见下方“生产消费者”） |
| `custom_components/lipro/core/coordinator/device_registry_sync.py` + `custom_components/lipro/core/coordinator/runtime/room_sync_runtime.py` | 云端 room → HA area 同步、清理 stale registry device | 仅 tests 引用（`tests/core/test_device_registry_sync.py:8`） | **无生产替代**；当前只有“device registry disable/enable reload”监听：`custom_components/lipro/services/maintenance.py:106` | **接回或删**（options 已暴露 `room_area_sync_force`，但生产无执行点） |
| `custom_components/lipro/core/coordinator/runtime/group_lookup_runtime.py` | mesh group gateway/member lookup-id 映射决策 | 仅 tests 引用（`tests/core/test_group_lookup_runtime.py:8`） | 仅有解析 helper：`custom_components/lipro/core/device/group_status.py:18`（只解析不落盘） | **接回或删**（不接回则 schedule/dispatch/developer_report 的 mesh 语义缺失，见下方“生产消费者”） |
| `custom_components/lipro/core/utils/developer_report.py` | 构建“运行态开发者报告”（脱敏、摘要、命令轨迹等） | 仅 tests 引用（`tests/core/test_developer_report.py:25`） | **无生产替代**；理想形态：由 `Coordinator.build_developer_report()` 调用此模块，并注入 runtimes 状态（但当前 Coordinator 未实现） | **接回或删** |
| `custom_components/lipro/core/device/group_status.py` | mesh group status payload 解析为 gateway/member IDs | 无生产引用（仅自身） | 无 | **并/接回或删**（建议与 group lookup 逻辑合并后接回生产，或整体删除） |

### 2.2 tests/类型影子模块（更偏“工程噪音”，但会误导维护者）

| 影子模块 | 主要职责 | 当前引用情况 | 新架构替代/对应位置 | 建议 |
|---|---|---|---|---|
| `custom_components/lipro/core/coordinator/protocols.py` | service 层 Protocol（类型约束） | 仅 tests 引用（`tests/type_checking/test_protocols.py:10`） | 真实实现：`custom_components/lipro/core/coordinator/services/command_service.py:33` 等 | **删/保留二选一**：要继续 type-checking 就保留；否则删以降噪 |
| `custom_components/lipro/const/__init__.py` | 常量 re-export 聚合（文件自述“test convenience only”） | `rg` 未见引用（生产/测试均未导入该聚合模块） | 直接导入子模块：`custom_components/lipro/const/base.py` 等 | **删**（若确实无外部引用） |

### 2.3 关键影子模块的“生产消费者”证据（帮助决策删/并/接回）

这些模块本身 tests-only，但其“预期产物/字段”已经在生产代码被依赖：

- **Mesh group 元数据缺口**（`gateway_device_id` / `group_member_ids`）
  - 消费点：
    - schedule service 组网参数：`custom_components/lipro/services/schedule.py:97`（读 `gateway_device_id` / `group_member_ids`）
    - 命令 fallback 决策：`custom_components/lipro/core/command/dispatch.py:98`（读 `group_member_ids`）
    - developer report mesh 片段：`custom_components/lipro/core/utils/developer_report.py:47`（读 `group_member_ids`）
  - 但设备构造层当前不会填充这些字段：`custom_components/lipro/core/device/device_factory.py:41`（`extra_data` 仅写入 `is_ir_remote`）

- **功耗能力缺口**（`extra_data["power_info"]`）
  - 消费点：
    - outlet power/energy 传感器：`custom_components/lipro/sensor.py:79`（读取 `power_info`）
    - diagnostics 输出 power_info：`custom_components/lipro/diagnostics.py:201`（保留 power_info 不脱敏）
    - options 已暴露开关：`custom_components/lipro/flow/options_flow.py:248`（`CONF_ENABLE_POWER_MONITORING`）

- **product config 动态能力缺口**（色温范围、风档上限等）
  - 消费点：
    - Light 色温范围：`custom_components/lipro/light.py:111` / `custom_components/lipro/light.py:119`
    - Fan 档位上限：`custom_components/lipro/fan.py:168`
    - Gear Select 显示范围：`custom_components/lipro/select.py:245`
    - anonymous share 上报：`custom_components/lipro/core/anonymous_share/collector.py:98`

---

## 3. “已装配但未接回”的链路（不属于单个影子模块，但体现迁移未收口）

### 3.1 `StatusRuntime` / `TuningRuntime` 已装配但未进入 `Coordinator._async_update_data()`

- 装配：`custom_components/lipro/core/coordinator/orchestrator.py:134`（tuning）、`custom_components/lipro/core/coordinator/orchestrator.py:197`（status）。
- 但 `Coordinator._async_update_data()`（`custom_components/lipro/core/coordinator/coordinator.py:392` 起）目前只做：
  - 鉴权：`custom_components/lipro/core/coordinator/coordinator.py:408`
  - 设备刷新：`custom_components/lipro/core/coordinator/coordinator.py:411`
  - MQTT setup：`custom_components/lipro/core/coordinator/coordinator.py:419`

### 3.2 connect-status refresh 标志位被写入但无人消费

- 写入：`custom_components/lipro/core/coordinator/runtime/command_runtime.py:195`（priority ids）+ `custom_components/lipro/core/coordinator/runtime/command_runtime.py:198`（`force_connect_status_refresh_setter(True)`）。
- 状态位仅被设置未被读取：`custom_components/lipro/core/coordinator/coordinator.py:148`。

### 3.3 `Coordinator` 内部存在未使用的“旧实现残片”方法

- `custom_components/lipro/core/coordinator/coordinator.py:302` `_query_device_status_batch()` 与 orchestrator closure（`custom_components/lipro/core/coordinator/orchestrator.py:157`）职责重复，且无调用点。
- `custom_components/lipro/core/coordinator/coordinator.py:348` `_async_trigger_reauth()` 无调用点，且与 `RuntimeContext` 回调 `_trigger_reauth()`（`custom_components/lipro/core/coordinator/coordinator.py:135`）职责重叠。

### 3.4 MQTT runtime 的“有实现但未接回”

- 轮询放宽依赖 `MqttRuntime.set_polling_updater()`：`custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py:156`，但生产代码没有注入 updater（`rg` 仅命中 tests：`tests/core/coordinator/runtime/test_mqtt_runtime.py:441`）。
- 断连通知触发入口 `check_disconnect_notification()`：`custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py:282`，同样仅 tests 调用（`tests/core/coordinator/runtime/test_mqtt_runtime.py:329`）。
- `MqttRuntime.connect()` 在 `mqtt_client.start()` 后立即调用 `_connection_manager.on_connect()`（`custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py:223` / `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py:225`），但 `core/mqtt` 真正握手完成才会置 `LiproMqttClient._connected = True`（`custom_components/lipro/core/mqtt/client_runtime.py:139`）；`mqtt_service.connected` 的语义可能与真实 broker 连接状态漂移。
- unload/shutdown 仅调用 `DataUpdateCoordinator.async_shutdown()`（`custom_components/lipro/__init__.py:157`），未见调用 `coordinator.mqtt_service.async_stop()`（`custom_components/lipro/core/coordinator/services/mqtt_service.py:46`；tests 覆盖：`tests/integration/test_mqtt_coordinator_integration.py:277`）。


### 3.5 `device_refresh_service` 刷新语义未接回（service facade 与 coordinator 主循环不一致）

- service facade：`CoordinatorDeviceRefreshService.async_refresh_devices()` 只调用 `device_runtime.refresh_devices(force=True)`（`custom_components/lipro/core/coordinator/services/device_refresh_service.py:45`），不负责把 snapshot 同步回 `coordinator._state.devices`。
- coordinator 主循环：`Coordinator._async_update_data()` 会把 snapshot 写回 `coordinator._state.devices`（`custom_components/lipro/core/coordinator/coordinator.py:415`）。
- tests 侧通过 helper 强行同步：`tests/conftest_shared.py:71`（`refresh_and_sync_devices()` 直接写 `coordinator._state.devices`）。

**风险形态（真实运行）**

- 后续若将 `refresh_devices` 服务简单改为调用 `device_refresh_service.async_refresh_devices()`，可能出现“调用成功但平台实体未看到 devices 更新”的假刷新。

### 3.6 Device 增量刷新：snapshot key 与增量回写 key 可能不一致

- snapshot 构建时 `devices` 映射 key 为 `device.serial`：`custom_components/lipro/core/coordinator/runtime/device/snapshot.py:136`。
- 增量刷新从 API 返回 `device_data["id"]`，并以该 id 查 `devices.get(device_id)` 回写 properties：`custom_components/lipro/core/coordinator/runtime/device/incremental.py:56`、`custom_components/lipro/core/coordinator/runtime/device/incremental.py:104`。
- snapshot 同时维护 `device_by_id`（key 为 `iot_device_id`）：`custom_components/lipro/core/coordinator/runtime/device/snapshot.py:107`、`custom_components/lipro/core/coordinator/runtime/device/snapshot.py:138`。

**风险形态（真实运行）**

- 如果 API 的 `id` 字段实际等同 `iot_device_id`（而不是 `serial`），则 `devices.get(device_id)` 将长期 miss，增量刷新会退化为“只请求 API，不更新内存状态”。

**新架构替代/对应位置（仅供决策）**

- 在增量回写阶段应优先使用 `device_by_id` 或 `StateRuntime.get_device_by_id()`（`custom_components/lipro/core/coordinator/runtime/state_runtime.py:59`）定位设备，再执行 `update_properties`。

---

## 4. 其他“兼容层残留”（更偏协议/测试兼容，不一定是重构债）

这类残留多为“对外 API payload / 历史协议 / tests patch surface”兼容：

- API payload 兼容：
  - `custom_components/lipro/core/api/client.py:24` `_build_compat_list_payload()`（`{"data": [...]}` 形态）
  - `custom_components/lipro/core/api/client_auth_recovery.py:214` `_unwrap_iot_success_payload()`（将 `data=None` 兼容为 `{}`）
  - `custom_components/lipro/core/coordinator/runtime/device/snapshot.py:75`（兼容 `{"devices": [...]}` 与 `{"data": [...]}`）
  - `custom_components/lipro/core/api/mqtt_api_service.py:13` `_extract_mqtt_config_payload()`（MQTT config 支持 direct / data-only / success+data 多形态）
  - `custom_components/lipro/core/api/schedule_codec.py:114` `normalize_mesh_timing_rows()`（mesh schedule row 缺 `deviceId` 时注入 `fallback_device_id`）
  - `custom_components/lipro/core/coordinator/mqtt/setup.py:30` `resolve_mqtt_biz_id()`（`CONF_BIZ_ID` 缺失时回退 `CONF_USER_ID`）
- 历史错误码兼容（非“旧架构”，是后端协议兼容）：
  - 定义：`custom_components/lipro/const/api.py:97`（`ERROR_DEVICE_OFFLINE_LEGACY`）
  - 使用：`custom_components/lipro/services/errors.py:18`、`custom_components/lipro/core/api/endpoints/status.py:14`
- tests patch surface 兼容（统一 logger / 暴露字段）：
  - `custom_components/lipro/core/api/client_transport.py:65`（保留 `self._session` 以兼容 tests）
  - `tests/conftest_shared.py:71` `refresh_and_sync_devices()` 直接写 `coordinator._state.devices`（与生产 `_async_update_data()` 语义强耦合，易随实现演进而漂移）
  - endpoints 同名 logger：`custom_components/lipro/core/api/endpoints/misc.py:26`（与 client logger 同名，便于 tests patch）
  - anonymous_share 内部常量导出：`custom_components/lipro/core/anonymous_share/sanitize.py:212`
- Worker API / 外部协议兼容：
  - `custom_components/lipro/core/anonymous_share/models.py:13`（Worker API compatible）
  - `custom_components/lipro/core/api/command_api_service.py:19`（busy-retry-compatible protocol）
- 旧 mocks 容忍（更偏工程健壮性）：
  - `custom_components/lipro/core/coordinator/runtime/state/reader.py:48`（room_id 同时兼容 int 与 str）

### 4.1 平台/实体层残留（未完全按“Service 边界 + 统一写路径”收敛）

这些点不一定是“旧架构”，但它们绕过了本次重构引入的稳定边界（如 `state_service/command_service`）或实体基类的统一写路径，容易导致后续持续漂移。

- **读侧仍倾向直接使用 `coordinator.devices`（而非 `coordinator.state_service.devices`）**
  - 典型：`custom_components/lipro/helpers/platform.py:55`、`custom_components/lipro/helpers/platform.py:71`、`custom_components/lipro/update.py:25`。
  - 稳定边界：`custom_components/lipro/core/coordinator/services/state_service.py:38`（`CoordinatorStateService.devices`）。

- **写侧仍存在绕过“lock + optimistic + debounce protection window”的直接写入**
  - Fan 在“关机时调速”分支直接写 `device.update_properties(...)`：`custom_components/lipro/fan.py:163`。
  - 新架构统一写路径（含 per-device lock）：`custom_components/lipro/entities/base.py:256`（`async_send_command_debounced` 的 optimistic 写入加锁）。

- **直接触发 listener 更新（绕过 coordinator/state runtime 的聚合入口）**
  - Select 在应用 gear preset 后直接 `coordinator.async_update_listeners()`：`custom_components/lipro/select.py:301`。
  - 新架构内置的“统一入口”是 context 回调 `_schedule_listener_update()`：`custom_components/lipro/core/coordinator/coordinator.py:131`。

- **实体直连 API client（穿透 coordinator boundary）**
  - OTA cache key 直接引用 `coordinator.client`：`custom_components/lipro/entities/firmware_update.py:260`。
  - 查询 OTA rows 直接调用 `coordinator.client.query_ota_info(...)`：`custom_components/lipro/entities/firmware_update.py:272`。

- **兼容导出/重导出模块扩大 public surface（对 tests patch surface 友好，但增加收口成本）**
  - Coordinator alias：`custom_components/lipro/coordinator_entry.py:5`、`custom_components/lipro/runtime_types.py:7`。
  - diagnostics re-export：`custom_components/lipro/services/diagnostics/__init__.py:8`（`__all__` 维持对外兼容）。

---

## 5. 建议的下一步收口策略（仅供决策）

1) **先收口 P0：统一“HA service handler → Coordinator”契约**
   - 倾向让 services 改用 `coordinator.command_service/device_refresh_service/mqtt_service`（稳定边界），不要继续依赖旧字段/旧签名。
   - 同时补齐 MQTT 生命周期的回调绑定与订阅 target fallback（见 1.5/1.6），否则 MQTT 可能“连上但不更新”或“无 group 直接失败”。

2) **对影子模块做一次明确决策：删 / 并 / 接回（不要悬空）**
   - “已有明确替代”的（如 MQTT policy/polling、coordinator_runtime）倾向直接删。
   - “生产已有消费者但未接回”的（如 product_config / outlet_power / group_lookup / developer_report）要么接回生产链路，要么删并同步清理消费者（实体、options、diagnostics、services）。

3) **让测试变“真绿”**
   - 避免 `MagicMock` 直接塞旧字段（`mqtt_connected/last_command_failure/async_refresh_devices/build_developer_report`），改为：
     - 真实 `Coordinator` + 真实 service handler 的集成测试；或
     - 至少 `spec_set/autospec` 锁住签名，避免旧接口悄悄通过。
