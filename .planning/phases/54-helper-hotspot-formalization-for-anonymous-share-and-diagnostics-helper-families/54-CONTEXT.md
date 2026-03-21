# Phase 54: Helper-hotspot formalization for anonymous-share and diagnostics helper families - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning
**Source:** `v1.8` roadmap route + `Phase 45/52` closeout evidence + targeted helper hotspot reread

<domain>
## Phase Boundary

本 phase 只处理 `HOT-13`：继续收窄 `custom_components/lipro/core/anonymous_share/manager.py`、`custom_components/lipro/core/anonymous_share/share_client.py`、`custom_components/lipro/services/diagnostics/helpers.py` 与 `custom_components/lipro/core/api/request_policy.py` 的 helper-owned decision density，让 helper families 更像 support/formal-home，而不是隐性第二故事线。

本 phase 必须保持以下真相不漂移：

1. `AnonymousShareManager` 仍是 anonymous-share aggregate/view 的 formal entry home，但不应继续独占 scope-state、cache、submit gating、report assembly 与 feedback bridge 全部机械细节；
2. `ShareWorkerClient` 仍是 share worker transport home，但 token lifecycle、attempt planning、HTTP outcome mapping 与 lite fallback 不得继续无边界混居；
3. `services/diagnostics/helpers.py` 仍只是 control helper family，不得长成 public handler home，`control/service_router.py` 仍是 public callback home；
4. `RequestPolicy` 仍是 `429` / busy / pacing 的 formal truth，request-policy companions 只能进一步 inward decomposition，不能重新吸回 request owner / helper folklore；
5. privacy shaping、developer feedback payload 与 upload projector 继续与 local debug report / control glue 分层，不得回流成第二 diagnostics story。

本 phase 不处理 runtime/entry-root throttling（`Phase 53`），也不处理 mega-test topicization 与 repo-wide typing stratification（`Phase 55`）。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- `AnonymousShareManager` 允许引入 support-only seams 承接 scope state、cache、submit gating、aggregate report assembly 与 developer-feedback bridge，但 manager 仍保留 current public behavior；不得引入第二 share manager / public wrapper。
- `ShareWorkerClient` 的 submit / refresh / outcome matrix 可继续 inward decomposition，但 worker payload contract、typed outcome story 与 external behavior 必须保持稳定。
- `services/diagnostics/helpers.py` 只允许 topicize 成更窄 helper families；public service handler 仍归 `control/service_router.py` / diagnostics surfaces，不得因 helper slimming 重新定义 public callback home。
- `RequestPolicy` 继续是 protocol-plane pacing / busy / rate-limit truth；若 generic backoff residual 被处理，必须显式更新 `RESIDUAL_LEDGER.md`，不得隐性扩大 helper-owned truth。
- 若新增 support-only files，必须同步 baseline / review truth 与 focused/meta tests，明确它们是 internal/helper seam，而不是新 root。

### Claude's Discretion
- manager 先收 scope-state/cache 还是 submit/report assembly，可按测试耦合最低的路径执行；
- share client 可按 token refresh、attempt planner、HTTP outcome mapping、lite fallback/backoff clock 分层；只要 typed outcome 更清晰即可；
- diagnostics helper family 可拆为 report collection、feedback payload builder、optional capability executor、service-call response shaping 等主题；
- request-policy companion closure 最终是迁移 generic backoff leak，还是继续显式登记 deferred residual，可按最小风险裁定，但必须 machine-checkable。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / current truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`

### Prior phase anchors
- `.planning/phases/45-hotspot-decomposition-and-typed-failure-semantics/45-SUMMARY.md`
- `.planning/phases/45-hotspot-decomposition-and-typed-failure-semantics/45-VERIFICATION.md`
- `.planning/phases/52-protocol-root-second-round-slimming-and-request-policy-isolation/52-SUMMARY.md`
- `.planning/phases/52-protocol-root-second-round-slimming-and-request-policy-isolation/52-VERIFICATION.md`

### Helper hotspot files
- `custom_components/lipro/core/anonymous_share/manager.py`
- `custom_components/lipro/core/anonymous_share/share_client.py`
- `custom_components/lipro/core/anonymous_share/report_builder.py`
- `custom_components/lipro/core/anonymous_share/registry.py`
- `custom_components/lipro/services/diagnostics/helpers.py`
- `custom_components/lipro/control/service_router.py`
- `custom_components/lipro/core/api/request_policy.py`

### Focused verify anchors
- `tests/core/anonymous_share/test_manager_recording.py`
- `tests/core/anonymous_share/test_manager_submission.py`
- `tests/core/anonymous_share/test_observability.py`
- `tests/core/test_anonymous_share_storage.py`
- `tests/core/test_share_client.py`
- `tests/services/test_services_diagnostics.py`
- `tests/services/test_services_share.py`
- `tests/core/test_init_service_handlers_share_reports.py`
- `tests/core/api/test_api_request_policy.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_dependency_guards.py`
- `tests/meta/test_phase31_runtime_budget_guards.py`
- `tests/meta/test_phase45_hotspot_budget_guards.py`
- `tests/meta/test_phase50_rest_typed_budget_guards.py`

</canonical_refs>

<specifics>
## Specific Ideas

- `AnonymousShareManager` 当前天然可按 scope-state/cache、submit gating、aggregate report build、developer feedback submit bridge 四簇切薄；manager 继续保留 aggregate/scoped public story。
- `ShareWorkerClient` 适合按 token lifecycle、submit attempt matrix、HTTP status → typed outcome、lite fallback/backoff clock 四簇下沉。
- diagnostics helper family 适合按 report collection、feedback payload builder、optional capability executor、service response shaping 拆开；但 public handler 仍在 control plane。
- `RequestPolicy` 当前可继续区分 pure helper math、mutable pacing cache 与 policy-owned async decisions；若 generic backoff helper 仍跨 family 泄漏，必须显式仲裁其归宿或 residual status。

</specifics>

<deferred>
## Deferred Ideas

- `Phase 55`: API/MQTT/platform mega-test topicization round 2 与 repo-wide typing metric stratification。
- broader privacy/reporting architecture rewrite、share worker protocol redesign、或 diagnostics public API 扩张。
- any new public façade、new manager hierarchy、or helper-driven second root story。

</deferred>

---

*Phase: 54-helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families*
*Context gathered: 2026-03-21 from v1.8 route + Phase 45/52 evidence + helper hotspot reread*
