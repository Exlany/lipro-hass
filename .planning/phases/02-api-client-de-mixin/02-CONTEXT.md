# Phase 02: API Client De-Mixin - Context

**Gathered:** 2026-03-12
**Status:** Completed / validated (historical planning context retained for audit)
**Decision mode:** North-star arbitration by default
**Source:** `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `02-RESEARCH.md`, `02-ARCHITECTURE.md`, current API plane inspection

<domain>
## Phase Boundary

本阶段的边界非常明确：

**把 `REST / IoT` 协议主链从历史 mixin 聚合重建为一条显式、可测试、可挂接到统一协议根的正式 REST 主链。**

本阶段必须完成：
- 停止把 mixin aggregation 当成合法正式设计
- 审视整个 `custom_components/lipro/core/api/**/*.py` 及其直接测试消费者
- 以 `LiproRestFacade` 作为 Phase 2 的正式 REST 根重建设计与实现路径
- 把 `AuthSession / RequestPolicy / transport / auth recovery / payload normalizers / endpoint collaborators` 变成显式协作对象
- 将 compat 行为集中到**受控 compat shell / compat adapters**，并登记删除路径

本阶段明确**不做**：
- `LiproProtocolFacade` 最终统一根落地（属于 Phase 2.5）
- MQTT 子门面重构
- control plane、domain plane、runtime plane 的正式重构
- capability model 统一与 runtime invariants 正式化
</domain>

<upstream_inputs>
## Required Upstream Inputs

以下上游输入曾是 Phase 2 进入执行态前的阻塞条件；截至 2026-03-12，均已满足并完成 closeout：

- `Phase 1` 冻结的 protocol contract baseline 仍必须作为唯一外部行为真源
- baseline assets（`PUBLIC_SURFACES.md`、`DEPENDENCY_MATRIX.md`、`VERIFICATION_MATRIX.md`、`AUTHORITY_MATRIX.md`）必须继续充当边界与验证输入，而不是被 Phase 2 重写
- `STATE.md` 仍显示 `Phase 1 / 1.5` 未真正 closeout，因此 Phase 2 当前应视为 drafted / waiting，而不是“已无条件 ready”

换言之：**本文件保留的是 pre-execution context；Phase 2 当前状态已由 `02-VALIDATION.md` 与 `02-01~02-04-SUMMARY.md` 定格为 Completed / validated。**
</upstream_inputs>

<decisions>
## Implementation Decisions

### Locked Decisions
- `LiproClient` 不能继续作为多重继承聚合体存在于正式架构中
- **`LiproRestFacade` 是 Phase 2 的正式 REST root**；它必须天然可挂接到未来的 `LiproProtocolFacade`
- `LiproProtocolFacade` 是终态正式协议根，但不在 Phase 2 直接落地
- `LiproClient` 若在 Phase 2 结束后仍存在，也只能是短期 compat shell，不能继续承载正式协议逻辑
- protocol normalization 必须发生在 protocol plane 边界内部
- `AuthSession / retry / rate-limit / reauth / request policy / payload normalizers` 必须闭环于 protocol plane
- Phase 2 必须留下治理收尾：`FILE_MATRIX`、`RESIDUAL_LEDGER`、`KILL_LIST`、`VERIFICATION_MATRIX` 至少完成针对本 slice 的更新或状态确认

### Claude's Discretion
- façade / collaborator / normalizer 的确切模块命名，只要边界清晰即可
- 临时 compat shell 的命名，只要不会误导为正式 root
- endpoint collaborators 是按域对象拆分，还是 façade 下的 service-like collaborators，只要不回到 mixin 聚合即可
</decisions>

<specifics>
## Specific Ideas

- 以 `LiproRestFacade` 取代 “`_ClientTransportMixin -> _ClientAuthRecoveryMixin -> _ClientPacingMixin -> _ClientBase`” 这条继承主链
- 用显式 collaborators 取代 `_ClientEndpointsMixin` 聚合，优先按 `auth / devices / status / commands / misc / schedule` 分域
- 将 `payloads.py` 与 service helpers 收拢到 canonical normalizers / protocol helpers 叙事中，而不是继续散落在 façade 旁路
- 保持 Phase 1 contract fixtures 作为唯一行为真相，不让新 façade 反向定义 contract
- 把 compat wrappers 与 legacy payload shapes 写进 residual / kill truth，而不是继续内联在 façade folklore 中
</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `custom_components/lipro/core/api/request_codec.py`、`request_policy.py`、`transport_core.py`、`transport_retry.py`、`transport_signing.py`、`response_safety.py`：具备保留/重构价值，可作为显式执行链基座
- `custom_components/lipro/core/api/endpoints/*.py`：天然适合演进为显式 endpoint collaborators
- `tests/core/api/test_protocol_contract_matrix.py`：继续作为协议重构的行为护栏
- `tests/core/api/test_api_client_transport.py`：适合验证 transport/auth/pacing 协作边界
- `tests/core/api/test_api.py` 与 service tests：适合验证 façade 与 endpoint/service 公开面

### Established Patterns
- 正式 public root 与终态名称必须对齐，不再接受“历史 public name 继续定义架构”
- contract baseline 是行为真相，不能被 mixin 继承链反向塑形
- compat 允许短期存在，但必须集中、可计数、可删除
- 每个 phase 都必须回写 governance outputs，而不是只跑测试

### Integration Points
- `Phase 2` 直接承接 `Phase 1` 的 contract baseline
- `Phase 2` 的输出必须能被 `Phase 2.5` 直接提升为 `LiproProtocolFacade + LiproMqttFacade`
- `Phase 2` 的 compat shell / adapters 状态将直接决定 `Phase 2.5` 与 `Phase 7` 的清理成本
</code_context>

<downstream_contract>
## Downstream Contract

### Contract for Phase 2.5
`Phase 2.5` 只能建立在以下 Phase 2 输出之上：
- `LiproRestFacade` 已成为明确的 Phase 2 正式 REST root
- canonical normalization 已在 REST protocol boundary 内收口
- `LiproClient` 与 legacy public names 已降级为 compat shell / residual，而不是继续主导 public direction
- governance outputs 已能清楚回答：哪些 compat 要在 `2.5` 清退，哪些 wrapper 仍需迁移

### Contract for Later Phases
- `Phase 2.6` 不能把 share / firmware / support payload authority 回写给 Phase 2
- `Phase 3` 不得直连 `LiproRestFacade` internals，只能把 Phase 2 视作 unified protocol root 的上游台阶

### Required Outputs Before Downstream Unblocks
- `.planning/phases/02-api-client-de-mixin/02-ARCHITECTURE.md`
- `.planning/phases/02-api-client-de-mixin/02-VALIDATION.md`
- `.planning/phases/02-api-client-de-mixin/02-01-SUMMARY.md`
- `.planning/phases/02-api-client-de-mixin/02-02-SUMMARY.md`
- `.planning/phases/02-api-client-de-mixin/02-03-SUMMARY.md`
- `.planning/phases/02-api-client-de-mixin/02-04-SUMMARY.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
</downstream_contract>

<deferred>
## Deferred Ideas

- `LiproProtocolFacade` 统一协议根落地
- `LiproMqttFacade` 子门面并入统一协议根
- telemetry / architecture enforcement 深化
- control plane lifecycle cleanup
- domain capability registry unification
- runtime invariant enforcement

这些都属于后续 phase，不回灌到 Phase 2。
</deferred>

---
*Phase: 02-api-client-de-mixin*
*Context refreshed: 2026-03-12 via north-star arbitration refresh*
