# Phase 107: REST/auth/status hotspot convergence and support-surface slimming - Context

**Gathered:** 2026-03-30
**Status:** Executed / governance projected
**Source:** `v1.30` activation from `.planning/MILESTONE-CONTEXT.md`

<domain>
## Phase Boundary

本 phase 只处理 `v1.30` 的第一段 hotspot convergence：

- 收窄 `custom_components/lipro/core/api/rest_facade.py` 的 explicit collaborator assembly。
- 收窄 `custom_components/lipro/core/api/status_fallback_support.py` 的 binary-split fallback orchestration。
- 收窄 `custom_components/lipro/core/api/request_policy_support.py` 的 pacing-cache / lock / trim state handling。
- 把上述变化投射回 planning/baseline/review/docs truth 与 focused guards，使 `Phase 107 complete` 成为 parser-stable current route。

不在本 phase 重开 MQTT transport-runtime、anonymous-share manager 或 runtime snapshot surgery；这些 scope 已显式路由到 `Phase 108 -> 110`。
</domain>

<decisions>
## Locked Decisions

- `rest_facade.py` 继续保持 `LiproRestFacade` formal child-façade 身份；本轮只收窄 init assembly / collaborator wiring，不扩 public surface。
- `status_fallback_support.py` 继续保持 support-only home；本轮允许增加 context/accumulator/helper 函数，但不让 fallback truth 再回流到 endpoint layer。
- `request_policy_support.py` 继续保持 pacing/backoff support seam；本轮目标是局部 state object 化，不把 pacing caches 重新讲成第二条 policy root。
- `Phase 107` 完成后，current route 应前推到 `v1.30 active route / Phase 107 complete / latest archived baseline = v1.29`，默认下一步是 `$gsd-discuss-phase 108`。
</decisions>

<canonical_refs>
## Canonical References

- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `custom_components/lipro/core/api/rest_facade.py`
- `custom_components/lipro/core/api/status_fallback_support.py`
- `custom_components/lipro/core/api/request_policy_support.py`
- `tests/core/api/test_api.py`
- `tests/core/api/test_api_status_service_fallback.py`
- `tests/core/api/test_api_request_policy.py`
</canonical_refs>
