# Phase 87: Assurance hotspot decomposition and no-regrowth guards - Research

**Date:** 2026-03-27
**Status:** Final
**Confidence:** HIGH
**Suggested shape:** 4 plans / 2 waves

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- `HOT-38` / `TST-27` 只处理 audit 已点名的 3 个 assurance hotspots：`tests/core/api/test_api_diagnostics_service.py`、`tests/core/api/test_protocol_contract_matrix.py`、`tests/core/coordinator/runtime/test_mqtt_runtime.py`。
- 本 phase 只做 topicization / thin-root / focused guard strengthening；不重开生产代码残留，不偷带 `Phase 88` 的治理冻结工作。
- 拆分必须复用现有自然 home，不制造新的 giant umbrella test、隐藏入口或第二套长期 truth。
- 每个被切薄的 hotspot 都必须留下 machine-checkable no-regrowth proof；若触及 docs/reviews/baseline，只允许做与 suite topology 直接相关的最小同步。
- 是否保留原始路径为 thin shell、support helper 的具体抽取范围、focused guard 的最终组合，可由 planner 自主裁量，但必须遵守“最小扰动、最大定位收益”。

### Deferred / Out of Scope
- 不变更 protocol/runtime/control 正式根，不触碰 vendor payload normalization。
- 不引入新依赖、snapshot 框架或大规模 fixture 基础设施。
- 不把 routed hotspots 叙述成 future file-delete target；它们只允许经由 topicization / thin-root closeout。
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| `HOT-38` | assurance hotspots 停止承担 giant truth-carrier 职责，需要继续 topicization / thin-root 化。 | 3 个 routed hotspot 都已被审计、review ledger 与 file matrix 明确点名，且都存在仓内同类拆分样板可复用。 |
| `TST-27` | 每个被消灭或收窄的 hotspot 都必须补齐 focused regressions / meta guards / no-regrowth checks。 | `tests/meta/test_phase45_hotspot_budget_guards.py`、`tests/meta/test_phase70_governance_hotspot_guards.py`、`tests/meta/test_phase71_hotspot_route_guards.py`、`tests/meta/test_phase85_terminal_audit_route_guards.py` 已提供成熟 guard 模式。 |

</phase_requirements>

## Summary

`Phase 85` 的终局审计已经把 `Phase 87` 的问题定义得很窄：不是 coverage 不足，而是 3 个 assurance roots 承担了过多 concern family，导致 failure-localization 半径过大。`Phase 86` 已清空 production residual，因此 `Phase 87` 的最佳策略不是再碰生产代码，而是把 routed hotspots 沿既有 topical home 继续 inward topicize，并用 focused guard / review truth 把新 topology 冻结下来。

仓库已经给出可直接复用的成熟模式：
- API 侧已有 `thin shell + sibling topical suites`（`test_api_device_surface.py`、`test_api_transport_and_schedule.py`）；
- runtime 侧已有 `support helper + topical suites`（`test_command_runtime.py` + `test_command_runtime_support.py`）；
- meta 侧已有 `thin shell + focused guard families`（`test_public_surface_guards.py`、`test_dependency_guards.py`、`test_governance_followup_route.py`）。

**Primary recommendation:** 用 `3 个 hotspot closeout plans + 1 个 no-regrowth/truth sync 计划` 完成 `Phase 87`。Wave 1 并行拆分 3 个热点；Wave 2 统一补 focused guards、verification/file-matrix truth 与 targeted validation commands。

## Current State

| File | Lines | Current hotspot story | Recommended end-state |
|------|------:|-----------------------|-----------------------|
| `tests/core/api/test_api_diagnostics_service.py` | 622 | 混合 OTA row helpers、V1/V2 fallback、degraded outcome、user-cloud、sensor history、command result fixtures | 保留 stable shell 或 anchor，拆成 OTA/info、history+command-result、cloud/raw-body 等 topical suites；必要时抽 `*_support.py` |
| `tests/core/api/test_protocol_contract_matrix.py` | 627 | 同时承载 unified root smoke、MQTT facade telemetry、REST/MQTT boundary decoders、replay manifest authority、Phase-1 fixture reuse | 按 `boundary decoders`、`facade/runtime smoke`、`fixture authority/replay` 三大 concern family topicize；原路径可退为 thin shell |
| `tests/core/coordinator/runtime/test_mqtt_runtime.py` | 644 | 混合 constructor DI、connect/reconnect、message handling、disconnect notification、reset、backoff gate | 先抽同目录 support helper，再按 `init/DI`、`connection/reconnect`、`message handling`、`notification/reset` 切分为 runtime topical suites |

## Recommended Decomposition

### Hotspot 1 — Diagnostics API suite
- **Natural home:** 继续位于 `tests/core/api/`
- **Preferred split:**
  - `test_api_diagnostics_service_ota.py`
  - `test_api_diagnostics_service_history.py`
  - `test_api_diagnostics_service_cloud.py`
  - 可选 `test_api_diagnostics_service_support.py`
- **Reasoning:** concern family 已天然分离，且都围绕 `diagnostics_api_service`；无需新目录。
- **Do not do:** 再造更大的 umbrella suite，或把 external-boundary authority 复制第二份。

### Hotspot 2 — Protocol contract matrix
- **Natural home:** 继续位于 `tests/core/api/`
- **Preferred split:**
  - `test_protocol_contract_boundary_decoders.py`
  - `test_protocol_contract_facade_runtime.py`
  - `test_protocol_contract_fixture_authority.py`
  - 原 `test_protocol_contract_matrix.py` 可保留为 thin shell / anchor
- **Reasoning:** current file 的核心问题是跨 boundary families 过载，而不是缺 helper；拆分后 failure 可直接指向 decoder/facade/authority。
- **Do not do:** 将 north-star protocol truth 扩散到多个不受控 helper 根，或打破现有 fixture authority anchors。

### Hotspot 3 — MQTT runtime suite
- **Natural home:** `tests/core/coordinator/runtime/`
- **Preferred split:**
  - `test_mqtt_runtime_connection.py`
  - `test_mqtt_runtime_messages.py`
  - `test_mqtt_runtime_notifications.py`
  - `test_mqtt_runtime_init.py`
  - `test_mqtt_runtime_support.py`
  - 原 `test_mqtt_runtime.py` 可保留为 thin shell / anchor
- **Reasoning:** 该文件的依赖注入模式已很统一，最适合复用 `test_command_runtime_support.py` 的 support-only pattern。
- **Do not do:** 新建额外 runtime tree，或把 support helper 放到仓外公共 util 形成第二真源。

## Reusable Patterns

### Thin-shell patterns
- `tests/core/api/test_api_device_surface.py`
- `tests/core/api/test_api_transport_and_schedule.py`
- `tests/core/coordinator/runtime/test_command_runtime.py`
- `tests/core/test_share_client.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_dependency_guards.py`

### Support-helper patterns
- `tests/core/coordinator/runtime/test_command_runtime_support.py`
- `tests/core/test_share_client_support.py`
- `tests/core/api/conftest.py`

### Focused no-regrowth guard patterns
- `tests/meta/test_phase45_hotspot_budget_guards.py`
- `tests/meta/test_phase70_governance_hotspot_guards.py`
- `tests/meta/test_phase71_hotspot_route_guards.py`
- `tests/meta/test_phase72_runtime_bootstrap_route_guards.py`
- `tests/meta/test_phase85_terminal_audit_route_guards.py`

## Risks and Pitfalls

1. **Over-splitting without real localization gain**
   - Risk: 生成太多碎片文件，增加跳转成本。
   - Mitigation: 以 concern family 为单位，而不是每个测试函数一个文件。

2. **Thin shell regrows into second giant root**
   - Risk: 保留原路径后，又把大量断言塞回 shell。
   - Mitigation: shell 只做 import aggregation 或极少数 anchor smoke；bulk tests 必须落在 sibling topical files。

3. **Fixture authority drift**
   - Risk: protocol/diagnostics fixture truth 被复制或重新包装，破坏 north-star authority。
   - Mitigation: 复用现有 fixture loaders 与 authority paths，不复制基准数据。

4. **Guard gap after topicization**
   - Risk: 文件拆完但 `FILE_MATRIX` / verification / hotspot budget guards 未同步，后续回流无人知晓。
   - Mitigation: 将 focused guard + truth sync 作为独立最后一 plan，而不是散落收尾。

5. **Cross-phase scope leak**
   - Risk: 顺手把 `Phase 88` 的 docs freeze 或 production cleanup 混进本 phase。
   - Mitigation: 仅同步与 suite topology / validation command 直接相关的基线与 review truth。

## Suggested Plan / Wave Shape

| Wave | Plan | Objective |
|------|------|-----------|
| 1 | `87-01` | topicize `test_api_diagnostics_service.py` into concern-local API diagnostics suites |
| 1 | `87-02` | topicize `test_protocol_contract_matrix.py` into boundary/facade/authority suites |
| 1 | `87-03` | topicize `test_mqtt_runtime.py` into runtime-facet suites with inward support helper |
| 2 | `87-04` | add focused no-regrowth guards and sync verification / file-matrix truth to new suite topology |

**Why this is optimal:** 3 个热点写集基本天然分离，适合并行；guard/truth sync 必须在 topology 稳定后集中执行，避免边拆边漂移。

## Validation Focus

- `uv run pytest -q tests/core/api/test_api_diagnostics_service*.py`
- `uv run pytest -q tests/core/api/test_protocol_contract*.py`
- `uv run pytest -q tests/core/coordinator/runtime/test_mqtt_runtime*.py`
- `uv run pytest -q tests/meta/test_phase85_terminal_audit_route_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py`
- `uv run python scripts/check_file_matrix.py --check`
- 若 verification matrix / route guards 有更新，再补：`uv run pytest -q tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py`

## Sources

### Primary (HIGH confidence)
- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/reviews/V1_23_TERMINAL_AUDIT.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/phases/87-assurance-hotspot-decomposition-and-no-regrowth-guards/87-CONTEXT.md`
- `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-RESEARCH.md`
- `.planning/phases/49-mega-test-topicization-and-failure-localization-hardening/49-{CONTEXT,RESEARCH}.md`
- `tests/core/api/test_api_diagnostics_service.py`
- `tests/core/api/test_protocol_contract_matrix.py`
- `tests/core/coordinator/runtime/test_mqtt_runtime.py`
- `tests/core/api/test_api_device_surface.py`
- `tests/core/api/test_api_transport_and_schedule.py`
- `tests/core/coordinator/runtime/test_command_runtime.py`
- `tests/core/coordinator/runtime/test_command_runtime_support.py`
- `tests/core/test_share_client.py`
- `tests/core/test_share_client_support.py`
- `tests/meta/test_phase45_hotspot_budget_guards.py`
- `tests/meta/test_phase70_governance_hotspot_guards.py`
- `tests/meta/test_phase71_hotspot_route_guards.py`
- `tests/meta/test_phase72_runtime_bootstrap_route_guards.py`
- `tests/meta/test_phase85_terminal_audit_route_guards.py`

### Secondary (MEDIUM confidence)
- `tests/core/api/conftest.py`
- `tests/meta/test_governance_followup_route.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_dependency_guards.py`

## Metadata

**Confidence breakdown:**
- Architecture / scope: **HIGH**
- Hotspot inventory: **HIGH**
- Reusable split patterns: **HIGH**
- Final file naming: **MEDIUM** — should stay planner-discretion within locked boundaries

**Research date:** 2026-03-27
**Valid until:** 2026-03-28
