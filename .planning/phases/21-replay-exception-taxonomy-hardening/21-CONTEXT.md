# Phase 21 Context

**Phase:** `21 Replay Coverage & Exception Taxonomy Hardening`
**Milestone:** `v1.2 Host-Neutral Core & Replay Completion`
**Date:** `2026-03-16`
**Status:** `Ready for planning`
**Source:** `Phase 20` closeout truth + current roadmap/requirements/state + Phase 21 code-reality audit

## Phase Boundary

`Phase 21` 只做三件事：

1. 把 `Phase 20` 已 formalize 的 `rest.list-envelope`、`rest.schedule-json`、`mqtt.topic`、`mqtt.message-envelope` 真正压进 replay / evidence assurance 主链。
2. 把 protocol / runtime / control 中最关键的 broad-catch 热点收窄，或明确保留为“有契约的 envelope catch”。
3. 把 failure taxonomy 收口成后续 `Phase 22` 可直接消费的正式输入，而不是继续散落为 raw exception type / helper-level log wording。

## Current Truth From Phase 20

- `Phase 20` 已确认 remaining families 完成 formal boundary registration、authority fixture、replay manifest 与 meta guard 同步；`Phase 21` **不再负责** boundary family formalization 本身。
- replay manifests 当前已经覆盖四个 `Phase 20` families，但 harness / evidence assertions 仍偏“全量 generic pass”，缺少对这四个 families 的显式 family-level coverage / evidence visibility 约束。
- telemetry / diagnostics / system health 当前仍以 `mqtt_last_error_type`、`mqtt_last_transport_error` 这类 raw type 字段为主；failure vocabulary 还没有形成稳定 taxonomy。
- broad-catch 现实并非“全部都错”：
  - **应优先收窄/分类**：`core/protocol/facade.py` 的 MQTT wrapper、`core/coordinator/runtime/mqtt_runtime.py`、`core/coordinator/mqtt_lifecycle.py`、`core/coordinator/coordinator.py` 的 update branch。
  - **可保留但必须立契约**：`control/entry_lifecycle_controller.py` 的 setup/unload abort envelope、`services/diagnostics/helpers.py` 的 per-entry best-effort collectors、`coordinator.async_shutdown()` 的 cleanup envelope。

## Locked Decisions

- 本 phase 不重开 boundary family story，不新增第二条 replay / evidence authority chain。
- `21-01` 只做 assurance coverage 与 evidence visibility；不要偷跑到 contributor docs / release closeout。
- `21-02` 不是“消灭所有 except Exception”，而是对热点做 **收窄 / 保留并文档化** 的明确裁决。
- `21-03` 的 taxonomy home 必须是 replay / telemetry / sink contract；`diagnostics_surface.py` 与 `system_health_surface.py` 继续保持 thin-adapter 身份。
- raw exception class / error code 可以作为 detail 保留，但**不能继续充当唯一分类语言**。
- 本 phase 的治理回写仅限被改变的 formal truth、phase closeout 与相应 guards；贡献者文档 / 模板 / release surface 对齐留给 `Phase 23`。

## Non-Negotiable Constraints

- 不得重开第二条正式主链、第二套 replay story、第二套 telemetry vocabulary。
- 不得让 helper / transport / diagnostics collector 自己长成 authority source。
- 所有 retained catch-all 必须满足：`CancelledError/KeyboardInterrupt/SystemExit` 直通、日志/遥测语义稳定、并有 focused regression 覆盖。
- 若执行中发现需要跨 phase 的 contributor-doc / release closeout 变更，必须 defer 到 `Phase 23`，而不是在 `Phase 21` 偷跑。

## Out Of Scope

- contributor-facing docs、Issue/PR 模板、release evidence gate 总收口（`Phase 23`）
- final repo audit / archive-ready bundle / v1.3 handoff（`Phase 24`）
- diagnostics / system health / support / developer-facing consumer 的全面对外暴露与词汇统一（`Phase 22`）

## Phase Exit Signals

- replay harness、replay summary、AI evidence pack 对四个 `Phase 20` families 都有显式 family-level coverage 断言。
- 关键 catch-all 热点完成“收窄或有契约保留”的明确处置，不再只有 generic warning / exception wording。
- replay / telemetry / system-health summary 至少共享一组稳定的 failure taxonomy 字段，可被 `Phase 22` 继续向 consumers 暴露。
