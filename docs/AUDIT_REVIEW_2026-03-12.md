# 🜏 Lipro-HASS 审计复核与纠偏报告

> **复核日期**：2026-03-12
> **复核对象**：`docs/COMPREHENSIVE_AUDIT_2026-03-12.md`、`docs/AUDIT_ISSUES_CHECKLIST.md`
> **复核范围**：`lipro-hass` 下全部 Python 文件（生产代码 + 测试代码）
> **复核方式**：主代理仲裁 + 7 路并行子代理全量审阅 + 定向测试验证
> **结论定位**：本报告用于纠偏既有审计，不覆盖原文档；后续修复优先级请以本报告为准。

---

## 1. 执行摘要

### 1.1 总裁决

- **原审计不是完全错误，但不能原样采纳。**
- 它更适合作为“问题线索库”，**不适合作为最终优先级清单**。
- 主要偏差有三类：
  1. **范围统计失真**：原文称约 `255` 个 Python 文件；本次实际覆盖 `385` 个。
  2. **部分结论已过期**：如 `StatusRuntime/TuningRuntime 未消费`、`MQTT 订阅无 fallback`。
  3. **部分严重度拔高**：若干问题确实存在，但更像协议漂移、未接线或维护性问题，不应定为 `P0`。

### 1.2 修正后的总体判断

- **总体健康度**：`B / B+`
- **架构方向**：是对的，`RuntimeContext -> Orchestrator -> Runtime -> Service` 主线已成形。
- **当前真实风险中心**：
  - MQTT 生命周期收口不完整
  - 设备索引 / 增量刷新链路存在错配
  - 部分装配链路与协议层文档漂移
  - 测试通过率高，但对 OTA / MQTT 并发与真实 wiring 的护栏偏弱

---

## 2. 复核覆盖范围

### 2.1 全量覆盖统计

| 范围 | 文件数 |
|---|---:|
| 生产代码 `custom_components/` + `scripts/` | 228 |
| 测试代码 `tests/` | 157 |
| **合计** | **385** |

### 2.2 协同分工

| 分片 | 范围 | 文件数 |
|---|---|---:|
| A1 | `const` + `core/api` + `core/auth` | 43 |
| A2 | `core/coordinator` | 61 |
| A3 | `core` 其余域模块 | 70 |
| A4 | 顶层集成 / services / entities / scripts | 54 |
| A5 | API / Coordinator / type-checking 测试 | 32 |
| A6 | core 其余测试 | 69 |
| A7 | 其余测试 | 56 |
| **总计** |  | **385** |

### 2.3 主代理额外验证

- `uv run pytest lipro-hass/tests/core/mqtt/test_mqtt_setup.py ...` → `13 passed`
- `uv run pytest lipro-hass/tests/core/test_coordinator.py::TestCoordinatorRuntimeComponents::test_status_runtime_updates_device_through_coordinator_callbacks` → `1 passed`

---

## 3. 原审计中确认成立的部分

### 3.1 高优先级且成立

1. **MQTT 卸载释放缺口**
   - 证据：`custom_components/lipro/core/coordinator/coordinator.py:46` 未实现自定义 `async_shutdown()`。
   - 调用点：`custom_components/lipro/__init__.py:129`、`custom_components/lipro/__init__.py:157`。
   - 影响：配置卸载/重载后，MQTT 循环与协调器后台任务可能残留。

2. **MQTT 消息桥接任务未纳入统一任务管理**
   - 证据：`custom_components/lipro/core/coordinator/mqtt_lifecycle.py:159` 直接 `asyncio.create_task(...)`。
   - 影响：异常可漂出，任务在 unload 时也不会统一清理。

3. **增量刷新设备查找键错配**
   - 证据：`custom_components/lipro/core/coordinator/runtime/device/incremental.py:94` 使用 `devices.get(device_id)`。
   - 事实：当前主设备映射以 serial 为主键，增量查询返回的是 IoT/device id。
   - 影响：增量刷新命中率会异常偏低，属于真实逻辑缺陷。

4. **影子模块 / 未接线路径存在**
   - 代表文件：`custom_components/lipro/core/coordinator/runtime/group_lookup_runtime.py:1`、`custom_components/lipro/core/coordinator/runtime/product_config_runtime.py:1`、`custom_components/lipro/core/coordinator/runtime/state_batch_runtime.py:1`。
   - 现状：主要由测试引用，缺少生产调用链。

5. **`group_member_ids` / `gateway_device_id` 缺少生产写入链**
   - 读取点：`custom_components/lipro/services/schedule.py:97`、`custom_components/lipro/core/command/dispatch.py:98`。
   - 构造点：`custom_components/lipro/core/device/device_factory.py:41` 仅填充 `is_ir_remote`。

### 3.2 成立但应下调严重度

1. **协议 / 签名漂移**
   - 证据：`custom_components/lipro/core/coordinator/runtime/protocols.py:26`、`custom_components/lipro/core/coordinator/runtime/protocols.py:122`。
   - 判断：问题真实存在，但更像“类型层与装配层失配”，不是当前最紧迫的运行时崩溃点。

2. **`AuthApiService` 与 client 私有状态紧耦合**
   - 证据：`custom_components/lipro/core/api/auth_service.py:39`、`custom_components/lipro/core/api/auth_service.py:54`。
   - 判断：是边界收口问题，应列为 `中风险`，不宜拔到 `P1-high` 之上。

3. **`request_codec` 保留键可被覆盖**
   - 证据：`custom_components/lipro/core/api/request_codec.py:20`。
   - 判断：当前更像内部 footgun，尚不足以单独上升为安全级高危。

---

## 4. 原审计中不成立、已过期或表述过重的部分

1. **`StatusRuntime/TuningRuntime 未消费` — 不成立**
   - 证据：`custom_components/lipro/core/coordinator/coordinator.py:346`、`custom_components/lipro/core/coordinator/coordinator.py:356`、`custom_components/lipro/core/coordinator/coordinator.py:377`、`custom_components/lipro/core/coordinator/coordinator.py:392`。

2. **`MQTT 订阅无 fallback` — 不成立**
   - 证据：`custom_components/lipro/core/coordinator/mqtt_lifecycle.py:195` 调用 `build_mqtt_subscription_device_ids()`。

3. **`set_polling_updater()` 从未调用 — 不成立，但存在后续丢失**
   - 已调用：`custom_components/lipro/core/coordinator/coordinator.py:117`。
   - 真问题：真实 MQTT runtime 替换后未重新注入，见 `custom_components/lipro/core/coordinator/coordinator.py:338`。

4. **`CommandRuntime.send_command()` 直接抛异常属于 P0 — 表述过重**
   - 证据：`custom_components/lipro/core/coordinator/runtime/command_runtime.py:80`。
   - 判断：它是显式占位接口；现生产路径走 `send_device_command()`，测试也已固定这一点。

5. **`MqttRuntime.handle_message` 签名不匹配会直接崩 — 表述过重**
   - 真实消息回调传入的是 `device_id, properties`，见 `custom_components/lipro/core/mqtt/message_processor.py:118`。
   - `mqtt_lifecycle.py` 里的形参名虽写成 `topic`，但语义上接收的实际是 `device_id`。

6. **`power_info 被读取但从未写入` — 结论不精确**
   - 写入 helper 存在：`custom_components/lipro/core/coordinator/outlet_power.py:26`。
   - 真问题不是“没有写语句”，而是**生产调用链基本未接回**。

---

## 5. 本次复核新增的重要发现

### 5.1 高风险

1. **MQTT 连接态与真实传输层状态脱节**
   - 证据：`custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py:223` 在 `start()` 后立即 `on_connect()`。
   - 对照：真实底层握手完成在 `custom_components/lipro/core/mqtt/client_runtime.py:113` 之后。

2. **真实 MQTT runtime 替换后丢失 polling updater**
   - 证据：`custom_components/lipro/core/coordinator/coordinator.py:117` 只给初始化占位 runtime 注入；真实 runtime 在 `custom_components/lipro/core/coordinator/coordinator.py:338` 被替换。

3. **设备全量快照只追加注册 identity alias，未做原子重建**
   - 证据：`custom_components/lipro/core/coordinator/runtime/device/snapshot.py:114` 到 `custom_components/lipro/core/coordinator/runtime/device/snapshot.py:121`。
   - 影响：陈旧别名与旧映射可能残留。

### 5.2 中风险

4. **developer-only 服务默认暴露**
   - 注册点：`custom_components/lipro/services/registrations.py:67`。
   - 开关未生效：`custom_components/lipro/flow/options_flow.py:287`。

5. **远端固件认证清单缺少完整性校验**
   - 证据：`custom_components/lipro/firmware_manifest.py:67`、`custom_components/lipro/entities/firmware_update.py:157`。
   - 影响：远端“认证”结果会影响是否跳过未认证固件二次确认。

6. **集成层仍残留 direct client 访问**
   - 代表：`custom_components/lipro/entities/firmware_update.py:260`、`custom_components/lipro/services/diagnostics/handlers.py:184`、`custom_components/lipro/services/schedule.py:202`。

7. **匿名分享脱敏键集合仍可能漏掉 camelCase /短凭证变体**
   - 证据：`custom_components/lipro/core/anonymous_share/sanitize.py:31`。

### 5.3 低风险

8. **`fan` 平台存在一条绕过基类统一写路径的本地状态写入**
   - 证据：`custom_components/lipro/fan.py:144`、`custom_components/lipro/fan.py:163`。

9. **测试存在影子覆盖与烟雾测试命名过度**
   - 代表：`tests/type_checking/test_protocols.py:1`、`tests/type_checking/test_api_types.py:1`。

---

## 6. 修正后的优先级建议

### 6.1 立即处理（第一批）

1. MQTT 关闭链路补全：`Coordinator.async_shutdown()` 收口 MQTT 与后台任务。
2. MQTT bridge 改接 `BackgroundTaskManager`。
3. 修复增量刷新查找键错配。
4. 修复真实 MQTT runtime 替换后的 polling updater 丢失。

### 6.2 短期处理（第二批）

5. 修正 MQTT 连接态来源，避免伪“已连接”。
6. 原子重建 identity index，并明确 stale alias 清理策略。
7. 为 `group_member_ids` / `gateway_device_id` 建立真实填充链，或删除消费方依赖。
8. 为 developer-only 服务增加显式 opt-in。

### 6.3 中期治理（第三批）

9. 收口 direct client 访问到 service/facade。
10. 重新整理 runtime/protocol 文档，消除 `type: ignore` 式装配掩盖。
11. 清理影子模块与重复测试。
12. 补 OTA / MQTT 并发与真实 wiring 测试。

---

## 7. 对测试质量的最终评价

### 7.1 优点

- 大量 unit/helper 测试让纯函数与基础映射层较稳。
- `tests/core/test_init.py:1`、`tests/core/test_device_refresh.py:1`、`tests/core/test_mqtt.py:1`、`tests/core/test_coordinator.py:1` 仍是当前回归主力。

### 7.2 真实缺口

1. **OTA 共享缓存与并发去重护栏不足**。
2. **MQTT 真实装配链路测试不足**，很多测试直接戳 runtime，不走真实 bridge。
3. **type-checking 测试更像运行时烟雾**，不能代表真实静态契约守护。
4. **部分 service 测试只验证 delegation，不验证 orchestration 副作用**。

### 7.3 结论

- 当前测试体系不能支撑“全面覆盖、质量很高”的乐观表述。
- 更准确的说法应是：**基础分支覆盖不错，但对并发、生命周期、装配链路的回归防护仍偏弱。**

---

## 8. 最终结论

### 8.1 对原审计的最终定性

- **可保留**：作为问题线索与历史快照。
- **不可直接执行**：尤其是 `P0/P1` 优先级与若干已过期结论，必须先纠偏。

### 8.2 本次复核后的核心判断

- 这不是“架构失败”的代码库，而是一个**架构方向正确、但 lifecycle / wiring / test guardrails 还没完全收口**的代码库。
- 当前最该修的，不是所有文档里列出来的 `91` 条问题，而是少数几条**真实影响运行链路**的问题：
  - MQTT 关闭与任务治理
  - 增量刷新与索引一致性
  - MQTT 装配漂移
  - 测试对高风险路径的护栏补齐

### 8.3 建议执行原则

- **先修真实运行风险，再修协议/文档漂移。**
- **先补生命周期与并发护栏，再清理影子模块。**
- **先把测试变成真实护栏，再谈覆盖率数字。**

---

## 9. 附录：相关文档

- 原审计：`docs/COMPREHENSIVE_AUDIT_2026-03-12.md`
- 原清单：`docs/AUDIT_ISSUES_CHECKLIST.md`
- 残留审计：`docs/refactor_residual_audit.md`
- 本报告：`docs/AUDIT_REVIEW_2026-03-12.md`

