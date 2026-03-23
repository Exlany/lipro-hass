# Phase 65: Runtime-access de-reflection and anonymous-share hotspot closure - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning
**Source:** PRD Express Path (`.planning/phases/65-runtime-access-de-reflection-and-anonymous-share-hotspot-closure/65-PRD.md`)

<domain>
## Phase Boundary

本 phase 只处理三类剩余高杠杆 residual：

1. control-plane `runtime_access` 仍被 MagicMock-aware reflection 绑架；
2. diagnostics/runtime identity 仍借 raw `extra_data` / alias sidecar 传递局部 truth；
3. anonymous-share manager / submit flows 仍存在较厚 orchestration hotspot。

禁止事项：
- 不新增 public root / compat shell / second runtime story。
- 不改变 outward service/API behavior。
- 不把测试特判继续写回生产 contract。
</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- `runtime_access.py` 保持 outward home；任何 slimming 只能 inward。
- diagnostics surface 保持 outward home；gateway/identity 只允许走更诚实的 typed projection。
- `AnonymousShareManager` 保持 outward home；decomposition 只能 inward。
- 允许调整测试夹具与 focused suites，以换取生产代码去反射化。
- docs / file matrix / current-story truth 必须与代码同轮同步。

### Claude's Discretion
- runtime-access 去反射化可以使用轻量 fake/fixture、显式 adapter function、narrow protocol 或 dedicated local view，但不允许重新长出 helper-owned second story。
- runtime identity / extras formalization 可以使用 dedicated runtime-local projection、device property、或更窄 local helper；以最小 fan-out 为准。
- anonymous-share inward split 的粒度可按 token refresh / submit attempt / scoped-vs-aggregate orchestration 切分，但不允许 public import path 漂移。
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / governance truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 单一主链、formal-home、control/runtime boundary
- `.planning/PROJECT.md` — current milestone story
- `.planning/ROADMAP.md` — `Phase 65` goal / success criteria
- `.planning/REQUIREMENTS.md` — `HOT-20`, `HOT-21`, `TYP-18`, `TST-15`, `GOV-49`, `QLT-23`
- `.planning/STATE.md` — current execution position
- `.planning/MILESTONES.md` — active milestone route truth
- `.planning/reviews/FILE_MATRIX.md` — ownership and wording truth

### Recent closeout evidence
- `.planning/phases/64-telemetry-typing-schedule-contracts-and-diagnostics-hotspot-slimming/64-SUMMARY.md`
- `.planning/phases/63-governance-truth-realignment-typed-runtime-access-and-hidden-root-closure/63-SUMMARY.md`
- `.planning/phases/61-formal-home-slimming-for-large-but-correct-production-modules/61-SUMMARY.md`
- `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-SUMMARY.md`

### Target hotspots
- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/control/runtime_access_support.py`
- `custom_components/lipro/control/runtime_access_types.py`
- `custom_components/lipro/control/diagnostics_surface.py`
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py`
- `custom_components/lipro/core/coordinator/runtime/state/index.py`
- `custom_components/lipro/core/device/extras_features.py`
- `custom_components/lipro/core/anonymous_share/manager.py`
- `custom_components/lipro/core/anonymous_share/manager_submission.py`
- `custom_components/lipro/core/anonymous_share/share_client_flows.py`

### Focused regressions
- `tests/core/test_control_plane.py`
- `tests/core/test_system_health.py`
- `tests/core/test_diagnostics.py`
- `tests/core/test_diagnostics_config_entry.py`
- `tests/core/coordinator/runtime/test_device_runtime.py`
- `tests/core/coordinator/runtime/test_state_runtime.py`
- `tests/core/test_share_client.py`
- `tests/core/anonymous_share/test_manager_submission.py`
- `tests/services/test_services_share.py`
</canonical_refs>

<specifics>
## Specific Ideas

- runtime access：把 entry/coordinator/materialized runtime projection 的真相收口为显式 adapter + honest fixture，不再让 mock internals 决定生产行为。
- device extras / identity：让 diagnostics/gateway redaction 与 identity index rebuild 使用 dedicated projection 或 explicit device fields，而不是 raw sidecar 读写。
- anonymous-share：继续把 submit attempt、token refresh、aggregate/scoped orchestration 切成更清晰 collaborator；减少 manager 代理属性与大函数半径。
</specifics>

<deferred>
## Deferred Ideas

- maintainer/delegate/bus-factor 制度问题仍属长期治理课题，不在本 phase 解决。
- `options_flow.py` 等 UI/config Any 使用，若仅服务于 voluptuous schema/HA adapter 且不定义 formal business truth，则暂不纳入本轮。
- 与当前 residual 无关的 mega-test topicization 或进一步 docs polish，不在本 phase 扩张。
</deferred>

---

*Phase: 65-runtime-access-de-reflection-and-anonymous-share-hotspot-closure*
*Context gathered: 2026-03-23 via PRD Express Path*
