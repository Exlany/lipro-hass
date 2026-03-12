# 🜏 Lipro-HASS 全面代码审计报告（复核整合版）

> **整合日期**：2026-03-12
> **审计范围**：`lipro-hass` 下全部 Python 文件（生产代码 + 测试代码）
> **实际覆盖**：385 个 Python 文件（生产 228 / 测试 157）
> **审计方式**：主代理仲裁 + 7 路并行子代理全量审阅 + 定向测试验证
> **文档状态**：本报告已吸收原始审计与复核结果，当前为 **唯一权威审计报告**

---

## 0. TL;DR

### 总结论

- 代码库**不是失控状态**，而是一个**架构方向正确，且本轮已完成生命周期、装配链路与测试护栏关键收口**的仓库。
- 原审计的很多问题**方向是对的**，但存在三类偏差：
  1. **覆盖统计失真**：原文写约 `255` 个 Python 文件，实际本次覆盖为 `385` 个。
  2. **结论已过期**：如 `StatusRuntime/TuningRuntime 未消费`、`MQTT 订阅无 fallback`。
  3. **严重度偏激进**：部分问题真实存在，但更像协议漂移、未接线或维护性问题，不该直接列入 `P0`。

### 当前最值得优先处理的 7 个问题

> **2026-03-12 执行更新**：本节列出的 7 个真实高优先问题已全部收口，当前剩余事项主要转为第 4 节记录类治理项，而非运行时崩溃风险。

1. MQTT 卸载/重载时未完整释放连接与后台任务
2. MQTT bridge 任务未接入统一任务管理
3. 增量刷新使用错误索引键，导致状态回写命中率异常
4. 真实 MQTT runtime 替换后丢失 polling updater 注入
5. MQTT runtime 的连接态与真实传输层握手状态脱节
6. 全量快照只追加 identity alias，不做原子重建与陈旧别名清理
7. 测试通过率高，但对 OTA/MQTT 并发与真实 wiring 的护栏不足

---

### 0.1 2026-03-12 执行状态更新

- 第一批 `1.1`–`1.6`、第二批 `2.1`–`2.8`、第三批 `3.1`–`3.6` 已全部完成并验证。
- 本轮完成的关键收口：
  - developer-only 服务改为 **debug_mode 显式 opt-in**，默认安装不再暴露。
  - OTA 认证信任根改为 **inline + local manifest**，远端 manifest 仅作 advisory 元数据。
  - 匿名分享脱敏补齐 camelCase / 变体键 / 短凭证场景，`fan` 平台已回归统一 optimistic 写路径。
  - OTA 共享缓存、MQTT 真实 wiring、service orchestration、benchmark 后置断言、影子 runtime/test/type-checking 伪护栏已全部收口。
  - `custom_components/lipro/core/coordinator/coordinator.py` 与相关测试类型边界已补齐，`uv run mypy` 重新转绿。
- 本轮验证：
  - `uv run ruff check .` → 全绿
  - `uv run mypy` → `Success: no issues found in 372 source files`
  - `uv run pytest ...`（跨批回归集合）→ `454 passed`

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
- **当前剩余议题**：
  - 第 4 节记录类兼容性约束仍需长期维护
  - 个别历史文档仍可继续去噪与收敛
  - 回归集合应固化为后续合并前基线

### 2.2 本次重排后的风险中心

| 优先级 | 主题 | 说明 |
|---|---|---|
| 中 | 兼容性约束 | 供应商协议常量、`MD5`、签名材料等记录项仍需持续跟踪 |
| 中 | 文档治理 | 历史审计/重构文档仍需按当前实现继续去噪 |
| 低 | 回归基线维护 | `ruff` / `mypy` / 关键回归集合需保持常态化执行 |

---

## 3. 已确认并已收口的高优先级问题

> **2026-03-12 执行更新**：本节问题保留为“问题来源 + 修复背景”，当前均已完成修复并进入回归观察。


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

### 4.4 developer-only 服务默认暴露（2026-03-12 更新）

- 修复点：`custom_components/lipro/services/registrations.py`、`custom_components/lipro/services/wiring.py`、`custom_components/lipro/__init__.py`
- 当前状态：developer-only 服务已改为 **显式 opt-in**；仅当存在开启 `debug_mode` 的 runtime entry 时才注册并放行。
- 当前定级：**已修复，转入观察**

### 4.5 远端固件认证信任链过弱（2026-03-12 更新）

- 修复点：`custom_components/lipro/core/ota/candidate.py`、`custom_components/lipro/firmware_manifest.py`
- 当前状态：`certified` 最终信任根已收口到 **inline + local manifest**；远端 manifest 不再单独放宽安装确认。
- 当前定级：**已修复，转入观察**

### 4.6 匿名分享脱敏规则对 camelCase / 变体键仍可能漏网（2026-03-12 更新）

- 修复点：`custom_components/lipro/core/anonymous_share/sanitize.py`
- 当前状态：已覆盖 camelCase、snake_case、短 token/key 及设备/网关/网络标识等变体，并补齐对应测试。
- 当前定级：**已修复，转入观察**

### 4.7 `fan` 平台保留一条绕过统一 optimistic 写路径的本地写入（2026-03-12 更新）

- 修复点：`custom_components/lipro/fan.py`
- 当前状态：直接本地写共享 device model 的路径已删除，平台重新统一走 optimistic/debounced 更新路径。
- 当前定级：**已修复，转入观察**

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

### 6.2 已完成收口的测试缺口（2026-03-12 更新）

1. **OTA 共享缓存与并发去重护栏已补齐**
   - 文件：`tests/core/ota/test_ota_rows_cache.py:1`
2. **MQTT 真实 wiring 链路已补真实 bridge 测试**
   - 文件：`tests/integration/test_mqtt_coordinator_integration.py:1`
3. **`tests/type_checking/*` 已降级为 smoke，并移除 tests-only 协议接口**
   - 文件：`tests/core/api/test_api_types_smoke.py:1`、`.github/workflows/ci.yml:1`
4. **service orchestration 已补副作用护栏**
   - 文件：`tests/core/coordinator/services/test_command_service.py:1`、`tests/core/coordinator/services/test_device_refresh_service.py:1`
5. **benchmark 已补最小后置状态断言**
   - 文件：`tests/benchmarks/test_command_benchmark.py:1`、`tests/benchmarks/test_mqtt_benchmark.py:1`、`tests/benchmarks/test_device_refresh_benchmark.py:1`、`tests/benchmarks/test_coordinator_performance.py:1`
6. **仓库级静态检查重新转绿**
   - 验证：`uv run mypy` → `Success: no issues found in 372 source files`

### 6.3 最终判断

- 当前测试体系已不再只是“通过很多但护栏虚弱”。
- 更准确的结论是：**基础回归、并发缓存、MQTT 真实装配链路、service orchestration 与 benchmark 后置状态，均已建立有效防回归护栏。**

---

## 7. 修正后的执行顺序

### 当前执行状态（2026-03-12 更新）

1. 第一批：**已完成**
2. 第二批：**已完成**
3. 第三批：**已完成**

### 后续建议

1. 维持当前 `ruff` / `mypy` / 回归集合为合并前基线
2. 对第 4 节记录类事项按“兼容性约束 / 文档治理”节奏处理
3. 若继续做架构演进，优先围绕 facade 契约稳定性与残余历史文档去噪推进

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

- 本轮审计对应的**真实运行风险与测试护栏缺口已经完成收口**。
- 当前更重要的，不是继续扩张问题清单，而是把现有 `ruff` / `mypy` / 回归测试集固化为持续基线。
- 后续若继续推进，请以 `docs/AUDIT_ISSUES_CHECKLIST.md` 中第 4 节记录项为治理清单，并优先清理剩余历史文档噪音。
