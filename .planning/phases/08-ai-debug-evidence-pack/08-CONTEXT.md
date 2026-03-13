# Phase 8 Context

**Phase:** `8 AI Debug Evidence Pack`
**Milestone:** `v1.1 Protocol Fidelity & Operability (extension)`
**Date:** 2026-03-13
**Status:** Proposed

## Why Phase 8 Exists

`07.3` 让 telemetry truth 正式化，`07.4` 让 protocol 样本可回放，`07.5` 负责治理与验证收尾。
但“可给 AI 调试/分析”的目标需要一个明确交付物：把分散在 diagnostics、telemetry exporter、replay corpus、boundary inventory、governance matrices 的信息 **以统一 schema 打包导出**。

本 phase 的定位是：**Assurance/Tooling only**。

## Goal

1. 定义一套稳定的 `AI Debug Evidence Pack` schema（版本化、可扩展）；
2. 把 exporter snapshots/views、replay run summaries、boundary inventory 摘要、关键 governance pointers 统一导出为一个 evidence 包；
3. evidence 包满足：
   - 结构化（机器可读 JSON 为主，必要时附带 markdown index）；
   - 脱敏（凭证等价物永不出现）；
   - 可关联（报告内稳定的 `entry_ref/device_ref`）；
   - 可裁决（每个字段能追溯 authority/source）。

## Decisions (Locked)

- **脱敏方式**：允许使用伪装字符/伪匿名引用（报告内稳定、跨报告不可关联）。
- **时间戳允许**：evidence 包允许包含真实时间戳（用于定位与 AI 分析），但仍遵守隐私策略。
- **采集方式**：优先 pull（从正式 sources/exporter 读取），不引入第二条 truth chain。

## Non-Negotiable Constraints

- 不得把 evidence pack 变成新的 runtime root 或第二条 diagnostics 实现；
- 不得引入重型外部 observability stack；
- 产物必须能被 tests/meta guards 纳入治理（文件归属、public surface、authority）。

