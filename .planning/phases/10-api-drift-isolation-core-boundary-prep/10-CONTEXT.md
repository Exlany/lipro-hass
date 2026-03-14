# Phase 10 Context

**Phase:** `10 API Drift Isolation & Core Boundary Prep`
**Milestone:** `v1.1 Protocol Fidelity & Operability (boundary hardening extension)`
**Date:** 2026-03-14
**Status:** Ready for planning
**Source:** architecture review + user direction

## Why Phase 10 Exists

`Phase 9` 已完成 residual surface closure，但最近的架构审查再次暴露一个更靠根因的问题：

- 逆向 API 变化的真实冲击面仍主要集中在 `core/api`、`core/protocol`、`core/coordinator` 与若干 control adapter；
- runtime/domain 仍能看到部分 vendor payload shape（如 `data` / `hasMore` / `iotId` / `deviceId` / `properties` 等形态）；
- `config_flow` / `entry_auth` 等 HA adapter 仍直接吃 protocol login/result shape；
- `core` 逻辑上承担宿主无关的 protocol/domain 职责，但物理上仍混有 `Coordinator` 等 HA runtime 叙事。

契约者的核心诉求不是“立刻把整个 `core` 抽成跨平台 SDK”，而是：

1. API 大范围变化时，不要迫使 HA 功能代码做大范围改写；
2. 未来若要做 CLI / 其他平台，应建立在正式 boundary / contract 之上；
3. 一切方案必须继续服从 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` 与 `.planning/*` 的单一主链裁决。

## Goal

1. 继续把高漂移 REST/MQTT 输入封死在 protocol boundary 内，减少 raw vendor shape 上浮；
2. 提炼 host-neutral auth / session / query-result contracts，让 HA control adapter 只吃 formal result/use case；
3. 继续收窄 `core` formal public surface 与 HA runtime root 的叙事边界，为未来多宿主复用保留“可抽离的 nucleus”，但不在本 phase 内引入 second root 或 physical shared SDK；
4. 把这些要求同步写进 roadmap / requirements / context / research / validation / verification / governance 文档，而不是只停留在口头约定。

## Decisions (Locked)

- **北极星优先**：`docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md` 与 `.planning/STATE.md` 继续是裁决真源。
- **先收口边界，再谈物理抽离**：本 phase 只做 API drift isolation 与 core-boundary prep，不把跨平台 SDK / second root 变成本期正式目标。
- **protocol boundary 必须独占 canonicalization**：runtime/domain/control/platform 不再自己兼容 vendor envelope、分页字段、alias 字段或 raw payload 包装层。
- **HA adapter 只吃 formal contract**：`config_flow`、`entry_auth`、control surfaces 只依赖 formal auth/result contract 或显式 use case，不直接吃 protocol login/result dict 形态。
- **文档与守卫同相位更新**：roadmap、requirements、context、research、validation、verification、governance、replay fixtures 与 meta guards 必须同轮同步。

## Non-Negotiable Constraints

- 不得引入第二条 protocol/runtime/control 正式主链；
- 不得把“未来 CLI / 其他平台”当理由提前抽离整块 shared SDK；
- 不得让 raw vendor payload 继续穿透 protocol boundary 进入 runtime/domain/control；
- 不得破坏 `Phase 7.3-9` 已锁定的 telemetry/replay/governance/evidence truth chain；
- 不得只修改代码而不补 phase docs / governance 文档。

## Specific Concerns To Address

- `login`、`device list`、`device status`、`mesh group status`、OTA/support payload 哪些仍未完成 canonical contract 收口；
- `config_flow`、`entry_auth`、control/telemetry/runtime access 哪些地方仍直接依赖 protocol/runtime concrete shape；
- `core/__init__.py`、`coordinator_entry.py`、`runtime_types.py`、control adapters 的正式边界还能如何继续收窄；
- 哪些 replay / contract / meta guards 需要补充，才能在 API 漂移时优先打到 boundary，而不是打穿 HA adapter。

## Deferred Ideas

- 物理抽离 shared `core` package；
- 正式 CLI / 其他宿主实现；
- 第二套 protocol/runtime implementation；
- 与本 phase 无直接关系的全局技术换栈。

---

*Phase: 10-api-drift-isolation-core-boundary-prep*
*Context gathered: 2026-03-14 via architecture review + user direction*
