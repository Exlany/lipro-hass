# Lipro 重构收口残留审查报告（Legacy / Compat Residual Audit）

> **生成日期**：2026-03-11
>
> **审查范围**：`lipro-hass/custom_components/lipro/` + `lipro-hass/tests/`（仅静态审阅，不做代码修改）
>
> **目标**：识别“新架构（RuntimeContext + Orchestrator + Runtime 组件 + Service 层）”落地后，仍残留的旧接口、兼容层、影子模块（仅测试引用/无生产路径引用/生产路径未接回）。

---

## 0. TL;DR（最关键结论）

### P0（高风险：真实运行可能直接报错）

1) **HA Service 仍按旧 Coordinator API 调用**，与当前 `Coordinator` 不一致：
- `send_command`：旧签名 `fallback_device_id` + 旧字段 `last_command_failure`（见 `custom_components/lipro/services/command.py`）
- `refresh_devices`：调用 `coordinator.async_refresh_devices()`（见 `custom_components/lipro/services/maintenance.py`）
- `async_execute_coordinator_call()`：假设 Coordinator 存在旧签名 `_trigger_reauth(key, **placeholders)`（见 `custom_components/lipro/services/execution.py`）

2) **HA diagnostics 仍直接读取旧字段 `coordinator.mqtt_connected`**，当前 Coordinator 不提供该属性（见 `custom_components/lipro/diagnostics.py`）。

> 备注：这类问题在测试里被 `MagicMock` 旧接口掩盖，导致“测试全绿但真实运行会炸”。

### P1（中风险：架构/类型漂移，后续维护成本高）

- `custom_components/lipro/core/coordinator/runtime/protocols.py`：内容与当前实现不一致、且未见生产引用（疑似旧草案遗留）。
- `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py`：保留 `legacy compatibility` 方法（`set_polling_updater()` / `setup()`），并存在注入形态不统一导致的 `type: ignore[arg-type]`（见 `custom_components/lipro/core/coordinator/orchestrator.py`）。
- `get_developer_report` 服务链路仍依赖旧接口：期望 `coordinator.build_developer_report()`，但当前 `Coordinator` 未实现（且 `core/utils/developer_report.py` 处于“未接回”状态）。

### P2（低风险但噪音大：影子模块 / 未接回生产路径）

存在一批“仅 tests 引用”的纯函数模块、以及“已装配但生产未调用”的 runtime 组件链路。详见第 2 节对照表。

---

## 1. P0 残留明细（接口不一致 / 真实运行风险）

### 1.1 `send_command` 服务：旧签名/旧字段残留

- 旧调用点：`custom_components/lipro/services/command.py:65` 调用：
  - `coordinator.async_send_command(..., fallback_device_id=...)`
  - 失败时读取 `coordinator.last_command_failure`（`custom_components/lipro/services/command.py:74`）
- 当前新 Coordinator：`custom_components/lipro/core/coordinator/coordinator.py:281`
  - `async_send_command(self, device, command, properties) -> bool`（不支持 `fallback_device_id`）
  - Coordinator 未暴露 `last_command_failure` 字段；新架构对应概念在 `command_service.last_failure`（`custom_components/lipro/core/coordinator/services/command_service.py:39`）

**测试掩盖点**：`tests/core/test_init.py:2096` 起使用 `MagicMock` 自行塞入旧签名/旧字段。

### 1.2 `refresh_devices` 服务：调用不存在的 `coordinator.async_refresh_devices()`

- 调用点：`custom_components/lipro/services/maintenance.py:65`
- 当前 Coordinator 未实现 `async_refresh_devices()`（生产代码 `rg` 仅命中 protocol / service adapter / tests）
- 新架构中最接近的能力：`custom_components/lipro/core/coordinator/services/device_refresh_service.py:45`（`device_refresh_service.async_refresh_devices()`）

### 1.3 Service 执行器：`_trigger_reauth` 旧签名残留（真实触发 reauth 时会 TypeError）

- 旧假设：`custom_components/lipro/services/execution.py:21` 声明 `_trigger_reauth(self, key: str, **placeholders)`
- 实际 Coordinator：`custom_components/lipro/core/coordinator/coordinator.py:135` 为 `_trigger_reauth(self, reason: str)`
- 触发路径：当 `async_execute_coordinator_call()` 捕获 `LiproAuthError` / `LiproRefreshTokenExpiredError` 时会调用 `_trigger_reauth(key, **placeholders)`（`custom_components/lipro/services/execution.py:85` 起）

### 1.4 HA diagnostics：直接读取 `coordinator.mqtt_connected`（当前 Coordinator 无此属性）

- 调用点：`custom_components/lipro/diagnostics.py:248`、`custom_components/lipro/diagnostics.py:282`
- 当前 Coordinator 仅提供 `_is_mqtt_connected()` 回调（`custom_components/lipro/core/coordinator/coordinator.py:142`），以及 `mqtt_service.connected`（`custom_components/lipro/core/coordinator/services/mqtt_service.py:34`）。

> 对比：`custom_components/lipro/system_health.py` 使用 `getattr(coordinator, "mqtt_connected", None)`，因此不会崩溃，但字段会长期缺失/漂移。

### 1.5 `get_developer_report` 服务：`build_developer_report()` 未接回新 Coordinator

- 服务链路：
  - `custom_components/lipro/services/wiring.py` → `_async_handle_get_developer_report()`
  - → `custom_components/lipro/services/diagnostics/helpers.py:130` `collect_developer_reports()`
  - → 过滤 `callable(getattr(coordinator, "build_developer_report", None))` 后调用 `coordinator.build_developer_report()`
- 当前新架构现状：
  - `custom_components/lipro/core/utils/developer_report.py:332` 提供 `build_developer_report(...)` 纯函数构建器，但**未见生产调用点**。
  - `custom_components/lipro/core/coordinator/coordinator.py` 未实现 `build_developer_report()` 方法。

**影响**：`get_developer_report` 很可能始终返回 `entry_count=0`（不会崩溃，但属于“迁移未完成/功能缺口”）。

---

## 2. P2 影子模块对照表（“它是什么”→“新架构替代在哪里”→“建议删/并/接回”）

说明：此处“影子模块”指 **仅 tests 引用 / 或当前生产路径完全未引用** 的模块（含为旧实现保留的策略函数）。

| 影子模块 | 主要职责 | 当前引用情况 | 新架构替代/对应位置 | 建议（删/并/接回） |
|---|---|---|---|---|
| `core/coordinator/mqtt/policy.py` | MQTT 断连时间/通知/放宽轮询间隔策略 | 仅 tests 引用（见 `tests/core/mqtt/test_mqtt_lifecycle.py`） | 连接状态与轮询放宽：`core/coordinator/runtime/mqtt/connection.py:43`；断连通知：`core/coordinator/runtime/mqtt_runtime.py:277` | **删**（已被新实现覆盖） |
| `core/coordinator/mqtt/polling.py` | 从 options 解析 scan interval；MQTT connect/disconnect 时轮询策略 | 仅 tests 引用（通过 `policy.py`） | scan interval 读取：`custom_components/lipro/__init__.py:69`（`get_entry_int_option`）；轮询放宽：`core/coordinator/runtime/mqtt/connection.py:58` | **删/并**（若仍需纯函数测试，考虑并入 `connection.py`） |
| `core/coordinator/runtime/coordinator_runtime.py` | 是否刷新设备列表、是否应调度 MQTT setup 的纯决策函数 | 仅 tests 引用（`tests/core/test_coordinator_runtime.py`） | 设备刷新判定：`core/coordinator/runtime/device_runtime.py:150`；MQTT setup：`core/coordinator/coordinator.py:411`（当前已内联） | **删**（逻辑已迁移且重复） |
| `core/coordinator/runtime/connect_status_runtime.py` | connect-status 查询间隔与 stale window 自适应（偏旧设计） | 仅 tests 引用（`tests/core/coordinator/runtime/test_connect_status_runtime.py`） | **无完整替代**；现仅存在简化版：`core/coordinator/runtime/tuning/algorithm.py:70`（仅 base/degraded）+ `device.has_recent_mqtt_update()`（`core/device/device.py:79`） | **接回或删**：若要实现 connect-status 轮询，应补齐消费链路（见下方“未接回链路”） |
| `core/coordinator/runtime/status_strategy.py` | connect-status candidate + 自适应 batch size（偏旧设计） | 仅 tests 引用（`tests/core/test_status_strategy.py`） | 现有状态查询策略：`core/coordinator/runtime/status/strategy.py:15`（更简化）；自适应思路在 `tuning_runtime.py`（但生产未用） | **删/并**（若继续要自适应，建议并入 tuning/status 的现实现） |
| `core/coordinator/runtime/state_batch_runtime.py` | state batch metric 归一化与统计 | 仅 tests 引用（`tests/core/test_state_batch_runtime.py`） | 近似替代：`core/coordinator/runtime/tuning/metrics.py`（通过 `TuningRuntime.record_batch_metric()` 记录/聚合） | **删/并**（若 tuning 真要用，合并到 tuning/metrics） |
| `core/coordinator/outlet_power.py` | outlet power 写入 extra_data + 错误升级策略 | 仅 tests 引用（`tests/core/test_outlet_power.py`） | **无完整替代**；现仅有 API endpoint：`core/api/endpoints/misc.py:45`（`fetch_outlet_power_info`） | **接回或删**：若不做功耗能力，建议删；若做，见 `outlet_power_runtime.py` |
| `core/coordinator/runtime/outlet_power_runtime.py` | 并发查询 outlet 功耗并回写 | 仅 tests 引用（`tests/core/test_outlet_power_runtime.py`） | **无生产替代**；`StatusScheduler` 仅保留切片逻辑：`core/coordinator/runtime/status/scheduler.py:46`，但未有执行器接入 | **接回或删**：若要功耗，建议接到 coordinator update loop 或独立 runtime；否则删 |
| `core/coordinator/runtime/product_config_runtime.py` | 匹配 `get_product_configs()` 并覆盖设备模型（色温/风档） | 仅 tests 引用（`tests/core/coordinator/runtime/test_product_config_runtime.py`） | **无生产替代**；仅有 endpoint：`core/api/endpoints/devices.py:32`（`get_product_configs`）与静态默认：`core/device/profile.py` | **接回或删**：若要动态能力，建议接回 `DeviceRuntime.refresh_devices()` 后处理 |
| `core/coordinator/device_registry_sync.py` + `core/coordinator/runtime/room_sync_runtime.py` | 云端 room → HA area 同步、清理 stale registry device | 无生产引用（仅 `room_sync_runtime.py` 被其引用 + tests） | **无生产替代**；当前只有“device registry disable/enable reload”监听：`custom_components/lipro/services/maintenance.py:109` | **接回或删**：若该功能已放弃则删；若保留应接到 refresh 结束后的 reconcile 阶段 |
| `core/coordinator/runtime/group_lookup_runtime.py` | mesh group gateway/member lookup-id 映射决策 | 仅 tests 引用（`tests/core/test_group_lookup_runtime.py`） | **无生产替代**；当前仅有解析 helper：`core/device/group_status.py:18`（只解析不落盘） | **接回或删**：若 schedule/diagnostics 依赖 `extra_data[group_member_ids]`，建议接回；否则删并清理依赖 |
| `core/utils/developer_report.py` | 构建“运行态开发者报告”（脱敏、摘要、命令轨迹等） | 无生产引用（仅自身 + tests/服务协议提及） | **无替代**；理想形态是由 `Coordinator.build_developer_report()` 调用本模块并注入 runtimes 状态 | **接回或删**：若保留服务则接回（补 Coordinator facade）；若不需要服务则连同 service/翻译/图标一并删除 |
| `core/device/group_status.py` | mesh group status payload 解析为 gateway/member IDs | 无生产引用（仅自身） | **无替代**；如需 mesh 组成员映射，建议与 `group_lookup_runtime.py` 合并并接入生产链路 | **并/接回或删**：若 mesh 组能力将继续演进则并入接回；否则删以减少噪音 |

---

## 3. “已装配但未接回”的链路（不属于单个影子模块，但体现迁移未收口）

以下属于“新架构里看起来有部件，但生产更新循环未调用/未消费”的典型症状，容易造成维护者误判：

### 3.1 `StatusRuntime` / `TuningRuntime` 目前仅被 Orchestrator 装配，但未进入 `Coordinator._async_update_data()`

- 装配：`custom_components/lipro/core/coordinator/orchestrator.py:134`（tuning）、`:197`（status）
- 访问器：`custom_components/lipro/core/coordinator/coordinator.py:172` 起仅提供 `@property`，生产路径未调用。

### 3.2 connect-status refresh 标志位被写入但无人消费

- 写入：`custom_components/lipro/core/coordinator/runtime/command_runtime.py:195`（成功命令后设置 priority ids + `force_connect_status_refresh_setter(True)`）
- 状态位：`custom_components/lipro/core/coordinator/coordinator.py:146` 设置 `_force_connect_status_refresh`
- 但：`Coordinator._async_update_data()` 未读取该标志位，也未执行任何 connect-status 查询逻辑。

### 3.3 `Coordinator` 内部存在未使用的“旧实现残片”方法

- `custom_components/lipro/core/coordinator/coordinator.py:302` `_query_device_status_batch()`：
  - 与 `RuntimeOrchestrator` 内部 closure（`custom_components/lipro/core/coordinator/orchestrator.py:157`）职责重复
  - `rg` 未发现任何生产调用点，疑似从旧实现迁移时遗留
- `custom_components/lipro/core/coordinator/coordinator.py:348` `_async_trigger_reauth()`：
  - 当前也未见调用点；与 `RuntimeContext` 回调 `_trigger_reauth()`（`custom_components/lipro/core/coordinator/coordinator.py:135`）职责重叠

**建议**：若确认无需，倾向删除以避免维护者误认为“存在并被调用的链路”。

---

## 4. 其他“兼容层残留”（不一定是影子模块，但属于刻意保留的兼容面）

这类残留多为“对外 API/旧测试/旧导入路径兼容”，不一定需要删除，但应在文档里明确其存在目的：

- `custom_components/lipro/core/api/client.py:24` `_build_compat_list_payload()` + `get_device_list()`：为旧 payload 形态（`{"data": [...]}`）与分页习惯提供兼容。
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py:75`：同时兼容 `{"data": [...]}` 与旧格式 `{"devices": [...]}`。
- `custom_components/lipro/core/api/client_transport.py:65` 保留 `self._session` 字段：仅为测试 patch logger/字段兼容。
- `custom_components/lipro/core/auth/manager.py:305` `async_ensure_authenticated()`：明确标注为“Compatibility wrapper”，用于收口 coordinator 更新流调用面。
- `custom_components/lipro/services/diagnostics/__init__.py`：re-export 维持旧导入路径（显式写明 backward compatibility）。
- `custom_components/lipro/runtime_types.py:7` / `custom_components/lipro/coordinator_entry.py:5`：类型/导出层面的兼容 shim。

---

## 5. 建议的下一步收口策略（仅供决策）

1) **优先修 P0：统一“HA service handler → Coordinator”契约**
   - 要么让 services 改用 `coordinator.command_service/device_refresh_service/mqtt_service`（稳定边界）
   - 要么在 `Coordinator` 上补齐旧 facade（但会长期背负兼容债）

2) **对影子模块做一次明确决策：删 / 并 / 接回（不要悬空）**
   - “已有明确替代”的（如 MQTT policy/polling、coordinator_runtime）倾向直接删。
   - “功能仍需要但未接回”的（如 product_config / outlet_power / room sync / group lookup）要么接回生产，要么删并同步清理依赖点。

3) **让测试覆盖“真实 Coordinator + 真实 service handler”**
   - 避免 `MagicMock` 旧字段导致的伪绿。
