# 更新日志

本项目的重要变更都会记录在本文件中。

格式参考 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，并遵循
[语义化版本](https://semver.org/spec/v2.0.0.html)。

## [Unreleased]（未发布）

### 新增（Added）

- 为最新一轮架构与治理收口补齐了维护者侧的归档证据链，方便在不污染公开 first hop 的前提下追溯 closeout 结论。
- 补强了与当前 release / governance story 对应的 focused 守卫与文档一致性检查。

### 变更（Changed）

- 公开 release notes 现在只保留对外可读的发布故事；维护者侧的 archived baseline、审计证据与内部路线说明继续留在 maintainer-only 文档中。
- `CI reuse`、`CodeQL`、`SBOM`、`cosign`、`release identity` 与 `compatibility preview` 仍是一条统一的 release-security 叙事，不再混入过期 closeout 口径。
- 当前仓库的治理现状已统一收敛到最新 archived baseline，公开文档与维护者附录不再讲两套冲突故事。

### 修复（Fixed）

- 修复了 release notes、maintainer runbook 与治理基线之间的 latest archived pointer 漂移，移除了过期的 closeout-ready 叙事。
- 修复了 archived-only route 下的 bootstrap / closeout / release-contract 文案不一致问题，使公开发布说明与维护者侧证据引用各归其位。

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
