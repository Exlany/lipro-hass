# 更新日志

本项目的重要变更都会记录在本文件中。

格式参考 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，并遵循
[语义化版本](https://semver.org/spec/v2.0.0.html)。

## [Unreleased]（未发布）

### 新增（Added）

- 一键安装脚本，便于自定义集成部署。
- 设备诊断报告导出，并增强诊断脱敏相关测试覆盖。
- `rest.device-list` / `rest.device-status` / `rest.mesh-group-status` 的 canonical boundary contracts 与 replay/contract fixtures。
- `AuthSessionSnapshot` formal auth/session contract，供 `config_flow` / `entry_auth` / control adapters 统一消费。
- 维护者附录现已显式指向 latest archived evidence index（`.planning/reviews/V1_21_EVIDENCE_INDEX.md`）与 archived milestone audit（`.planning/v1.21-MILESTONE-AUDIT.md`），保持 release pull-chain 单一路由。

### 变更（Changed）

- 迁移依赖元数据到 `pyproject.toml`，并引入 `uv.lock`。
- 将 CI 的类型检查合并到 lint 工作流，减少重复环境初始化。
- 重构 coordinator 的更新/指令工作流，提升可维护性。
- 重构匿名分享能力检测逻辑，改为更清晰的规则映射。
- 重构共享 sensor 实体初始化，并进行更广泛的类型安全/代码质量清理。
- 删除 room sync / stale-device 的 shadow runtime 链（含历史 `device_registry_sync.py`），让正式 coordinator 主链只保留编排职责。
- 重构 device identity index，使用更严格的注册 API，并移除遗留的直接修改兼容路径。
- 移除 `core.api` 的旧兼容别名，改为使用标准子模块符号（`api_response_safety` / `request_policy`）。
- 移除 `login_with_hash` 兼容入口；config flow 直接使用
  `login(..., password_is_hashed=True)`。
- 重构平台模块：直接导入 helper 子模块，移除 `helpers` 包级兼容 re-export。
- 移除根模块遗留的 service contract re-export；以 `services/contracts.py` 作为权威来源。
- `core/__init__.py` 不再导出 `Coordinator`；HA runtime-home public surface 固定为 `custom_components/lipro/coordinator_entry.py`。
- control adapters 改为消费 formal auth/session/result contracts，而不是依赖 raw login dict shape。
- governance / replay / meta guards 已同步到 `Phase 10 completed` 口径，future-host 叙事仅允许建立在 formal boundary/auth/device nucleus 之上。
- maintainer-facing release route 现统一承认 `docs/README.md` maintainer appendix → `docs/MAINTAINER_RELEASE_RUNBOOK.md` → version-sync triad / tagged workflows / archived evidence pointer 的单一路径。
- release notes 已补齐 CI reuse、tagged `pip-audit` / `CodeQL`、`SBOM` / attestation / `cosign` / release identity manifest、verify-only / non-publish rehearsal 与 compatibility preview advisory lane 的同一故事。

### 修复（Fixed）

- 改进认证问题生命周期处理（repair 通知与 reauth 流程）。
- 修复匿名分享的崩溃路径，并提升刷新稳定性。
- 在 diagnostics/anonymous share 载荷中脱敏 `wifiSsid` 等敏感字段。
- 加固属性解析逻辑，防御畸形 API item。
- 恢复 `PROP_FAN_ONOFF` 导出，并修复 import 顺序问题。
- 修正亮度取整与人体传感器能力检测行为。
- 通过收紧依赖约束修复 aiodns/pycares 兼容性问题。
- 补齐灯光平台 icons，并修正 command/device-id 示例。
- 修复强制房间-区域同步：即使云端房间名不变，也能收敛用户在 HA 中手动修改的 area。
- 修复 stale-device 对账：使用未过滤的云端 serials 并在冷启动时以 registry 为基线，避免过滤器误删。
- 加固 bool-like coercion 的 debug 日志，避免记录原始异常值。
- 加固敏感信息脱敏：覆盖国际化手机号与数值型 `user_id`/`biz_id`，并在 UI 中遮罩 reauth phone 占位符。
- 减少状态兜底流程中冗余的全量 batch 重试，降低可重试批量失败时的重复 API 调用。
- `v1.21` archived evidence index 与 milestone audit 不再冒充当前 active-route / default-next truth，历史 closeout 语态已退回 archive-only 身份。

## [1.0.0] - 2026-02-08

### 新增（Added）

- Lipro Smart Home Home Assistant 集成首次发布。
- 云端 API 集成 + MQTT 实时推送更新。
- 支持的设备类型：
  - Light（灯光）：开关、亮度、色温
  - Cover（窗帘）：开/关、位置、停止
  - Switch（开关/插座）：开关
  - Fan（风扇）：开关、风速、预设模式
  - Climate（浴霸）：开关、预设模式
  - Binary Sensor（传感器）：人体、门窗、光照、电池
- 配置流程：手机号+密码认证。
- 选项流程：配置刷新间隔（10-300 秒）。
- 重新认证与重新配置流程。
- 乐观状态更新，提升 UI 响应速度。
- 滑块防抖，避免 API 过载。
- MQTT 指数退避重连。
- 为高级用户提供自定义服务 `lipro.send_command`。
- 中英文双语支持。
- 诊断支持与敏感数据脱敏。
