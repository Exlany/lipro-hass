# 更新日志

本项目的重要变更都会记录在本文件中。

格式参考 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，并遵循
[语义化版本](https://semver.org/spec/v2.0.0.html)。

## [Unreleased]（未发布）

### 变更（Changed）

- 优化了 REST / protocol 内部边界的可维护性，减少超大 façade 文件里的重复样板与隐式中转。
- 完善了设备定时相关调用链的一致性，补齐 mesh / standard schedule 之间的参数透传行为。
- 同步收紧了开发者架构文档、维护者发布手册与治理基线之间的当前路线说明，降低后续维护时的定位成本。
- 持续压缩内部实现热点，保持对外导入入口与正式根对象不变。

### 修复（Fixed）

- 修复了 schedule `group_id` 在部分 REST/protocol forwarding 链路中的透传缺口。
- 修复了当前治理/验证文档仍引用过期路线状态与旧测试路径的若干漂移项。
- 修复了维护者发布语义与 private-access / mirror reachability 条件之间的不一致表述。

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
