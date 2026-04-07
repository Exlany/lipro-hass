# Phase 31 Research

**Status:** `research complete`
**Date:** `2026-03-17`
**Requirement:** `TYP-07`, `ERR-05`, `GOV-23`

## Executive Judgment

`Phase 31` 最优是 `4 plans / 4 waves`，而不是 `3`。原因是 runtime lifecycle broad-catch、device/state payload typing、service/platform tails、GOV-23 no-growth guards 这四簇的风险模型不同；若硬压成三波，极易再次形成 catch-all cleanup 巨相。

## Current Distributed Backlog Snapshot

### 1. runtime lifecycle / transport broad-catch 是 P0

- `Coordinator`、`mqtt_runtime`、`mqtt_lifecycle` 持有约半数 broad-catch，直接挂在 runtime root / transport setup-shutdown 主链。
- 负分支测试目前还偏弱，最值得优先做 `ERR-05`。

### 2. runtime device/state payload typing 是最适合量化下降的 `Any` 簇

- `device/filter.py`、`state/updater.py`、`device/snapshot.py`、`device_runtime.py` 这批 `Any` 多数是真 payload/backlog，不是 HA 签名噪声。
- 这部分更适合做明确 typed budget 和阶段性下降。

### 3. service/platform/entity tails 应单独成波

- `services/diagnostics/helpers.py`、`services/maintenance.py`、`entities/firmware_update.py` 等处仍有“先吞后记”的 broad-catch / loose typing。
- 少量平台 `Any` 可顺带清理，但不应把 HA-required `**kwargs: Any` 当成主胜利目标。

### 4. GOV-23 应最后定版

- budget truth 要双层：机器真源记录 scope/family/counts/allowlist；人工真源回写 planning docs 与 phase closeout。
- daily guard 只卡生产代码；测试预算应单列 informational，不与生产 budget 混算。

## Recommended Plan Structure

### Plan 31-01 — runtime lifecycle / transport exception closure

**File focus:**
- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py`
- `custom_components/lipro/core/coordinator/mqtt_lifecycle.py`
- `tests/core/test_coordinator.py`
- `tests/core/coordinator/runtime/test_mqtt_runtime.py`

### Plan 31-02 — runtime device/state typed narrowing

**File focus:**
- `custom_components/lipro/core/coordinator/runtime/device/filter.py`
- `custom_components/lipro/core/coordinator/runtime/state/updater.py`
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py`
- `custom_components/lipro/core/coordinator/runtime/device_runtime.py`
- `tests/core/coordinator/runtime/test_device_runtime.py`
- `tests/core/test_device_refresh.py`

### Plan 31-03 — service/platform/entity targeted closure

**File focus:**
- `custom_components/lipro/services/diagnostics/helpers.py`
- `custom_components/lipro/services/maintenance.py`
- `custom_components/lipro/entities/firmware_update.py`
- `custom_components/lipro/select.py`
- `custom_components/lipro/sensor.py`
- `tests/services/test_services_diagnostics.py`
- `tests/services/test_maintenance.py`
- `tests/platforms/test_update.py`
- `tests/platforms/test_select.py`
- `tests/platforms/test_sensor.py`

### Plan 31-04 — institutionalize budgets, no-growth guards, and closeout truth

**File focus:**
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_governance_closeout_guards.py`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/baseline/AUTHORITY_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/v1.3-HANDOFF.md`

## Validation Architecture

- `uv run pytest -q tests/core/test_coordinator.py tests/core/coordinator/runtime/test_mqtt_runtime.py`
- `uv run pytest -q tests/core/coordinator/runtime/test_device_runtime.py tests/core/test_device_refresh.py`
- `uv run pytest -q tests/services/test_services_diagnostics.py tests/services/test_maintenance.py tests/platforms/test_update.py tests/platforms/test_select.py tests/platforms/test_sensor.py`
- `uv run mypy custom_components/lipro/core/coordinator custom_components/lipro/services custom_components/lipro/entities custom_components/lipro/select.py custom_components/lipro/sensor.py`
- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_toolchain_truth.py`

## High-Risk Truths To Lock

- runtime broad-catch closure 不能把 degrade/fail-closed semantics 偷偷改回 silent continue。
- budget truth 必须区分 `sanctioned_any`、`backlog_any` 与 touched-zone `type: ignore` no-growth；不能把 HA-required signatures 当作 cleanup 成果。
- final no-growth contract 必须同时落到 meta guards、baseline truth 与 closeout assets，不能只停在 phase 局部文档。
