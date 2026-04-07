# Phase 116: Anonymous-share and REST façade hotspot slimming - Context

**Gathered:** 2026-03-31
**Status:** Draft planning workspace

<domain>
## Phase Boundary

本 phase 处理 `HOT-49`：继续在既有 formal homes 内收窄 `custom_components/lipro/core/api/rest_facade.py` 与 `custom_components/lipro/core/anonymous_share/manager.py` 这两个仍偏厚的热点文件，但**不**改变 outward contract、stable import shell、registry/factory 入口与 child-façade composition truth。

本 phase 的目标不是“通过新增壳层把复杂度藏起来”，而是：
- 把 `LiproRestFacade` 的 session/token state proxy、transport/request wrapper density 再下沉到内聚的 inward support 机制；
- 把 `AnonymousShareManager` 的 scoped-state proxy、aggregate/scoped view 语义与 submit-outcome memory 进一步压缩到更明确的内部机制；
- 用 focused tests 冻结 formal home / factory / stable import / wrapper contract，确保热点瘦身不靠全量测试碰运气。

本 phase **不**处理：
- 新 public API / new outward root / compat shell；
- 回写 `v1.31` archived truth；
- 打开 `services/command.py`、`request_policy.py`、`status_fallback_support.py` 的下一轮热点治理；
- 伪造开源入口、delegate maintainer 或任何仓外 continuity 事实。
</domain>

<decisions>
## Implementation Decisions

- **D-01:** `custom_components/lipro/core/api/client.py` 继续作为 `LiproRestFacade` 的 stable import home；`custom_components/lipro/core/api/rest_facade.py` 继续作为 formal composition root。
- **D-02:** `rest_facade.py` 的 state / token / callback / transport wrapper 收窄必须发生在已有 formal home 或 support collaborator 内部，不新增第二 façade、compat adapter 或 package-level re-export。
- **D-03:** `AnonymousShareManager` 继续保持唯一 outward manager identity；aggregate/scoped 语义只能 inward split，不能长出第二条 production path。
- **D-04:** 对于两处热点，优先收敛“重复状态代理 / 分支语义 / discoverability 噪音”，而不是引入只会换名字的 helper shell。
- **D-05:** focused tests 至少冻结以下 contract：REST stable import + façade state binding contract；anonymous-share aggregate/scoped manager contract + submit-outcome / registry behavior。
- **D-06:** 本 phase 完成后，current route 应前推到 `Phase 116 complete; Phase 117 discuss-ready`，并保持 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md` 与 focused meta truth 同步。
</decisions>

<canonical_refs>
## Canonical References

- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/core/api/rest_facade.py`
- `custom_components/lipro/core/api/session_state.py`
- `custom_components/lipro/core/api/rest_facade_request_methods.py`
- `custom_components/lipro/core/api/rest_facade_endpoint_methods.py`
- `custom_components/lipro/core/api/request_gateway.py`
- `custom_components/lipro/core/api/request_policy.py`
- `custom_components/lipro/core/api/transport_executor.py`
- `custom_components/lipro/core/anonymous_share/manager.py`
- `custom_components/lipro/core/anonymous_share/manager_scope.py`
- `custom_components/lipro/core/anonymous_share/manager_submission.py`
- `custom_components/lipro/core/anonymous_share/manager_support.py`
- `custom_components/lipro/core/anonymous_share/registry.py`
- `tests/core/api/test_api.py`
- `tests/core/api/test_api_status_service_wrappers.py`
- `tests/core/anonymous_share/test_manager_scope_views.py`
- `tests/core/anonymous_share/test_manager_submission.py`
- `tests/core/anonymous_share/test_manager_recording.py`
- `tests/core/anonymous_share/test_observability.py`
- `tests/meta/governance_current_truth.py`
- `tests/meta/test_governance_route_handoff_smoke.py`
</canonical_refs>

<specifics>
## Specific Ideas

- `rest_facade.py` 当前最厚的噪音面不是 endpoint binding，而是大量 `RestSessionState` / transport / recovery 代理属性与薄 wrapper 并排堆叠，降低了 composition root 的可读性。
- `manager.py` 当前最厚的噪音面不是 record/build/submit 主流程，而是 `_state` 代理字段与 aggregate/scoped 分支语义交错，导致 manager 读起来像“状态镜像 + 行为容器”的混合物。
- 现有 `manager_scope.py`、`manager_submission.py`、`manager_support.py` 已经存在 inward split 方向；本 phase 应继续沿这条主线，而不是新造并列 support 家族。
</specifics>

<risks>
## Risks

- 如果只是把重复代理移动到另一个命名模糊的 helper，而没有减少认知分叉，热点会“换壳不减重”。
- 如果 focused tests 只验证行为大面，不冻结 stable import / state binding / aggregate-view contract，后续 hotspot burndown 仍可能悄悄回退。
- 如果 phase 完成后只更新 prose 不更新 machine-readable governance truth，`$gsd-next` 会再次误路由。
</risks>
