# Phase 36 Context

**Phase:** `36 Runtime root and exception burn-down`
**Milestone:** `v1.4 seed — Sustainment, Trust Gates & Final Hotspot Burn-down`
**Date:** `2026-03-18`
**Status:** `planned — context captured, ready for execution planning`
**Source:** `.planning/{ROADMAP,REQUIREMENTS,STATE,PROJECT}.md` + coordinator/runtime audit + Phase 31 typed-budget guards + current runtime/control tests

## Why Phase 36 Exists

`Phase 35` 解决 protocol hotspot 后，最大的生产热点将回到 runtime root：`Coordinator` 仍吸附若干 orchestration helper，且 runtime/device/MQTT 主链上仍存在多处宽异常。

这些 catch-all 并非全部错误；但若缺少 typed arbitration 或 documented degraded contract，它们就会成为 correctness / observability 的灰区。`Phase 36` 的任务不是发明第二个 runtime root，而是沿现有 seams 把 root 继续收薄，并把高风险宽异常压缩到 machine-guarded 阈值。

## Goal

1. 继续收薄 `Coordinator`，把 runtime/service orchestration helper 下沉到既有 home。
2. 优先 burn-down runtime 主链宽异常，形成 typed arbitration、guarded degraded contract 或 fail-closed path。
3. 刷新 runtime/service/platform touched-zone 的 typed budget 与 no-growth evidence。

## Decisions (Locked)

- `Coordinator` 仍是唯一正式 runtime root；不得新增第二 manager/root。
- 先做 `36-01` root slimming，再做 `36-02` exception burn-down，最后做 `36-03` budget/governance 收口。
- 已冻结 named lifecycle contract 的 `control/entry_lifecycle_controller.py` 仅作为后置 touched zone，不在本 phase 作为主战场。
- 只读 `devices` / power / protocol public surface 的现有语义不能在抽取过程中回退。
- broad-catch burn-down 优先打 runtime 主链热点，而不是一次性清全仓所有 `except Exception`。

## Non-Negotiable Constraints

- 不得绕开现有 orchestrator / runtime / service seams。
- 不得把异常处理改成吞错沉默；所有收口都要有命名语义或 fail-closed 行为。
- 不得新增第二套 typed budget / exception policy story；必须复用既有 guards。
- 不得为了拆根而破坏 `Coordinator` 的 public API 与 HA wiring。

## Canonical References

### Governance / Route Truth
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/PROJECT.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`

### Runtime Root / Hotspots
- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/core/coordinator/orchestrator.py`
- `custom_components/lipro/core/coordinator/runtime_context.py`
- `custom_components/lipro/core/coordinator/services/device_refresh_service.py`
- `custom_components/lipro/core/coordinator/services/mqtt_service.py`
- `custom_components/lipro/core/coordinator/services/telemetry_service.py`
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py`
- `custom_components/lipro/core/coordinator/runtime/device_runtime.py`
- `custom_components/lipro/core/coordinator/mqtt_lifecycle.py`
- `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py`

### Guard / Regression Truth
- `tests/core/test_coordinator.py`
- `tests/core/test_init_runtime_behavior.py`
- `tests/core/test_system_health.py`
- `tests/integration/test_mqtt_coordinator_integration.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_phase31_runtime_budget_guards.py`

### Baseline / Residual Truth
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`

## Expected Scope

### In scope
- coordinator orchestration helper extraction along existing seams
- runtime/device/MQTT broad-catch burn-down on the mainline
- typed-budget / no-growth truth refresh

### Out of scope
- protocol hotspot slimming
- giant test topicization
- release / continuity productization
- global repository-wide exception cleanup

## Open Planning Questions

1. 哪一组 coordinator helper 最适合先下沉：snapshot refresh、status polling 还是 MQTT lifecycle？
2. 哪些 broad-catch 需要 typed exception，哪些更适合 degraded contract？
3. Phase 31 runtime budget guards 需要新增哪些 truth，而不是重写另一套？
4. 哪些 runtime tests 最能证明收口没有改变 public behavior？

---

*Phase directory: `36-runtime-root-and-exception-burn-down`*
*Context gathered: 2026-03-18 from runtime hotspot audit and Phase 31 guard truth.*
