# Phase 64: Telemetry typing, schedule contracts, and diagnostics hotspot slimming - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning
**Source:** Renewed repository-wide architect review after Phase 63

<domain>
## Phase Boundary

本 phase 只处理三类仍然高杠杆、但已被审阅证据明确指出的正式热点：

1. `custom_components/lipro/core/telemetry/*`
   - formal truth 已存在，但 `models.py` / `ports.py` / `exporter.py` / `sinks.py` 仍由 `Any`-centric payload/view contracts 主导。
2. `custom_components/lipro/services/schedule.py`
   - service outward behavior 正确，但 service layer 仍保留 mixed tuple contract、`Any`、`getattr()` 式 mesh-context probing。
3. `custom_components/lipro/core/api/diagnostics_api_service.py`
   - outward home 正确，但 OTA fallback、sensor history 与 misc diagnostics query 仍混在同一厚模块里。

禁止事项：
- 不新增 public root / compat shell / second truth。
- 不改变对外 service/API 行为语义。
- 不把 helper/support 命名继续扩散成第二故事线。
</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- `custom_components/lipro/core/api/diagnostics_api_service.py` 必须继续保留 outward import home；允许 inward split 到 concern-local modules，但不改变现有 public import path。
- `custom_components/lipro/services/schedule.py` 必须继续保留 service outward home；允许抽出 typed contract / row normalization / mesh-context helpers，但 service handler registration 与 outward response shape 不得漂移。
- `custom_components/lipro/core/telemetry/*` 是 assurance-plane 正式 truth；必须优先使用 JSON-safe typed aliases / stable mapping contracts，而不是继续让 `Any` 成为 formal source/sink contract。
- 文档与治理真相必须同轮同步：至少更新 `ROADMAP` / `REQUIREMENTS` / `STATE` / `PROJECT` / `MILESTONES` 与 `FILE_MATRIX`。
- focused tests 必须与 hotspot decomposition 同轮落地；不要只做文件搬移。

### Claude's Discretion
- telemetry typing 具体采用 alias / protocol / dataclass / TypedDict 的哪种组合，由实现时择优，但必须保持现有依赖面最小。
- diagnostics API inward split 的粒度可按 OTA / history / misc query concern 仲裁，但不要为一次性逻辑过度抽象。
- schedule contract 是否采用本地 `Protocol`、typed alias 或小型 helper module，可按最小 fan-out 原则决定。
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / governance truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 单一主链、边界纯度、formal-home 约束
- `.planning/PROJECT.md` — 当前 milestone 叙事与 next step
- `.planning/ROADMAP.md` — `v1.14` active route 与 `Phase 64` 目标
- `.planning/REQUIREMENTS.md` — `ARC-11`, `HOT-18`, `HOT-19`, `TYP-17`, `TST-14`, `GOV-48`, `QLT-22`
- `.planning/STATE.md` — 当前执行位置与 closeout history
- `.planning/MILESTONES.md` — active milestone route truth
- `.planning/reviews/FILE_MATRIX.md` — 文件归属与 ownership wording

### Recent closeout evidence
- `.planning/phases/63-governance-truth-realignment-typed-runtime-access-and-hidden-root-closure/63-SUMMARY.md` — Phase 63 已关闭的 seams，避免回流
- `.planning/phases/61-formal-home-slimming-for-large-but-correct-production-modules/61-SUMMARY.md` — large-but-correct production homes slimming precedent
- `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-SUMMARY.md` — refreshed audit verdict 与 remediation routing baseline
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-SUMMARY.md` — repo-wide strengths / risks baseline

### Target hotspots
- `custom_components/lipro/core/api/diagnostics_api_service.py` — thick mixed-concern outward home
- `custom_components/lipro/services/schedule.py` — schedule service contract + mesh-context hotspot
- `custom_components/lipro/core/telemetry/models.py` — current formal telemetry contracts with `Any`-heavy internals
- `custom_components/lipro/core/telemetry/ports.py` — source/sink contracts currently exposing `Mapping[str, Any]`
- `custom_components/lipro/core/telemetry/exporter.py` — exporter-owned sanitation / view build path
- `custom_components/lipro/core/telemetry/sinks.py` — sink projections still centered on `dict[str, Any]`

### Focused regressions
- `tests/core/api/test_api_diagnostics_service.py`
- `tests/services/test_services_schedule.py`
- `tests/core/telemetry/test_models.py`
- `tests/core/telemetry/test_exporter.py`
- `tests/core/telemetry/test_sinks.py`
- `tests/services/test_services_diagnostics.py`
</canonical_refs>

<specifics>
## Specific Ideas

- telemetry 方向：让 exporter/ports/sinks 至少共享 `JsonObject` / `JsonValue` or equally honest typed view contracts，不再把 `Any` 作为 formal return type。
- schedule 方向：把 `GetDeviceAndCoordinator` 的 `tuple[Any, Any]` 与 `_normalize_schedule_time_events()` 的 `Mapping[str, Any]` 收口到 typed aliases / protocols；`get_mesh_context()` 不应继续依赖 broad `getattr()` 作为主逻辑。
- diagnostics API 方向：保留 `diagnostics_api_service.py` outward home，但把 OTA fallback / sensor history / misc query helpers inward split，缩小认知半径并保持 tests focused。

### Audit Evidence
- `custom_components/lipro/core/api/diagnostics_api_service.py` 约 497 LOC
- `custom_components/lipro/services/schedule.py` 约 345 LOC，并含 `Any` / mixed tuple contract
- `custom_components/lipro/core/telemetry/models.py` 约 421 LOC，`exporter.py` / `sinks.py` / `ports.py` 仍有 formal `Any` usage
</specifics>

<deferred>
## Deferred Ideas

- single-maintainer continuity / co-maintainer制度化：继续属于开源治理层长期课题，不在本 phase 处理。
- `scripts/check_file_matrix_registry.py` 进一步压缩：已在 previous phase 收口一轮，本 phase 不再重开 tooling hotspot。
- 更大范围的 mega-test topicization：只做 touched focused regressions，不重新打开另一轮全仓 test surgery。
</deferred>

---

*Phase: 64-telemetry-typing-schedule-contracts-and-diagnostics-hotspot-slimming*
*Context gathered: 2026-03-23 via renewed architect review*
