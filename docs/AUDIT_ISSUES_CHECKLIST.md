# 🜏 Lipro-HASS 审计执行清单（复核整合版）

> **基于**：`docs/COMPREHENSIVE_AUDIT_2026-03-12.md`
> **用途**：按真实严重度执行修复，而不是按旧问题编号机械推进
> **状态定义**：`[ ]` 未开始 / `[~]` 进行中 / `[x]` 已完成 / `[-]` 记录但暂不执行

---

## 0. 使用规则

- 只以本清单为当前修复顺序依据。
- 原始 `P0/P1/P2` 编号不再直接沿用；若旧编号与本清单冲突，以本清单为准。
- 每个任务完成后，应补至少一条直接护栏测试，或明确记录“为何无法自动化验证”。

---

## 1. 第一批：真实运行风险（优先执行）

### [x] 1.1 为 `Coordinator` 实现完整 `async_shutdown()`
- **文件**：`custom_components/lipro/core/coordinator/coordinator.py`
- **目标**：在 unload / reload 时显式执行 MQTT disconnect、后台任务取消、必要 issue 清理与 runtime reset。
- **验收**：
  - `custom_components/lipro/__init__.py:129` 调用后不会残留 MQTT 连接循环
  - `BackgroundTaskManager` 挂载任务被清空
  - 补卸载/重载测试

### [x] 1.2 将 MQTT bridge 改接 `BackgroundTaskManager`
- **文件**：`custom_components/lipro/core/coordinator/mqtt_lifecycle.py`
- **目标**：替换裸 `asyncio.create_task(...)`，统一纳入任务追踪与异常消费。
- **验收**：
  - bridge 任务异常不会以未消费 task exception 形式漂出
  - unload 后 bridge 任务不会悬挂

### [x] 1.3 修复增量刷新索引键错配
- **文件**：`custom_components/lipro/core/coordinator/runtime/device/incremental.py`
- **目标**：改为通过 identity index 或等价统一查找层解析 `device_id -> device`。
- **验收**：
  - 增量刷新返回的 IoT/device id 能命中现有设备对象
  - 补针对性单测

### [x] 1.4 真实 MQTT runtime 替换后重新注入 polling updater
- **文件**：`custom_components/lipro/core/coordinator/coordinator.py`
- **目标**：`async_setup_mqtt()` 返回真实 runtime 后重新注入 updater，或改为构造期强依赖。
- **验收**：
  - 真实 runtime 的 `update_polling_interval()` 能影响 coordinator 轮询间隔
  - 补 setup 后断言测试

### [x] 1.5 修正 MQTT runtime 的连接态来源
- **文件**：
  - `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py`
  - `custom_components/lipro/core/coordinator/mqtt_lifecycle.py`
  - `custom_components/lipro/core/mqtt/mqtt_client.py`
- **目标**：只在真实握手成功后标记连接成功；disconnect/error 也要来自真实回调。
- **验收**：
  - 连接态与传输层真实状态一致
  - REST fallback / 诊断不会误判“已连接”

### [x] 1.6 设备快照后同步 MQTT 订阅集
- **文件**：
  - `custom_components/lipro/core/coordinator/coordinator.py`
  - `custom_components/lipro/core/coordinator/services/mqtt_service.py`
- **目标**：全量刷新后，即使 MQTT 已存在，也同步订阅集。
- **验收**：
  - 新增设备会被订阅
  - 移除设备会被取消订阅

---

## 2. 第二批：数据一致性与边界收口

### [x] 2.1 identity index 改为原子重建
- **文件**：`custom_components/lipro/core/coordinator/runtime/device/snapshot.py`
- **目标**：每次全量快照后原子 replace，而不是只增量 register。
- **验收**：
  - 陈旧别名不会残留
  - 旧设备删除后不再能通过历史 id 命中

### [x] 2.2 建立 `group_member_ids` / `gateway_device_id` 数据闭环
- **文件**：
  - `custom_components/lipro/core/device/group_status.py`
  - `custom_components/lipro/core/coordinator/runtime/device/snapshot.py`
  - `custom_components/lipro/core/coordinator/runtime/device/incremental.py`
  - `custom_components/lipro/services/schedule.py`
- **目标**：以 mesh 组状态查询为权威来源，在 coordinator runtime 内回填拓扑元数据，并让消费侧改依赖统一语义而非测试手填。
- **验收**：
  - full snapshot + incremental refresh 都会回填 `gateway_device_id` / `group_member_ids`
  - mesh group schedule 与 group command fallback 逻辑有明确数据来源
  - IR remote 场景可通过 `ir_remote_gateway_device_id` 派生 gateway，不再依赖手填 `extra_data`

### [x] 2.3 明确 `power_info` 主路径：接回或下线
- **文件**：
  - `custom_components/lipro/core/coordinator/coordinator.py`
  - `custom_components/lipro/core/coordinator/runtime/outlet_power_runtime.py`
  - `custom_components/lipro/core/coordinator/outlet_power.py`
  - `custom_components/lipro/sensor.py`
- **目标**：将 outlet power 查询正式纳入 coordinator 主轮询路径，而不是停留在孤立 helper/runtime。
- **验收**：
  - `Coordinator._async_run_status_polling()` 会在到期周期驱动 outlet power refresh
  - `power_info` 的写入来源与传感器读取路径一致
  - 传感器读取的是 coordinator 真实维护的状态，而非“永远没人写”的字段

### [x] 2.4 收口 direct client 访问到 service/facade
- **文件**：
  - `custom_components/lipro/core/coordinator/coordinator.py`
  - `custom_components/lipro/entities/firmware_update.py`
  - `custom_components/lipro/services/schedule.py`
  - `custom_components/lipro/services/diagnostics/handlers.py`
  - `custom_components/lipro/services/diagnostics/types.py`
- **目标**：实体/handler 统一改走 coordinator facade，不再直接触达 `coordinator.client.*`。
- **验收**：
  - schedule / diagnostics / firmware_update 已只依赖高层稳定接口
  - 认证、限流、遥测后续可继续在 facade 层集中收口
  - 生产代码中已清除 `coordinator.client.*` 直接访问

### [ ] 2.5 developer-only 服务改为显式 opt-in
- **文件**：
  - `custom_components/lipro/services/registrations.py`
  - `custom_components/lipro/services/wiring.py`
  - `custom_components/lipro/flow/options_flow.py`
- **目标**：仅在 `debug_mode` 或等价显式开关开启时注册/放行。
- **验收**：
  - 默认安装不暴露 developer-only 服务
  - 开启 debug_mode 后服务才可见/可调用

### [ ] 2.6 强化远端固件认证信任链
- **文件**：
  - `custom_components/lipro/firmware_manifest.py`
  - `custom_components/lipro/entities/firmware_update.py`
- **目标**：远端 manifest 不应单独决定“已认证可跳过确认”。
- **验收**：
  - 本地清单或签名校验成为最终信任根
  - 远端异常不会无提示放宽安装确认

### [ ] 2.7 补齐匿名分享脱敏规则
- **文件**：`custom_components/lipro/core/anonymous_share/sanitize.py`
- **目标**：补 camelCase / 变体键与短凭证场景。
- **验收**：
  - 敏感键变体不会漏过结构化脱敏
  - 补对应测试

### [ ] 2.8 收口 `fan` 的直接本地写入
- **文件**：`custom_components/lipro/fan.py`
- **目标**：复用基类 optimistic 写路径或统一 device lock。
- **验收**：
  - 不再存在绕过通用回滚/锁路径的共享状态写入

---

## 3. 第三批：测试护栏与影子清理

### [ ] 3.1 为 OTA 共享缓存补并发护栏测试
- **文件**：`tests/core/ota/test_ota_rows_cache.py`
- **目标**：覆盖共享缓存命中、并发 in-flight 去重、异常清理、过期重拉。

### [ ] 3.2 为 MQTT 真实 wiring 链路补测试
- **文件**：
  - `tests/integration/test_mqtt_coordinator_integration.py`
  - `tests/core/coordinator/runtime/test_mqtt_runtime.py`
- **目标**：验证 `LiproMqttClient -> bridge -> runtime -> coordinator` 真实链路，而不只是直接调用 runtime。

### [ ] 3.3 为 service orchestration 补副作用测试
- **文件**：
  - `tests/core/coordinator/services/test_command_service.py`
  - `tests/core/coordinator/services/test_device_refresh_service.py`
- **目标**：验证 fallback scheduling、refresh、user action/tuning 等副作用，而不只是 delegation。

### [ ] 3.4 清理 `tests/type_checking/*` 的伪护栏定位
- **文件**：
  - `tests/type_checking/test_protocols.py`
  - `tests/type_checking/test_api_types.py`
- **目标**：升级为真实静态检查入口，或明确降级为 smoke tests。

### [ ] 3.5 清理影子 runtime 测试与重复测试
- **代表文件**：
  - `tests/core/coordinator/runtime/test_connect_status_runtime.py`
  - `tests/core/coordinator/runtime/test_product_config_runtime.py`
  - 与 monolith 明显重复的 device/MQTT/边界测试
- **目标**：去掉“只有测试在消费”的伪落地表象。

### [ ] 3.6 benchmark 补充最小 postcondition 断言
- **文件**：`tests/benchmarks/*.py`
- **目标**：避免“快但错”的实现也被 benchmark 全绿掩盖。

---

## 4. 记录但不建议优先投入的项

### [-] 4.1 `CommandRuntime.send_command()` 占位接口
- **理由**：当前生产路径不依赖它；若无明确对外协议需求，可先不改。

### [-] 4.2 `硬编码签名密钥` / `MD5` 供应商协议约束
- **理由**：真实存在，但更适合作为兼容性约束记录，不是当前仓库第一优先级修复项。

### [-] 4.3 单纯“协议注释与实现不一致”但不影响真实运行的项
- **理由**：应放入第三批治理，与装配/测试收口一起做。

---

## 5. 执行完成标准

当以下条件全部满足时，可认为本轮审计问题真正收口：

- MQTT unload/reload 不再遗留连接或后台任务
- 增量刷新与 identity index 查找一致
- 真实 MQTT runtime 的 polling updater 与连接态都与生产路径一致
- `group_member_ids` / `gateway_device_id` / `power_info` 的来源与消费关系明确
- developer-only 服务不再默认暴露
- OTA/MQTT 并发与真实 wiring 测试补齐
- 影子模块 / 影子测试不再制造“已覆盖”错觉

---

## 6. 文档定位

- 权威报告：`docs/COMPREHENSIVE_AUDIT_2026-03-12.md`
- 可执行清单：`docs/AUDIT_ISSUES_CHECKLIST.md`
- 历史背景：`docs/refactor_residual_audit.md`
