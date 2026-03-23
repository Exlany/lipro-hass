# Phase 65 PRD: Runtime-access de-reflection and anonymous-share hotspot closure

**Date:** 2026-03-23
**Source:** Renewed repository-wide architect audit after `Phase 64`
**Mode:** PRD express path for `$gsd-plan-phase 65`

## Problem Statement

`v1.14 / Phase 64` 已关闭 telemetry、schedule、diagnostics 三个热点，但仓库仍存在三类值得工程化收口、且会继续增加长期维护成本的剩余问题：

1. `custom_components/lipro/control/runtime_access_support.py`
   - 仍通过 `inspect.getattr_static`、`object.__getattribute__(..., "__dict__")` 与 materialized-mock probing 来判定 runtime truth。
   - 这会把测试夹具历史反向写回正式 contract，抬高控制面的认知负荷。
2. runtime/device extras 残留
   - `custom_components/lipro/control/diagnostics_surface.py` 仍直接读取 `device.extra_data`。
   - `custom_components/lipro/core/coordinator/runtime/device/snapshot.py` 与 `custom_components/lipro/core/coordinator/runtime/state/index.py` 仍借 `extra_data["identity_aliases"]` 传递 runtime identity sidecar truth。
3. `custom_components/lipro/core/anonymous_share/{manager.py,manager_submission.py,share_client_flows.py}`
   - 仍有较重的跨文件状态代理、聚合/作用域提交耦合与 submit-flow hotspot。
   - outward home 正确，但 internal collaboration 仍偏厚。

## Goals

- 让 control-plane runtime access 通过显式 entry/coordinator projection 讲一条 truth，不再依赖 mock-aware reflection。
- 让 diagnostics/runtime identity 不再借 raw `extra_data` sidecar 讲第二条故事线。
- 让 anonymous-share manager / submit flows 继续 inward split，降低单文件复杂度与跨文件私有状态耦合。
- 保持 outward behavior、public import home、service semantics 与 release/governance contract 稳定。

## Non-Goals

- 不重开新的 broad audit。
- 不引入新依赖。
- 不改变 Home Assistant outward service/API behavior。
- 不重开 unrelated governance/publisher/custodian 人事问题。
- 不为一次性逻辑创建新的 public wrapper / compat shell / helper-owned second root。

## Requirement Mapping

- `HOT-20` — runtime access exits reflection-heavy runtime truth.
- `HOT-21` — anonymous-share hotspots continue inward decomposition.
- `TYP-18` — runtime/device/share residual raw sidecars and probing converge onto explicit local contracts.
- `TST-15` — focused regressions and fixture honesty prove no behavior drift.
- `GOV-49` — topology truth and current-story docs freeze the new ownership story.
- `QLT-23` — all quality gates pass together.

## Locked Decisions

- `custom_components/lipro/control/runtime_access.py` remains the formal outward home for control-plane runtime reads.
- `custom_components/lipro/control/runtime_access_support.py` may slim drastically or split inward, but no second outward runtime-access story may appear.
- `custom_components/lipro/control/diagnostics_surface.py` remains the diagnostics formal home.
- gateway / mesh / identity alias truth must prefer explicit typed properties or dedicated runtime-local projections over ad-hoc `device.extra_data` reads.
- `custom_components/lipro/core/anonymous_share/manager.py` remains the outward manager home; decomposition must stay inward.
- tests that currently force production code to recognize `MagicMock` ghosts should be migrated toward more honest fakes or explicit typed fixtures where that removes reflection pressure.

## Acceptance Criteria

### A. Runtime access
- `runtime_access_support.py` no longer uses `inspect.getattr_static`, `object.__getattribute__(..., "__dict__")`, or `_mock_children` probing as the primary runtime contract mechanism.
- control-plane runtime projections still reject partial/foreign entries and unloaded runtime data.
- system health, diagnostics, developer router, and control-plane tests keep their current outward behavior.

### B. Device extras / identity
- diagnostics device payloads no longer branch on raw `device.extra_data` for gateway visibility.
- runtime identity/index flow no longer relies on `extra_data["identity_aliases"]` as a sidecar transport.
- gateway/member/identity behavior stays stable in focused runtime and diagnostics tests.

### C. Anonymous share
- submit-flow and manager orchestration are split into narrower collaborators or state views without changing outward import homes.
- aggregate/scoped submit behavior, retry/backoff semantics, and typed outcomes remain stable.
- focused anonymous-share regression suites pass without compatibility drift.

### D. Governance / validation
- `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES / FILE_MATRIX` freeze the new topology truth.
- `uv run ruff check .`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- focused pytest suites + full `uv run pytest -q`

## Canonical References

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/phases/64-telemetry-typing-schedule-contracts-and-diagnostics-hotspot-slimming/64-SUMMARY.md`
- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/control/runtime_access_support.py`
- `custom_components/lipro/control/diagnostics_surface.py`
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py`
- `custom_components/lipro/core/coordinator/runtime/state/index.py`
- `custom_components/lipro/core/anonymous_share/manager.py`
- `custom_components/lipro/core/anonymous_share/manager_submission.py`
- `custom_components/lipro/core/anonymous_share/share_client_flows.py`
