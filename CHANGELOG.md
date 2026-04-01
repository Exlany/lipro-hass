# 更新日志

本项目的重要变更都会记录在本文件中。

格式参考 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，并遵循
[语义化版本](https://semver.org/spec/v2.0.0.html)。

## [Unreleased]（未发布）

### 新增（Added）

- `Phase 119` closeout 资产：`119-01/02/03-SUMMARY.md`、`119-SUMMARY.md` 与 `119-VERIFICATION.md`，为 MQTT boundary 解环、runtime contract 真源统一与 release/governance 收口提供 machine-checkable handoff。
- `119-RESEARCH.md`，把当前 residual bundle 的根因、正式裁决与执行分层沉淀为 phase-local research artifact。

### 变更（Changed）

- MQTT topic/payload decode authority 已统一回 `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py`，`core/mqtt` helpers 仅单向消费 boundary truth，不再保留 reverse import / lazy-import folklore。
- `runtime_types.py` 现为 runtime/service 合同的唯一正式真源；`services/execution.py`、`services/command.py` 与 `control/entry_lifecycle_support.py` 已去除平行 Protocol / concrete typing 漂移。
- release / governance current story 现只承认 semver public release namespace 与 canonical route contract；`release.yml` / `codeql.yml`、`docs/developer_architecture.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md` 与 live planning docs 已对齐 `v1.33` closeout-ready truth。
- release notes 继续保留 `CI reuse`、`CodeQL`、`SBOM`、`cosign`、`release identity` 与 `compatibility preview` 的单一 release-security 叙事，但已移除过时的内部 milestone / stale archive-pointer folklore。

### 修复（Fixed）

- 修复 governance current-truth helper 的硬编码 archived-route 漂移：current route 现直接读取 `.planning/PROJECT.md` machine-readable contract，而不再维护第二份 Python dict。
- 修复 route-handoff / follow-up milestone guards 对旧 `v1.32 archived` 叙事、旧 phase counters 与旧默认命令的耦合，当前只承认 `Phase 119 complete; closeout-ready` 的 live selector truth。
- 修复 maintainer-facing route note 与 changelog freshness 漂移：不再引用 `.planning/reviews/V1_29_EVIDENCE_INDEX.md`、`.planning/v1.29-MILESTONE-AUDIT.md` 或 `Phase 10 completed` 口径。

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
