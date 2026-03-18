# Phase 27 Research

**Status:** `research complete`
**Date:** `2026-03-17`
**Requirement:** `HOT-05`, `RES-04`, `TST-02`

## Executive Judgment

`Phase 27` 最该先切的不是再造 abstraction，而是**让已经存在的 formal service surface 真正成为唯一正式调用路径**，并把伴随它的测试/治理巨石同步切薄。

最优拆分是 `4 plans / 4 waves`：

1. `27-01`：把 `protocol_service` 提升为 runtime formal contract，并迁移 schedule / diagnostics / OTA consumers
2. `27-02`：删除 coordinator 顶层 pure protocol forwarders，收口内部自转发 wiring 与 phase residue
3. `27-03`：同步 hotspot / dependency / residual truth，冻结 no-return rules
4. `27-04`：拆分 `test_init.py` 与 `test_governance_guards.py` 中最重的专题块，并同步 TESTING/toolchain truth

## Current Defect Chain

### 1. Formal service exists, but external consumers still bypass it

`CoordinatorProtocolService` 已在 runtime 内成型，但 `services/schedule.py`、`services/diagnostics/handlers.py`、`entities/firmware_update.py` 仍依赖 coordinator 顶层 `async_*` pure forwarders。

### 2. Coordinator still carries a removable protocol-forwarder cluster

`Coordinator` 顶层仍保留 schedule / diagnostics / OTA / outlet-power 的一簇纯委派方法。这些方法让 runtime root 继续承担 protocol surface 噪声。

### 3. Runtime code still leaks historical phase narration

`Phase C - Aggressive Refactor`、`Phase H4` 之类注释仍混在正式 runtime docstring / comments 中，属于已完成迁移叙事未收口。

### 4. Test monoliths still over-aggregate unrelated concerns

- `tests/core/test_init.py` 把 setup/runtime/service-handler/schedule/diagnostics/anonymous-share 等主题压在一只 mega class 上。
- `tests/meta/test_governance_guards.py` 同时承载 repo-level docs truth、milestone closeout truth 与 phase-history truth，局部修改时需要加载过多上下文。

## Recommended Contract

### A. `protocol_service` becomes the only formal protocol-capability port exposed by runtime

- `runtime_types.LiproCoordinator` 必须显式暴露 `protocol_service`。
- schedule / diagnostics / OTA consumers 只 pull `coordinator.protocol_service.async_*`。
- coordinator 顶层 pure forwarders 一旦无生产调用者，即可删除。

### B. Runtime root stays runtime-only

- entity-facing runtime helpers 保留在 coordinator formal surface；protocol capabilities 不再混入同一层。
- outlet-power polling 这类 coordinator 内部 wiring 也应直接使用 `self.protocol_service`，而非自转发回 coordinator 顶层。

### C. Test split must preserve truth density

- `test_init.py` 优先分裂 service-handler / diagnostics / schedule 主题。
- `test_governance_guards.py` 优先分裂 milestone closeout / archive/handoff 主题。
- 所有新增测试文件必须同步 `TESTING.md` 的文件数与 minimal suite guidance。

## Recommended Plan Structure

### Plan 27-01 — formalize protocol-service runtime contract and migrate external consumers

**File focus:**
- `custom_components/lipro/runtime_types.py`
- `custom_components/lipro/services/schedule.py`
- `custom_components/lipro/services/diagnostics/handlers.py`
- `custom_components/lipro/entities/firmware_update.py`
- `tests/conftest.py`
- `tests/core/test_init.py`
- `tests/services/test_services_diagnostics.py`
- `tests/services/test_service_resilience.py`

### Plan 27-02 — remove coordinator protocol forwarders and phase-residue comments

**File focus:**
- `custom_components/lipro/core/coordinator/coordinator.py`
- `tests/test_coordinator_public.py`
- `tests/core/test_coordinator.py`
- `tests/core/test_init.py`

### Plan 27-03 — sync hotspot/dependency/residual governance truth

**File focus:**
- `.planning/codebase/STRUCTURE.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`

### Plan 27-04 — split service/governance monolith tests and refresh testing map truth

**File focus:**
- `tests/core/test_init.py`
- `tests/core/test_init_service_handlers.py`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_governance_closeout_guards.py`
- `.planning/codebase/TESTING.md`
- `tests/meta/test_toolchain_truth.py`

## Validation Architecture

### Targeted regression slices

- `uv run pytest -q tests/core/test_init.py tests/core/test_init_service_handlers.py tests/services/test_services_diagnostics.py tests/services/test_service_resilience.py tests/test_coordinator_public.py`
- `uv run pytest -q tests/core/test_coordinator.py tests/integration/test_telemetry_exporter_integration.py tests/core/test_system_health.py`
- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py`
- `uv run ruff check custom_components/lipro/runtime_types.py custom_components/lipro/services/schedule.py custom_components/lipro/services/diagnostics/handlers.py custom_components/lipro/entities/firmware_update.py custom_components/lipro/core/coordinator/coordinator.py tests/core/test_init.py tests/core/test_init_service_handlers.py tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py`

### High-risk scenarios that must be locked

- service handlers no longer read removed `Coordinator.async_*` forwarders
- fake coordinators missing `protocol_service` fail loudly in tests rather than silently passing
- coordinator outlet-power polling no longer self-calls deleted forwarder
- split tests keep total file inventory、minimal suite guidance 与 governance gates 一致
