# 🜏 Lipro-HASS 全面代码审计报告（复核整合版）

> **整合日期**：2026-03-12
> **审计范围**：`lipro-hass` 下全部 Python 文件（生产代码 + 测试代码）
> **实际覆盖**：385 个 Python 文件（生产 228 / 测试 157）
> **审计方式**：主代理仲裁 + 7 路并行子代理全量审阅 + 定向测试验证
> **文档状态**：本报告已吸收原始审计与复核结果，当前为 **唯一权威审计报告**

---

## 0. TL;DR

### 总结论

- 代码库**不是失控状态**，而是一个**架构方向正确、但生命周期与装配链路尚未完全收口**的仓库。
- 原审计的很多问题**方向是对的**，但存在三类偏差：
  1. **覆盖统计失真**：原文写约 `255` 个 Python 文件，实际本次覆盖为 `385` 个。
  2. **结论已过期**：如 `StatusRuntime/TuningRuntime 未消费`、`MQTT 订阅无 fallback`。
  3. **严重度偏激进**：部分问题真实存在，但更像协议漂移、未接线或维护性问题，不该直接列入 `P0`。

### 当前最值得优先处理的 7 个问题

1. MQTT 卸载/重载时未完整释放连接与后台任务
2. MQTT bridge 任务未接入统一任务管理
3. 增量刷新使用错误索引键，导致状态回写命中率异常
4. 真实 MQTT runtime 替换后丢失 polling updater 注入
5. MQTT runtime 的连接态与真实传输层握手状态脱节
6. 全量快照只追加 identity alias，不做原子重建与陈旧别名清理
7. 测试通过率高，但对 OTA/MQTT 并发与真实 wiring 的护栏不足

---

### 0.1 2026-03-12 执行状态更新

- 第一批 `1.1`–`1.6` 已全部完成并验证。
- 第二批 `2.1`–`2.4` 已完成并验证，其中：
  - mesh group 元数据现由 **full snapshot + incremental refresh** 双路径回填；
  - `power_info` 已接回 `Coordinator._async_run_status_polling()` 正式主路径；
  - `schedule` / `diagnostics` / `firmware_update` 已改走 coordinator facade。
- 本轮验证：
  - `uv run pytest tests/services/test_services_schedule.py ... tests/core/test_init.py` → `302 passed`
  - `uv run pytest tests/core/test_command_dispatch.py ... tests/core/test_outlet_power.py` → `71 passed`
  - `uv run ruff check .` → 全绿

## 1. 审计范围与方法

### 1.1 文件覆盖

| 范围 | 文件数 |
|---|---:|
| `custom_components/` + `scripts/` | 228 |
| `tests/` | 157 |
| **合计** | **385** |

### 1.2 协同分工

| 分片 | 覆盖范围 | 文件数 |
|---|---|---:|
| A1 | `const` + `core/api` + `core/auth` | 43 |
| A2 | `core/coordinator` | 61 |
| A3 | 其余 `core` 域模块 | 70 |
| A4 | 顶层集成 / services / entities / scripts | 54 |
| A5 | API / Coordinator / type-checking 测试 | 32 |
| A6 | core 其余测试 | 69 |
| A7 | 其余测试 | 56 |
| **总计** |  | **385** |

### 1.3 主代理验证

- `uv run pytest lipro-hass/tests/core/mqtt/test_mqtt_setup.py ...` → `13 passed`
- `uv run pytest lipro-hass/tests/core/test_coordinator.py::TestCoordinatorRuntimeComponents::test_status_runtime_updates_device_through_coordinator_callbacks` → `1 passed`

---

## 2. 总体评估

### 2.1 健康度

- **总体健康度**：`B / B+`
- **架构成熟度**：主架构清晰，服务边界与运行时拆分方向正确。
- **主要短板**：
  - MQTT 生命周期收口不完整
  - 设备索引与增量刷新链路一致性不足
  - 部分 runtime/protocol 文档与实际实现漂移
  - 测试“有效护栏率”明显低于通过率

### 2.2 本次重排后的风险中心

| 优先级 | 主题 | 说明 |
|---|---|---|
| 高 | 生命周期 / 并发 | MQTT disconnect、task 管理、连接态、订阅同步 |
| 高 | 数据一致性 | 增量刷新索引键错配、identity index 重建缺口 |
| 中 | 边界收口 | direct client 访问、developer-only 服务暴露 |
| 中 | 数据模型闭环 | `group_member_ids` / `gateway_device_id` 生产写入缺失 |
| 中 | 文档/协议漂移 | runtime protocols 与真实实现不一致 |
| 中 | 测试护栏不足 | OTA/MQTT 并发路径、真实装配链路、type-checking 伪护栏 |

---

## 3. 确认成立的高优先级问题

### 3.1 MQTT 卸载释放缺口

- 证据：`custom_components/lipro/core/coordinator/coordinator.py:46`
- 调用点：`custom_components/lipro/__init__.py:129`、`custom_components/lipro/__init__.py:157`
- 现状：`Coordinator` 未实现自定义 `async_shutdown()`，卸载路径虽然会调用该方法，但不会主动执行 `mqtt_runtime.disconnect()`、`background_task_manager.cancel_all()`。
- 影响：配置重载后 MQTT 循环与协调器后台任务可能残留，形成幽灵更新与资源泄漏。
- 当前定级：**高**

### 3.2 MQTT bridge 任务未统一追踪

- 证据：`custom_components/lipro/core/coordinator/mqtt_lifecycle.py:159`
- 现状：消息桥接直接 `asyncio.create_task(...)`，绕过 `BackgroundTaskManager`。
- 影响：异常漂出、unload 时无法统一清理。
- 当前定级：**高**

### 3.3 增量刷新索引键错配

- 证据：`custom_components/lipro/core/coordinator/runtime/device/incremental.py:94`
- 现状：增量刷新通过 `devices.get(device_id)` 取设备，而主设备映射以 serial 为主键。
- 影响：状态回写命中率异常偏低，属于真实逻辑缺陷。
- 当前定级：**高**

### 3.4 真实 MQTT runtime 替换后丢失 polling updater

- 初始化注入：`custom_components/lipro/core/coordinator/coordinator.py:117`
- 替换点：`custom_components/lipro/core/coordinator/coordinator.py:338`
- 现状：占位 runtime 注入了 polling updater，但真实 runtime 在 setup 后替换，未重新注入。
- 影响：`MQTT connected -> 放宽轮询 / disconnect -> 恢复轮询` 设计实际上无法完整生效。
- 当前定级：**高**

### 3.5 MQTT runtime 连接态与真实握手状态脱节

- 证据：`custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py:223`
- 对照：真实传输层握手在 `custom_components/lipro/core/mqtt/client_runtime.py:113` 之后。
- 现状：runtime 在 `start()` 返回后立即标记连接成功，没有等待真实握手完成。
- 影响：REST fallback、诊断、断连通知会建立在错误连接态上。
- 当前定级：**高**

### 3.6 identity index 只增不重建

- 证据：`custom_components/lipro/core/coordinator/runtime/device/snapshot.py:114`
- 现状：全量快照构建时持续向共享 `DeviceIdentityIndex` 注册别名，未见原子 replace / clear 流程。
- 影响：陈旧别名或老设备映射可能滞留。
- 当前定级：**高**

### 3.7 影子模块仍制造“已接线”错觉

- 代表：
  - `custom_components/lipro/core/coordinator/runtime/group_lookup_runtime.py:1`
  - `custom_components/lipro/core/coordinator/runtime/product_config_runtime.py:1`
  - `custom_components/lipro/core/coordinator/runtime/state_batch_runtime.py:1`
  - `custom_components/lipro/core/coordinator/runtime/status_strategy.py:1`
- 现状：主要由测试引用，缺少真实生产调用链。
- 影响：维护者容易误以为能力已落地。
- 当前定级：**高（治理优先级）**

---

## 4. 确认成立的中优先级问题

### 4.1 `group_member_ids` / `gateway_device_id` 已建立真实生产闭环（2026-03-12 更新）

- 权威来源：mesh 组状态查询（`query_mesh_group_status` / `iotQueryMeshGroupStatus`）。
- 生产写入点：
  - `custom_components/lipro/core/coordinator/runtime/device/snapshot.py`
  - `custom_components/lipro/core/coordinator/runtime/device/incremental.py`
  - `custom_components/lipro/core/device/group_status.py`
- 当前状态：full snapshot 与 incremental refresh 都会把 `gatewayDeviceId` / `devices[].deviceId` 回填到 `device.extra_data`；schedule 侧对 gateway 的读取也支持 `ir_remote_gateway_device_id` 兜底。
- 当前定级：**已修复，转入观察**

### 4.2 `power_info` 已接回 coordinator 主路径（2026-03-12 更新）

- 写入 helper：`custom_components/lipro/core/coordinator/outlet_power.py`
- 主路径：`custom_components/lipro/core/coordinator/coordinator.py`
- 消费点：`custom_components/lipro/sensor.py`
- 当前状态：outlet power 查询已由 coordinator 正式轮询链路驱动，`power_info` 不再是孤立 helper/runtime 的悬空状态。
- 当前定级：**已修复，转入观察**

### 4.3 集成层 direct client 访问已收口到 coordinator facade（2026-03-12 更新）

- 收口范围：
  - `custom_components/lipro/entities/firmware_update.py`
  - `custom_components/lipro/services/diagnostics/handlers.py`
  - `custom_components/lipro/services/schedule.py`
- 当前状态：生产代码中已移除 `coordinator.client.*` 直达路径，后续认证、限流、遥测可继续在 facade 层集中演进。
- 当前定级：**已修复，转入观察**

### 4.4 developer-only 服务默认暴露

- 注册点：`custom_components/lipro/services/registrations.py:67`
- 调试开关：`custom_components/lipro/flow/options_flow.py:287`
- 现状：`debug_mode` 存在，但未参与 developer-only 服务注册判定。
- 当前定级：**中**

### 4.5 远端固件认证信任链过弱

- 证据：`custom_components/lipro/firmware_manifest.py:67`
- 消费点：`custom_components/lipro/entities/firmware_update.py:157`
- 现状：远端 manifest 仅校验 HTTP/JSON 可用性，未见签名校验或本地信任根优先策略。
- 当前定级：**中**

### 4.6 匿名分享脱敏规则对 camelCase / 变体键仍可能漏网

- 证据：`custom_components/lipro/core/anonymous_share/sanitize.py:31`
- 当前定级：**中**

### 4.7 `fan` 平台保留一条绕过统一 optimistic 写路径的本地写入

- 证据：`custom_components/lipro/fan.py:144`、`custom_components/lipro/fan.py:163`
- 现状：并非整个平台都绕锁，但这两个点确实直接写共享 device model。
- 当前定级：**中偏低**

---

## 5. 应下调、修正或驳回的旧结论

| 旧结论 | 新裁决 | 依据 |
|---|---|---|
| `StatusRuntime/TuningRuntime 未消费` | **驳回** | `Coordinator._async_run_status_polling()` 与 `CoordinatorCommandService.async_send_command()` 已真实消费 status/tuning runtime |
| `MQTT 订阅无 fallback` | **驳回** | `custom_components/lipro/core/coordinator/mqtt_lifecycle.py:195` 已使用 `build_mqtt_subscription_device_ids()` |
| `set_polling_updater() 从未调用` | **修正** | 调用过，但真实 runtime 替换后丢失 |
| `CommandRuntime.send_command()` 为 P0 | **下调** | 显式占位接口，生产路径走 `send_device_command()` |
| `MqttRuntime.handle_message` 签名不匹配会崩 | **下调** | 更接近协议层命名/文档漂移，不是当前主崩点 |
| `power_info 从未写入` | **修正并已完成修复** | 写入 helper 早已存在；本轮已将其接回 coordinator 正式主路径 |
| `硬编码签名密钥` | **下调** | 更像供应商协议常量，不是部署侧 secret 泄露 |
| `MD5 使用` | **下调** | 真实存在，但明显受供应商协议约束，应记录为兼容性约束 |

---

## 6. 测试体系复核结论

### 6.1 优点

- 纯 helper / unit 层的基础覆盖并不差。
- 以下文件仍是回归主力：
  - `tests/core/test_init.py:1`
  - `tests/core/test_device_refresh.py:1`
  - `tests/core/test_mqtt.py:1`
  - `tests/core/test_coordinator.py:1`

### 6.2 真实缺口

1. **OTA 共享缓存与并发去重缺少强护栏**
   - 代表：`tests/core/ota/test_ota_rows_cache.py:1`
2. **MQTT 真实 wiring 链路测试不足**
   - 许多测试直接调用 runtime，不经过真实 bridge。
3. **`tests/type_checking/*` 更像运行时烟雾测试**
   - 代表：`tests/type_checking/test_protocols.py:1`、`tests/type_checking/test_api_types.py:1`
4. **service 测试偏 delegation，副作用 orchestration 守护不足**
   - 代表：`tests/core/coordinator/services/test_command_service.py:1`
5. **benchmark 多为计时，不验证后置状态**
   - 代表：`tests/benchmarks/test_command_benchmark.py:1`

### 6.3 最终判断

- 当前测试体系不应被表述为“全面而强壮”。
- 更准确的结论是：**基础分支覆盖尚可，但并发、生命周期、装配链路的防回归能力仍不足。**

---

## 7. 修正后的执行顺序

### 第一批：立即修复

1. `Coordinator.async_shutdown()` 收口 MQTT 与后台任务
2. MQTT bridge 接入 `BackgroundTaskManager`
3. 修复增量刷新索引键错配
4. 真实 MQTT runtime 替换后重新注入 polling updater

### 第二批：短期修复

5. 修正 MQTT 连接态来源
6. identity index 改为原子重建
7. 补齐 `group_member_ids` / `gateway_device_id` 数据闭环，或移除消费依赖
8. developer-only 服务改为显式 opt-in

### 第三批：治理与补测

9. 收口 direct client 访问到 service/facade
10. 清理影子模块与重复测试
11. 补 OTA / MQTT 并发与真实 wiring 测试
12. 重写 runtime/protocol 文档，消除 `type: ignore` 掩盖装配漂移

---

## 8. 文档整合结果

### 当前建议保留的审计文档

1. `docs/COMPREHENSIVE_AUDIT_2026-03-12.md`
   - 作为**唯一权威审计报告**
2. `docs/AUDIT_ISSUES_CHECKLIST.md`
   - 作为**可执行修复清单**
3. `docs/refactor_residual_audit.md`
   - 作为**历史背景与前序收口记录**

### 已清理的中间文档

  - 已并入本报告与执行清单，不再单独保留。

---

## 9. 最终结论

- 这份仓库当前最重要的，不是继续堆更多“问题数量”，而是把**真实运行风险**先收掉。
- 真正该先做的，是：
  - 修 MQTT 生命周期
  - 修索引与增量刷新一致性
  - 修装配漂移
  - 把测试从“通过很多”变成“真能挡住回归”
- 后续修复优先级、任务拆分与验收条件，请直接使用 `docs/AUDIT_ISSUES_CHECKLIST.md`。
