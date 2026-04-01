# 更新日志

本项目的重要变更都会记录在本文件中。

格式参考 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，并遵循
[语义化版本](https://semver.org/spec/v2.0.0.html)。

## [Unreleased]（未发布）

### 新增（Added）

- `v1.34` 归档证据资产：`.planning/v1.34-MILESTONE-AUDIT.md`、`.planning/reviews/V1_34_EVIDENCE_INDEX.md`、`.planning/milestones/v1.34-ROADMAP.md` 与 `.planning/milestones/v1.34-REQUIREMENTS.md`，把 latest archived baseline 固化为 pull-only closeout bundle。
- `Phase 120` / `Phase 121` promoted evidence：terminal audit contract hardening、residual contract closure、flow invariant tightening 与 surface hygiene cleanup 的 summary / verification 资产已纳入长期治理引用链。

### 变更（Changed）

- governance current story 现统一收敛为 `no active milestone route / latest archived baseline = v1.34`；默认下一步改为 `$gsd-new-milestone`，不再把 `v1.34` 误讲成 active milestone 或 closeout-ready continuation。
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、selector-family planning docs 与最新 evidence pointer 已全部对齐 `V1_34_EVIDENCE_INDEX.md` / `v1.34-MILESTONE-AUDIT.md` 的 archived-only truth。
- release notes 继续保留 `CI reuse`、`CodeQL`、`SBOM`、`cosign`、`release identity` 与 `compatibility preview` 的单一 release-security 叙事，不再混入过期的 `v1.33` closeout-ready 口径。

### 修复（Fixed）

- 修复 baseline / runbook / changelog 之间的 latest archived pointer 漂移：不再引用 `.planning/reviews/V1_33_EVIDENCE_INDEX.md`、`.planning/v1.33-MILESTONE-AUDIT.md` 或 `$gsd-complete-milestone v1.34`。
- 修复 archived-only route 下的 bootstrap / closeout / release-contract 守卫断言，使 machine-readable route contract、maintainer appendix 与 release story 只承认 `v1.34` 作为 latest archived baseline。

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
