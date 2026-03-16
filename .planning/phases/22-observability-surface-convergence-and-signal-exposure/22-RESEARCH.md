# Phase 22 Research

**Status:** `research complete`
**Date:** `2026-03-16`
**Mode:** `forced re-research via $gsd-plan-phase 22 --research`

## Executive Judgment

`Phase 22` 的真实工作不是“再加更多 telemetry 字段”，而是把 `Phase 21` 已冻结的 failure taxonomy 统一投影给 observability consumers。当前最大的缺口是 **consumer vocabulary / field-shape drift**：不同 surface 使用不同字段名、不同层级与不同失败摘要方式，导致 `OBS-03` 仍未达成。

最优拆分仍然是 `3 plans / 3 waves`：

- `22-01`：先统一 diagnostics / system health 的 signal 语言
- `22-02`：再统一 developer / support / report-building consumers 的 signal 消费方式
- `22-03`：最后冻结 observability contract、治理回写与 fail-fast guards

## Code Reality Audit

### 1. diagnostics / system health 已接入 telemetry exporter，但仍不讲同一种语言

现状：

- `custom_components/lipro/control/diagnostics_surface.py` 会把完整 exporter diagnostics view 放入 `payload["telemetry"]`，同时另有一套 `coordinator` 摘要字段：
  - `last_update_success`
  - `update_interval`
  - `device_count`
  - `mqtt_connected`
- `custom_components/lipro/control/system_health_surface.py` 则完全绕开这些 diagnostics payload，只输出：
  - `can_reach_server`
  - `logged_accounts`
  - `total_devices`
  - `mqtt_connected_entries`

缺口：

- diagnostics payload 里是 nested telemetry truth；system health 是 coarse summary truth；两者没有共享的 normalized failure summary。
- `runtime_access.build_runtime_snapshot()` 当前只吸收 `device_count / last_update_success / mqtt_connected`，并未把 failure taxonomy summary 一起上抬。

**裁决：** `22-01` 必须让 diagnostics / system health 从“各有一套字段”变成“共享同一 observability summary vocabulary”。

### 2. telemetry sinks 本身仍有 field-shape drift

当前 exporter sinks 使用的语言并不完全对齐：

- diagnostics sink：保留 full nested snapshot
- system_health sink：扁平字段，例如 `protocol_mqtt_last_error_type`、`mqtt_last_transport_error`
- developer sink：保留 nested protocol/runtime + session flags
- ci sink：只保留 summary metrics，几乎不含 failure-language fields
- replay summary：仍使用 `error_category`

缺口：

- 相同语义在不同 sink 中被命名成不同 key / shape。
- replay summary、telemetry sink views、diagnostics/system_health surfaces 还没有讲同一套 normalized failure words。

**裁决：** `22-03` 不能只测“字段存在”，必须锁定 contract mapping 与命名稳定性。

### 3. developer / support consumers 仍通过不同路径消费失败信息

现状：

- `custom_components/lipro/services/diagnostics/helpers.py::collect_developer_reports()` 在 legacy builder 缺失时，会回退到 `telemetry_surface.get_entry_telemetry_view(entry, "developer")`。
- `build_developer_feedback_payload()` 直接把这些 reports 打进 developer feedback payload。
- `custom_components/lipro/services/diagnostics/handlers.py::_build_last_error_payload()` 仍是 capability / API-error 风格的局部错误结构。
- `custom_components/lipro/core/anonymous_share/report_builder.py` 会对 developer feedback 做脱敏 / lite projection，但本身并不知道 normalized failure taxonomy。

缺口：

- developer report 与 capability last-error payload 可能继续讲不同语言。
- support / developer payload 会继承上游 drift，而不是强制使用同一 signal vocabulary。

**裁决：** `22-02` 应集中治理 `developer report + diagnostics service payload + developer feedback upload` 这条线，而不是泛化到所有 share/report 功能。

### 4. evidence / integration consumers 需要作为 contract sinks 一起锁定

- `tests/integration/test_ai_debug_evidence_pack.py` 与 `tests/integration/test_telemetry_exporter_integration.py` 已经是非常好的 consumer truth。
- 它们目前更多在检查 exporter / evidence 是否可用，而不是验证 consumer vocabulary 是否统一。

**裁决：** `22-03` 要把它们升级成“consumer convergence guards”，而不只是 exporter smoke tests。

## Recommended Plan Structure

### Wave 1 — Plan 22-01

#### Plan 22-01 — diagnostics / system health signal convergence

**目标：** 让 control-plane adapters 对 failure taxonomy 暴露同一 structured summary，而不是 diagnostics 靠 nested telemetry、system health 靠 bespoke aggregates。

**建议文件域：**
- `custom_components/lipro/control/diagnostics_surface.py`
- `custom_components/lipro/control/system_health_surface.py`
- `custom_components/lipro/control/runtime_access.py`
- `tests/core/test_diagnostics.py`
- `tests/core/test_system_health.py`
- `tests/core/test_control_plane.py`
- `tests/integration/test_telemetry_exporter_integration.py`
- `tests/core/telemetry/test_sinks.py`

### Wave 2 — Plan 22-02

#### Plan 22-02 — developer / support / report consumer convergence

**目标：** 统一 developer report、diagnostics service payload、developer feedback payload 对 failure signals 的消费方式。

**建议文件域：**
- `custom_components/lipro/services/diagnostics/helpers.py`
- `custom_components/lipro/services/diagnostics/handlers.py`
- `custom_components/lipro/control/developer_router_support.py`
- `custom_components/lipro/core/anonymous_share/report_builder.py`
- `tests/core/test_developer_report.py`
- `tests/core/test_report_builder.py`
- `tests/services/test_services_diagnostics.py`
- `tests/services/test_services_share.py`

### Wave 3 — Plan 22-03

#### Plan 22-03 — observability contract freeze + governance / integration guards

**目标：** 把 consumer convergence 写成可执行 contract，并回写最小治理真源，明确 `Phase 23` 才负责 docs/templates/release gate。

**建议文件域：**
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_dependency_guards.py`
- `tests/integration/test_ai_debug_evidence_pack.py`
- `tests/integration/test_telemetry_exporter_integration.py`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`

## Governance / Verification Assets That Must Be Considered

若本 phase 新增或冻结了新的 consumer contract，则必须同步：

- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`

只有在 consumer convergence 改动实际改变 public surface / authority / dependency policy 时，才扩写：

- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/AUTHORITY_MATRIX.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`

## Recommended Verification Slices

### Plan 22-01

- `uv run pytest -q tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_control_plane.py tests/integration/test_telemetry_exporter_integration.py tests/core/telemetry/test_sinks.py`

### Plan 22-02

- `uv run pytest -q tests/core/test_developer_report.py tests/core/test_report_builder.py tests/services/test_services_diagnostics.py tests/services/test_services_share.py`

### Plan 22-03

- `uv run pytest -q tests/integration/test_ai_debug_evidence_pack.py tests/integration/test_telemetry_exporter_integration.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py`
- `uv run mypy`

## Work Explicitly Deferred To Phase 23

以下内容不能在 `Phase 22` 偷跑：

- README / README_zh / CONTRIBUTING / SUPPORT / SECURITY / issue template / PR template 改写
- `.github/workflows/ci.yml` / `.github/workflows/release.yml` / release runbook 改写
- v1.2 release evidence index / milestone audit / archive-ready bundle
- 开源协作面文案统一与 release gate closeout

## Risks And Controls

### Risk 1 — 把 consumer convergence 误做成 taxonomy redefinition

- **症状：** 在 diagnostics/service layer 自造第二套 category 名称。
- **控制：** 所有 normalized fields 只能来自 `Phase 21` formal truth；consumer 只能 pull / project。

### Risk 2 — system health 继续保留 bespoke summary 语言

- **症状：** diagnostics 与 system health 虽都“有失败字段”，但 key / meaning 不一致。
- **控制：** 由 `22-01` 锁定 shared summary vocabulary 与 integration regression。

### Risk 3 — developer/support payload 把 raw detail 当 normalized truth

- **症状：** developer feedback payload 继续只传播 raw `error_type` 或 ad-hoc `last_error`。
- **控制：** `22-02` 要采用 “normalized summary + raw detail” 分层。

### Risk 4 — 把 docs / release work 提前混入 22

- **症状：** 为了“统一语言”直接去改 README / runbook / workflows。
- **控制：** `22-03` 只回写 verification / file / residual truth；对外 docs 与 release gate 留给 `Phase 23`。
