# Phase 130: runtime command and firmware update hotspot decomposition - 背景

**Gathered:** 2026-04-01
**Status:** 规划就绪
**Source:** v1.37 active milestone route + Phase 129 完成移交

<domain>
## 阶段边界

本阶段承接 `ARC-41, HOT-60, TST-51`，只处理 `custom_components/lipro/core/coordinator/runtime/command_runtime.py` 与 `custom_components/lipro/entities/firmware_update.py` 两个 hotspot，以及它们紧邻的 support / OTA / focused tests / governance proof 收口。目标是继续把 runtime command 与 firmware update 的多主题逻辑 inward split 回更窄的 helper/policy seams，而不是扩展功能、改写 outward contract，或提前把工作扩散成 repo-wide final audit；后者明确留给 `Phase 131`。

</domain>

<decisions>
## 实施决策

### Locked Decisions
- `CommandRuntime` 仍是唯一正式的 command runtime orchestration home，不得再长出第二条 runtime story。
- `LiproFirmwareUpdateEntity` 仍是 entity/update outward shell，不得把 orchestration 反向拉回 entity 之外的错误位置，也不得直连 concrete coordinator internals。
- 允许继续 inward split 到邻近的 support / policy / helper seams，但不得引入新的 public surface、compat shell 或 delete folklore。
- outward behavior 保持不变，必须依靠 focused/full tests 把现状固定住。
- repo-wide terminal audit final report、governance continuity closeout、external private-fallback honesty 明确延后到 `Phase 131`，本阶段不得伪装为已完成。

### the agent's Discretion
- `command_runtime.py` 是否把 dispatch outcome / verification / telemetry bookkeeping 继续下沉到现有或新增的 localized helper。
- `firmware_update.py` 是否把 install flow / OTA refresh pipeline / background task bookkeeping 继续下沉到邻近的 support / OTA seams。
- focused tests 的增补粒度与命名，只要仍保持 suites focused、可审阅且不回长成 megatest。

</decisions>

<canonical_refs>
## 权威参考

**下游代理在规划或实现前必须先读完这些文件。**

### 治理与架构
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 北极星裁决标准
- `.planning/PROJECT.md` — v1.37 active milestone route 与 phase handoff 真源
- `.planning/ROADMAP.md` — `Phase 129 -> 131` 的路线、目标与下一步 truth
- `.planning/REQUIREMENTS.md` — `ARC-41, HOT-60, TST-51` 的 requirement 映射
- `.planning/codebase/CONCERNS.md` — 当前 hotspot 排名与债务说明
- `AGENTS.md` — 仓级约束、formal home 与 route honesty 规则

### Runtime Command Hotspots
- `custom_components/lipro/core/coordinator/runtime/command_runtime.py` — command runtime orchestration 正式 home
- `custom_components/lipro/core/coordinator/runtime/command_runtime_support.py` — runtime support seam
- `custom_components/lipro/core/coordinator/runtime/command_runtime_outcome_support.py` — outcome / bookkeeping 邻近 helper

### Firmware Update 与 OTA Hotspots
- `custom_components/lipro/entities/firmware_update.py` — firmware update entity outward shell
- `custom_components/lipro/entities/firmware_update_support.py` — entity 邻近 support seam
- `custom_components/lipro/core/ota/candidate.py` — OTA candidate truth
- `custom_components/lipro/core/ota/row_selector.py` — OTA row arbitration 规则
- `custom_components/lipro/core/ota/rows_cache.py` — OTA rows cache / refresh 邻近逻辑

### Focused Runtime Tests
- `tests/core/coordinator/runtime/test_command_runtime_orchestration.py` — orchestration 主链回归
- `tests/core/coordinator/runtime/test_command_runtime_sender.py` — sender 行为与 dispatch 路径覆盖
- `tests/core/coordinator/runtime/test_command_runtime_confirmation.py` — confirmation / verification 行为冻结
- `tests/core/coordinator/runtime/test_command_runtime_builder_retry.py` — builder / retry 路径覆盖
- `tests/core/coordinator/runtime/test_command_runtime_outcome_support.py` — outcome helper focused coverage
- `tests/core/coordinator/runtime/test_runtime_telemetry_methods.py` — telemetry bookkeeping focused coverage

### Focused Firmware Update / OTA Tests
- `tests/platforms/test_update_install_flow.py` — install flow 回归
- `tests/platforms/test_update_background_tasks.py` — background task 生命周期覆盖
- `tests/platforms/test_update_task_callback.py` — task callback 行为冻结
- `tests/platforms/test_update_entity_refresh.py` — refresh pipeline focused coverage
- `tests/platforms/test_update_certification_policy.py` — certification / policy coverage
- `tests/platforms/test_firmware_update_entity_edges.py` — entity edge cases 与 outward shell 边界
- `tests/core/ota/test_ota_candidate.py` — OTA candidate truth coverage
- `tests/core/ota/test_ota_rows_cache.py` — OTA rows cache focused coverage
- `tests/core/ota/test_ota_row_selector.py` — OTA row selector arbitration coverage

### Meta Guards
- `tests/meta/test_phase95_hotspot_decomposition_guards.py` — hotspot decomposition guard 基线
- `tests/meta/test_phase99_runtime_hotspot_support_guards.py` — runtime hotspot support no-regrowth guards
- `tests/meta/test_phase111_runtime_boundary_guards.py` — runtime / entity boundary guards
- `tests/meta/test_phase113_hotspot_assurance_guards.py` — hotspot assurance no-regrowth guards
- `tests/meta/test_phase71_hotspot_route_guards.py` — route / hotspot continuity meta guards

</canonical_refs>

<specifics>
## 具体关注点

- 优先把 `command_runtime.py` 的 dispatch / verify / trace bookkeeping seams 变窄。
- 优先把 `firmware_update.py` 的 install flow、refresh task lifecycle、OTA row arbitration projection 变窄。
- 测试优先复用现有 focused suites，不新增 megatest。

</specifics>

<deferred>
## 延后事项

- `Phase 131` 的 repo-wide audit closeout。
- developer / open-source docs final current story。
- external continuity / private fallback governance decisions。

</deferred>

---

*阶段：130-runtime-command-and-firmware-update-hotspot-decomposition*
*背景收集：2026-04-01，基于 v1.37 active milestone route / Phase 129 完成移交*
