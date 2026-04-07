# Phase 101: Anonymous-share manager and REST decoder hotspot decomposition freeze - Context

**Gathered:** 2026-03-28
**Status:** Ready for execution

<domain>
## Phase Boundary

`Phase 101` 承接 `Phase 100` 之后的终审热点：继续不重开新功能，只把 `anonymous_share` 与 REST protocol boundary 中仍然偏厚、或仍有 authority/residual drift 的正式 home / support seam 再做一轮 inward decomposition 与 truth cleanup，并同步把治理、focused guards、phase 资产与 GSD parser truth 推进到 `v1.27 active route / Phase 101 complete / latest archived baseline = v1.26`。
</domain>

<decisions>
## Implementation Decisions
- **D-01:** `custom_components/lipro/core/anonymous_share/manager.py` 继续保留 `AnonymousShareManager` 作为 formal anonymous-share aggregate/scoped manager home；允许收口 accessor re-export、aggregate outcome state、cache lifecycle 与 submit-flow duplication，但不得新增第二条 manager root。
- **D-02:** `custom_components/lipro/core/protocol/boundary/rest_decoder.py` / `rest_decoder_support.py` 继续保留 protocol-boundary decode authority；允许统一 offset / list-envelope truth、tighten property fallback、去掉重复 schedule parse，但不得把 vendor payload 重新泄漏到 runtime/domain。
- **D-03:** `custom_components/lipro/core/api/rest_facade.py` 本 phase 只允许做最小 truth cleanup（如 child-facing typed payload wording）；不把 canonical REST child façade composition home 重新拆散。
- **D-04:** `Phase 100` 现在是 `v1.27` 里的 completed predecessor evidence；current-route truth 必须前推到 `Phase 101 complete`，且 `$gsd-next` 在本 phase 收口后仍应自然落回 `$gsd-complete-milestone v1.27`。
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / governance
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 唯一终态架构裁决
- `.planning/PROJECT.md` — 当前里程碑目标与 active-route 真源
- `.planning/ROADMAP.md` — phase 编排与 closeout route
- `.planning/REQUIREMENTS.md` — requirement basket 与 traceability
- `.planning/STATE.md` — parser-facing live state truth
- `.planning/baseline/VERIFICATION_MATRIX.md` — focused/repo-wide proof chain 真源
- `.planning/reviews/FILE_MATRIX.md` — 文件归属与 hotspot note 真源

### Anonymous-share hotspot target
- `custom_components/lipro/core/anonymous_share/manager.py` — 待收口的 formal manager home
- `custom_components/lipro/core/anonymous_share/manager_submission.py` — submit-flow 协作面
- `custom_components/lipro/core/anonymous_share/manager_support.py` — scope-state / cache / report support seam
- `custom_components/lipro/core/anonymous_share/registry.py` — formal accessor home
- `tests/core/anonymous_share/test_manager_submission.py` — submit-flow focused regressions
- `tests/core/anonymous_share/test_manager_recording.py` — cache / scope / aggregate behavior coverage
- `tests/core/anonymous_share/test_observability.py` — root/scoped accessor routing coverage
- `tests/core/test_anonymous_share_cov_missing.py` — residual branch coverage

### Protocol boundary hotspot target
- `custom_components/lipro/core/protocol/boundary/rest_decoder.py` — formal REST boundary family home
- `custom_components/lipro/core/protocol/boundary/rest_decoder_support.py` — canonicalization helper truth
- `custom_components/lipro/core/api/mqtt_api_service.py` — MQTT config helper authority consumer
- `custom_components/lipro/core/api/rest_facade_endpoint_methods.py` — REST child-facing typed endpoint wording
- `tests/core/api/test_protocol_contract_boundary_decoders.py` — decoder family regression truth
- `tests/core/api/test_api_status_service_wrappers.py` — misc endpoint wrapper coverage

</canonical_refs>

<specifics>
## Specific Ideas
- `manager.py` 当前最值得收口的是 accessor re-export、aggregate submit outcome/client selection，以及 `_foo` / `foo` 双份薄包装。
- `manager_submission.py` 当前最值得收口的是 aggregate child traversal 重复与 disabled-scope no-op 语义。
- `rest_decoder_support.py` 当前最值得收口的是 top-level fallback property extraction、offset/hasMore truth 与 nested vendor shape leakage 风险。
- `rest_decoder.py` 当前只做 low-risk truth cleanup：schedule parse once、endpoint metadata 更可追踪；`rest_facade.py` 只做 wording cleanup，不做结构级拆分。
</specifics>

<deferred>
## Deferred Ideas
- `custom_components/lipro/core/api/rest_facade.py` deeper façade slimming
- `custom_components/lipro/entities/firmware_update.py`
- maintainer / delegate continuity docs

以上仍是非阻塞热点，但本 phase 不同时推进，避免让 `v1.27` 再扩散成高风险 mega-phase。
</deferred>

---

*Phase: 101-anonymous-share-manager-and-rest-decoder-hotspot-decomposition-freeze*
*Context gathered: 2026-03-28*
