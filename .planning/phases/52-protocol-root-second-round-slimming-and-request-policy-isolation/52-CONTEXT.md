# Phase 52: Protocol-root second-round slimming and request-policy isolation - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning
**Source:** `v1.8` milestone route + `Phase 35/50/51` closeout evidence + targeted protocol/request-policy reread

<domain>
## Phase Boundary

本 phase 只处理 `ARC-08`：继续 inward decomposition `LiproProtocolFacade` 与 request-policy collaborator family，目标是降低 protocol root 与 request-policy family 的 decision density，同时保持以下真相完全不漂移：

1. `LiproProtocolFacade` 仍是唯一正式 protocol-plane root；
2. `LiproRestFacade` / `LiproMqttFacade` 仍只是 child façade，而不是第二根；
3. request pacing / retry / `429` / busy / auth-retry 语义仍属于 protocol plane formal truth，而不是 helper folklore；
4. public surface、dependency direction、contract suites 与 governance wording 必须继续讲同一条 single protocol-root story。

本 phase 的重点不是“再造 façade”，而是把仍然堆在 protocol root 与 request-policy family 上的 forwarding / glue / policy decision 继续 inward topicize 到更窄、更诚实的 localized collaborator seams。

本 phase 不处理 runtime / entry-root throttling（`Phase 53`）、anonymous-share / diagnostics helper hotspot（`Phase 54`）、second-wave mega-test topicization 与 typing sustainment（`Phase 55`）。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- `LiproProtocolFacade` 必须继续保留唯一 protocol-plane root 身份；不得新增 façade、wrapper、package export 或第二条 protocol mainline。
- `LiproRestFacade` 仍是 canonical REST child façade；允许继续 inward 拆薄其协作者与端口，但不得改写对外 import story。
- request-policy truth 必须继续留在 protocol plane formal home；不得把 pacing / retry / busy / `429` / auth-retry 重新散落到 request helper、endpoint helper 或上层 runtime/control。
- `build_mqtt_facade()`、`attach_mqtt_facade()`、`protocol_diagnostics_snapshot()` 与 shared session / telemetry / diagnostics context 仍属于 protocol root 真职责，不做表面拆散。
- 本 phase 允许保留必要 thin delegates 以维持 formal surface 稳定，但复杂实现必须继续 inward 下沉，不能只是 rename / relocate。
- 若 public surface、dependency direction、formal-home wording 或 residual disposition 发生变化，必须同步回写 baseline / review truth 与对应 meta guards，而不是只写 phase 文档。

### Claude's Discretion
- protocol root 的 forwarding clusters 应按 topic surface、capability seam 还是更窄的 rest dispatch helper 下沉；只要不形成新 root 即可。
- request-policy isolation 应优先落在 `request_policy.py`、`transport_executor.py`、`request_gateway.py`、`rest_facade_request_methods.py` 之间的哪一层；只要 formal truth 更集中、边界更清楚即可。
- contract/test hardening 应采用 focused protocol/API regression、phase-specific guard，还是扩充现有 public-surface / dependency guards；只要能 machine-check protocol-root truth 即可。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Route / North-star Truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/reviews/V1_8_MILESTONE_SEED.md`

### Prior Phase Evidence
- `.planning/phases/35-protocol-hotspot-final-slimming/35-CONTEXT.md`
- `.planning/phases/35-protocol-hotspot-final-slimming/35-SUMMARY.md`
- `.planning/phases/35-protocol-hotspot-final-slimming/35-VERIFICATION.md`
- `.planning/phases/50-rest-typed-surface-reduction-and-command-result-ownership-convergence/50-RESEARCH.md`
- `.planning/phases/50-rest-typed-surface-reduction-and-command-result-ownership-convergence/50-VALIDATION.md`
- `.planning/phases/50-rest-typed-surface-reduction-and-command-result-ownership-convergence/50-SUMMARY.md`
- `.planning/phases/51-continuity-automation-governance-registry-projection-and-release-rehearsal-hardening/51-SUMMARY.md`
- `.planning/phases/51-continuity-automation-governance-registry-projection-and-release-rehearsal-hardening/51-VERIFICATION.md`

### Protocol / Request-policy Hotspots
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/protocol/rest_port.py`
- `custom_components/lipro/core/protocol/mqtt_facade.py`
- `custom_components/lipro/core/api/rest_facade.py`
- `custom_components/lipro/core/api/rest_facade_request_methods.py`
- `custom_components/lipro/core/api/request_gateway.py`
- `custom_components/lipro/core/api/request_policy.py`
- `custom_components/lipro/core/api/transport_executor.py`
- `custom_components/lipro/core/api/transport_retry.py`
- `custom_components/lipro/core/api/endpoints/commands.py`
- `custom_components/lipro/core/api/command_api_service.py`

### Baseline / Guard Truth
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `tests/core/api/test_protocol_contract_matrix.py`
- `tests/core/api/test_api_transport_and_schedule.py`
- `tests/core/api/test_api_command_surface.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_dependency_guards.py`

</canonical_refs>

<specifics>
## Specific Ideas

- 把 `LiproProtocolFacade` 中仍然冗长的 REST forwarding tail 继续按 protocol concern inward topicize，使 root 更接近“shared truth + child wiring + diagnostics/MQTT lifecycle owner”；
- 把 request-policy family 中跨 `request_policy.py` / `request_gateway.py` / `transport_executor.py` / `rest_facade_request_methods.py` 的 pacing / retry / busy / mapping-finalization 决策重新聚焦到更少、更清晰的 formal home；
- 若需要新增 collaborator，也必须是 localized collaborator / support seam，而不是新的 public façade / wrapper；
- 用 targeted protocol/API regressions 与 public-surface/dependency guards 锁定：root identity 不漂移、request-policy truth 不上浮、child façades / localized collaborators 不被误提升为第二 root。

</specifics>

<deferred>
## Deferred Ideas

- `Phase 53`: runtime / entry-root second-round throttling。
- `Phase 54`: anonymous-share / diagnostics API helper family slimming。
- `Phase 55`: mega-test topicization round 2 + typing sustainment。
- broad repo-wide naming/style cleanup、非 protocol-plane helper sweep、或不直接服务 `ARC-08` 的文档治理工作。

</deferred>

---

*Phase: 52-protocol-root-second-round-slimming-and-request-policy-isolation*
*Context gathered: 2026-03-21 from v1.8 route + Phase 35/50/51 evidence + protocol/request-policy reread*
