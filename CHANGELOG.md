# 更新日志

本项目的重要变更都会记录在本文件中。

格式参考 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，并遵循
[语义化版本](https://semver.org/spec/v2.0.0.html)。

## [Unreleased]（未发布）

### 变更（Changed）

- `entry_auth.py`、`flow/step_handlers.py` 与 `config_flow.py` 现共同收敛为 Phase 124 的 auth-seed / config-flow thin-adapter 正式主链。
- `services/contracts.py -> services/schedule.py` 现在承担 schedule direct-call normalization / result typing shared contract truth，并补齐 translated invalid-request fail-fast 行为。
- `.planning` 基线、审计账本、codebase maps、`docs/developer_architecture.md` 与 Phase 124 evidence chain 已同步切到 closeout-ready 叙事。
- `control/service_router_handlers.py` 重新收拢 command / schedule / share / maintenance 回调，减少四个过薄 handler shell 带来的导航与维护成本。
- `CI reuse`、`CodeQL`、`SBOM`、`cosign`、`release identity` 与 `compatibility preview` 仍保持同一条 release-security 叙事，只是不再夹带过期 archived-only 路线口径。
- `docs/developer_architecture.md`、`.planning/codebase/ARCHITECTURE.md` 与相关治理账本已同步到当前 control-plane topology，不再保留过期的 split-family 现状描述。
- 公开 release notes 继续只保留对外可理解的变更故事，不再夹带过期的 archived-only route 叙述。

### 修复（Fixed）

- 修复了 persisted auth-seed、config-flow orchestration 与 schedule direct-call contract 分别散落在多个 helper / handler 中的真源漂移。
- 修复了 Phase 124 route truth、testing inventory、translation tree 与 closeout evidence 之间的治理不同步。
- 修复了 service-router family 与 file-matrix / meta guards / architecture archive 之间的 topology 漂移。
- 修复了 developer architecture 当前路线说明仍停留在 `v1.34 archived-only baseline` 的陈旧文案。

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
