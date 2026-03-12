# 🜏 Lipro-HASS 审计问题清单

> **生成日期**: 2026-03-12
> **基于**: COMPREHENSIVE_AUDIT_2026-03-12.md
> **用途**: 逐项修复追踪

---

## 🔴 P0 问题（致命 - 会崩溃）

### [ ] P0-1: MQTT 资源泄漏
- **文件**: `custom_components/lipro/core/coordinator/coordinator.py`
- **问题**: 未重写 `async_shutdown()`，MQTT 连接在 unload 时未关闭
- **修复**: 添加方法重写，调用 `mqtt_runtime.disconnect()` 和 `mqtt_client.stop()`
- **预计时间**: 30 分钟

### [ ] P0-2: MQTT 消息处理任务未追踪
- **文件**: `custom_components/lipro/core/coordinator/mqtt_lifecycle.py:159-165`
- **问题**: `asyncio.create_task()` 异常会被静默吞噬
- **修复**: 使用 `background_task_manager.create()`
- **预计时间**: 15 分钟

### [ ] P0-3: Entity Protocol 类型不匹配
- **文件**: `custom_components/lipro/core/coordinator/entity_protocol.py:14`
- **问题**: `entity_id` 声明为 `str` 但实际可能为 `None`
- **修复**: 改为 `str | None`
- **预计时间**: 5 分钟

### [ ] P0-4: Device 增量刷新键不匹配
- **文件**: `custom_components/lipro/core/coordinator/runtime/device/incremental.py:103-110`
- **问题**: `devices.get(device_id)` 使用 API 的 `id`，但字典用 `serial` 作键
- **修复**: 使用 `device_identity_index.get(device_id)`
- **预计时间**: 1 小时

### [ ] P0-5: MqttRuntime.handle_message 签名不匹配
- **文件**: `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py:249`
- **问题**: Protocol 期望 `(topic, payload)`，实现是 `(device_id, properties)`
- **修复**: 更新 Protocol 或添加适配层
- **预计时间**: 30 分钟

### [ ] P0-6: CommandRuntime Protocol 方法抛出 NotImplementedError
- **文件**: `custom_components/lipro/core/coordinator/runtime/command_runtime.py:80-95`
- **问题**: `send_command()` 直接抛异常而非委托
- **修复**: 实现委托逻辑
- **预计时间**: 30 分钟

---

## 🟠 P1 问题（架构问题）

### Core 架构层

#### [ ] P1-1: StatusRuntime/TuningRuntime 未消费
- **文件**: `custom_components/lipro/core/coordinator/orchestrator.py:134-141, 160-213`
- **问题**: 装配但从未在 `_async_update_data()` 中调用
- **修复**: 注释掉装配代码，添加 TODO 标记 Phase H4
- **预计时间**: 15 分钟

#### [ ] P1-2: MQTT 订阅无 fallback
- **文件**: `custom_components/lipro/core/coordinator/services/mqtt_service.py:53-63`
- **问题**: 仅订阅 group 设备，无 group 时无订阅
- **修复**: 使用 `build_mqtt_subscription_device_ids()` helper
- **预计时间**: 20 分钟

#### [ ] P1-3: Device lock 竞态条件
- **文件**: `custom_components/lipro/core/coordinator/services/state_service.py:60-64`
- **问题**: 未知设备每次返回新锁，无互斥
- **修复**: 未知设备抛异常或缓存锁
- **预计时间**: 30 分钟

#### [ ] P1-4: Protocol 签名不匹配
- **文件**: `custom_components/lipro/core/coordinator/runtime/protocols.py` vs 实现
- **问题**: `MqttRuntimeProtocol` 与实现不一致
- **修复**: 更新 Protocol 定义
- **预计时间**: 15 分钟

#### [ ] P1-5: 重复 Protocol 定义
- **文件**: `custom_components/lipro/core/coordinator/runtime_context.py:22` vs `mqtt_runtime.py:38`
- **问题**: `DeviceResolverProtocol` 定义两次
- **修复**: 删除重复，统一导入
- **预计时间**: 10 分钟

#### [ ] P1-6: 浪费的 MqttRuntime 创建
- **文件**: `custom_components/lipro/core/coordinator/orchestrator.py:216-227`
- **问题**: 创建后立即被 `mqtt_lifecycle` 替换
- **修复**: 初始化为 `None`
- **预计时间**: 10 分钟

### Runtime 组件层

#### [ ] P1-7: Connect-status 刷新标志只写不读
- **文件**: `custom_components/lipro/core/coordinator/coordinator.py:85, 146-148`
- **问题**: CommandRuntime 设置但从未检查
- **修复**: 在 status 轮询中使用或删除
- **预计时间**: 30 分钟

#### [ ] P1-8: MQTT 轮询更新器从未设置
- **文件**: `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py:156-158`
- **问题**: `set_polling_updater()` 从未调用
- **修复**: 注入或删除功能
- **预计时间**: 20 分钟

#### [ ] P1-9: MQTT 断连通知从未调用
- **文件**: `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py:282-324`
- **问题**: `check_disconnect_notification()` 无调用点
- **修复**: 在 `_async_update_data()` 中调用或删除
- **预计时间**: 30 分钟

#### [ ] P1-10: 影子模块清理
- **文件**:
  - `custom_components/lipro/core/coordinator/runtime/group_lookup_runtime.py`
  - `custom_components/lipro/core/coordinator/runtime/product_config_runtime.py`
  - `custom_components/lipro/core/coordinator/runtime/state_batch_runtime.py`
  - `custom_components/lipro/core/coordinator/runtime/status_strategy.py`
- **问题**: 仅被测试引用，无生产路径
- **修复**: 移至 `tests/helpers/` 或删除
- **预计时间**: 1 小时

#### [ ] P1-11: StateRuntime.apply_properties_update 总是返回 True
- **文件**: `custom_components/lipro/core/coordinator/runtime/state/updater.py:49-91`
- **问题**: 未检查实际变更
- **修复**: 返回 `device.update_properties()` 的结果
- **预计时间**: 20 分钟

#### [ ] P1-12: DeviceRuntime 增量刷新忽略返回值
- **文件**: `custom_components/lipro/core/coordinator/runtime/device_runtime.py:108-114`
- **问题**: 返回数据未使用
- **修复**: 使用返回值或改为 `-> None`
- **预计时间**: 15 分钟

### API 层

#### [ ] P1-13: 硬编码签名密钥
- **文件**: `custom_components/lipro/const/api.py:12-13, 160`
- **问题**: `SMART_HOME_SIGN_KEY`, `IOT_SIGN_KEY`, `MQTT_AES_KEY` 在源码中
- **修复**: 添加注释说明这是从 APK 逆向的应用级常量
- **预计时间**: 5 分钟

#### [ ] P1-14: MD5 用于密码哈希和签名
- **文件**: `custom_components/lipro/core/api/auth_service.py:35-37`, `transport_signing.py:30-31`
- **问题**: MD5 已知弱算法
- **修复**: 添加注释说明这是供应商 API 限制
- **预计时间**: 5 分钟

#### [ ] P1-15: 递归 429 重试
- **文件**: `custom_components/lipro/core/api/transport_retry.py:96-109`
- **问题**: 递归实现可能栈溢出
- **修复**: 改为 `while` 循环
- **预计时间**: 30 分钟

#### [ ] P1-16: AuthApiService 紧耦合
- **文件**: `custom_components/lipro/core/api/auth_service.py:39, 54-67`
- **问题**: 直接访问 client 私有属性
- **修复**: 使用 `set_tokens()` 方法
- **预计时间**: 20 分钟

#### [ ] P1-17: 请求数据字典可覆盖框架键
- **文件**: `custom_components/lipro/core/api/request_codec.py:20-27`
- **问题**: `**data` 可能覆盖 `sign`, `optFrom` 等
- **修复**: 框架键后应用或验证冲突
- **预计时间**: 20 分钟

#### [ ] P1-18: 重复用户 ID 解析逻辑
- **文件**: `custom_components/lipro/core/api/auth_service.py:57-67, 105-115`
- **问题**: 相同逻辑重复两次
- **修复**: 提取 `_parse_user_id()` 方法
- **预计时间**: 15 分钟

### Device 模型 + MQTT

#### [ ] P1-19: Device factory 不完整的 extra_data 填充
- **文件**: `custom_components/lipro/core/device/device_factory.py:41-45`
- **问题**: 仅写入 `is_ir_remote`，其他字段运行时填充
- **修复**: 在 factory 中提取所有元数据或文档化可变设计
- **预计时间**: 2 小时

#### [ ] P1-20: group_status.py 死代码
- **文件**: `custom_components/lipro/core/device/group_status.py`
- **问题**: 零生产引用
- **修复**: 删除文件
- **预计时间**: 5 分钟

#### [ ] P1-21: MQTT `_connected` 状态漂移风险
- **文件**: `custom_components/lipro/core/mqtt/client_runtime.py:172-174`
- **问题**: 同步回调写入未加锁
- **修复**: 使用异步任务或文档化 best-effort 语义
- **预计时间**: 30 分钟

#### [ ] P1-22: MQTT 回调类型不匹配
- **文件**: `custom_components/lipro/core/mqtt/mqtt_client.py:32`, `mqtt_lifecycle.py:159-165`
- **问题**: 声明为同步但实际处理器是异步
- **修复**: 更新签名或文档化 fire-and-forget
- **预计时间**: 15 分钟

#### [ ] P1-23: 身份字段混淆
- **文件**: 多个文件
- **问题**: `serial` vs `iot_device_id` vs `device_id` 使用不一致
- **修复**: 统一使用 `serial`，弃用 `device_id` 属性
- **预计时间**: 2 小时

#### [ ] P1-24: AES-ECB 模式用于凭证解密
- **文件**: `custom_components/lipro/core/mqtt/credentials.py:23`
- **问题**: ECB 模式安全最佳实践违规
- **修复**: 添加注释说明 API 契约要求
- **预计时间**: 5 分钟

#### [ ] P1-25: SHA-1 用于 HMAC 签名
- **文件**: `custom_components/lipro/core/mqtt/credentials.py:65`
- **问题**: SHA-1 已弃用
- **修复**: 添加注释说明 MQTT broker 要求
- **预计时间**: 5 分钟

### Platform/Entity 层

#### [ ] P1-26: Unload 未停止 MQTT
- **文件**: `custom_components/lipro/__init__.py:150-165`
- **问题**: 仅调用 `async_shutdown()`，未调用 `mqtt_service.async_stop()`
- **修复**: 在 shutdown 前调用 `mqtt_service.async_stop()`
- **预计时间**: 10 分钟

#### [ ] P1-27: firmware_update.py 直接访问 coordinator.client
- **文件**: `custom_components/lipro/entities/firmware_update.py:260, 272`
- **问题**: 绕过服务层边界
- **修复**: 添加 OTA 服务方法
- **预计时间**: 1 小时

#### [ ] P1-28: Fan 绕过设备锁
- **文件**: `custom_components/lipro/fan.py:163`
- **问题**: `update_properties()` 未加锁
- **修复**: 重构为异步并加锁
- **预计时间**: 1 小时

### Services 层

#### [ ] P1-29: 未填充的 `group_member_ids` 字段
- **文件**: `custom_components/lipro/services/schedule.py:98`, `core/command/dispatch.py:98`
- **问题**: 读取但从未写入
- **修复**: 实现字段填充或删除消费者
- **预计时间**: 2 小时

#### [ ] P1-30: 未填充的 `gateway_device_id` 字段
- **文件**: `custom_components/lipro/services/schedule.py:97`
- **问题**: 读取但应使用计算属性
- **修复**: 使用 `device.ir_remote_gateway_device_id`
- **预计时间**: 15 分钟

#### [ ] P1-31: 异常层次不一致
- **文件**: `custom_components/lipro/core/exceptions.py`
- **问题**: 未使用的异常类与 `core/api/` 并行
- **修复**: 删除未使用的异常或合并层次
- **预计时间**: 30 分钟

### 测试代码

#### [ ] P1-32: 删除影子模块测试
- **文件**:
  - `tests/test_coordinator_runtime.py`
  - `tests/core/test_device_registry_sync.py`
  - `tests/core/test_group_lookup_runtime.py`
  - `tests/core/test_state_batch_runtime.py`
  - `tests/core/test_outlet_power_runtime.py`
- **问题**: 测试无生产调用者的模块
- **修复**: 删除测试文件
- **预计时间**: 30 分钟

#### [ ] P1-33: conftest_shared.py 反模式
- **文件**: `tests/conftest_shared.py:61-73`
- **问题**: 直接写入 `coordinator._state.devices`
- **修复**: 使用 `coordinator._async_update_data()`
- **预计时间**: 30 分钟

#### [ ] P1-34: 添加 spec_set 到 mocks
- **文件**: 多个测试文件
- **问题**: `MagicMock()` 无 `spec_set`
- **修复**: 使用 `spec_set=Coordinator`
- **预计时间**: 2 小时

---

## 🟡 P2 问题（代码异味）

### [ ] P2-1 至 P2-34: 详见完整审计报告

**类别**:
- 重复代码（密码哈希、强制转换函数、用户 ID 解析）
- 性能问题（防御性检查、分页断路器、过滤效率）
- 死代码（未使用字段、方法、导入）
- 不一致模式（命名、回调、docstring）

**预计总时间**: 8-10 小时

---

## ⚪ P3 问题（细节）

### [ ] P3-1 至 P3-17: 详见完整审计报告

**类别**:
- 命名不一致
- 缺失类型注解
- Magic numbers
- 代码风格

**预计总时间**: 4-6 小时

---

## 📊 修复进度追踪

| 优先级 | 总数 | 已完成 | 进行中 | 待处理 | 完成率 |
|--------|------|--------|--------|--------|--------|
| P0 | 6 | 0 | 0 | 6 | 0% |
| P1 | 34 | 0 | 0 | 34 | 0% |
| P2 | 34 | 0 | 0 | 34 | 0% |
| P3 | 17 | 0 | 0 | 17 | 0% |
| **总计** | **91** | **0** | **0** | **91** | **0%** |

---

## 🎯 建议修复顺序

### 第一阶段：关键修复（1-2 天）
1. 所有 P0 问题（6 个）
2. MQTT 资源管理相关 P1（P1-1, P1-2, P1-26）
3. 数据完整性 P1（P1-4, P1-19, P1-29, P1-30）

### 第二阶段：架构清理（2-3 天）
4. 删除影子模块和死代码（P1-10, P1-20, P1-32）
5. 修复边界违规（P1-27, P1-28）
6. 测试质量改进（P1-33, P1-34）

### 第三阶段：代码质量（3-4 天）
7. 所有 P2 问题
8. 重构重复代码
9. 性能优化

### 第四阶段：细节打磨（1-2 天）
10. 所有 P3 问题
11. 文档完善
12. 代码风格统一

**总预计时间**: 7-11 天

---

⛧ 虚空低语：清单已织就，每一裂隙皆有修复之路。愿汝逐项收口，代码重归完美。

**Iä! Iä! Code fhtagn!** 🜏
