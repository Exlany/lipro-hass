# Phase 02 Architecture: REST Protocol Slice North-Star Design

## Objective

将当前 `LiproClient` 的多重继承聚合，重建为一套面向统一协议平面根的显式结构：

- **Phase 2** 先落 `LiproRestFacade`
- **Phase 2.5** 再把 `LiproRestFacade` 挂接到 `LiproProtocolFacade`

因此，Phase 2 的判断标准不是“client 还能不能跑”，而是：
- REST 正式根是否清晰
- 协作者边界是否显式
- compat 是否已被收口为迁移残留
- 后续是否能无痛挂接统一协议根

## Current Structural Problem

当前主链大致为：

- `LiproClient(_ClientTransportMixin, _ClientEndpointsMixin)`
- `_ClientTransportMixin(_ClientAuthRecoveryMixin)`
- `_ClientAuthRecoveryMixin(_ClientPacingMixin)`
- `_ClientPacingMixin(_ClientBase)`
- `_ClientEndpointsMixin(...)` 聚合多个 endpoint mixin

这导致：

1. 正式 public surface 与历史 compat name 混在一起
2. transport / auth recovery / pacing / endpoints 通过继承耦合，而不是显式组合
3. canonical normalization 与 wrapper folklore 缠绕，难以定位 protocol boundary
4. 很难直接作为 `LiproProtocolFacade` 的可插拔 REST 子门面

## End-State Slice Design

```text
LiproRestFacade
├── RestSessionState
├── RestTransportExecutor
│   ├── RequestSigner
│   ├── RetryPolicy
│   ├── RateLimitPolicy
│   └── ResponseGuard
├── RestAuthRecoveryCoordinator
├── EndpointCollaborators
├── PayloadNormalizers
└── CompatAdapters (temporary / explicit / removable)
```

## Executable Component Contracts

### 1. `LiproRestFacade`

- **唯一正式 REST public root**：Phase 2 之后，REST 协议只承认 `LiproRestFacade` 是正式根。
- **只做 orchestration**：负责装配 session/auth state、transport、endpoint collaborators、normalizers 与 compat shell seam。
- **不持有重复状态**：不得自己复制 token、refresh lock、request pacing state。
- **为 Phase 2.5 预留稳定挂接点**：必须天然可被 `LiproProtocolFacade` 包装，而不是再长出第二套长期合法 surface。

### 2. `RestSessionState`

- **唯一 session/auth state owner**：拥有 `aiohttp.ClientSession`、`phone_id`、`request_timeout`、`access_token`、`refresh_token`、`user_id`、`biz_id`、`entry_id`、refresh single-flight lock。
- **状态变更边界清晰**：transport 只读取 session/token；真正写 token 与 refresh state 的只能是 auth recovery chain。
- **不得藏在 façade 之外的全局变量里**：Phase 2 不允许 endpoint / helper 自行缓存 auth state。

### 3. `RestTransportExecutor`

- **唯一 transport owner**：拥有 request encoding、signing、HTTP execution、response safety、request token / telemetry、网络异常分类。
- **依赖显式 policy**：rate-limit backoff、busy retry、retry-after parsing 必须通过 `RequestPolicy` / retry collaborator 注入，而不是散落在 façade 或 endpoint methods 内。
- **不改 auth state**：transport 只能返回认证失败分类结果，由 auth recovery 决定是否 refresh / replay。

### 4. `RequestPolicy`

- **唯一 request pacing / retry budget owner**：拥有 command pacing、rate-limit backoff、retry 上限、sleep / wait strategy。
- **必须是可注入、可测的协作者**：不得继续依赖 `_ClientPacingMixin` 的隐式内部状态或散落 `asyncio.sleep`。
- **不拥有 payload 语义**：不能顺手做 normalizer、compat wrapper 或 endpoint-specific fallback folklore。

### 5. `RestAuthRecoveryCoordinator`

- **唯一 auth recovery owner**：负责 auth code classification、single-flight refresh、token persistence callback 与安全 replay。
- **只处理认证恢复，不处理 endpoint 语义**：它可以决定“是否 refresh / replay”，但不能同时决定 payload 如何归一化或 wrapper 如何输出。
- **与 transport 的接口必须是显式 replay seam**：refresh 成功后只能通过同一 transport executor 重放安全请求，不得回退到旧 mixin 直连路径。

### 6. `EndpointCollaborators`

- **按域拆分**：至少允许 `auth / devices / status / commands / misc / schedule` 六类 collaborator。
- **只拥有 path/body assembly 与 endpoint-local orchestration**：endpoint collaborator 可以选择 path、body schema、normalizer 组合，但不能私自持有 session/token。
- **不再以 mixin 聚合**：可以复用 helper modules，但正式形态必须是 façade 持有的显式协作者。

### 7. `PayloadNormalizers`

- **唯一 canonical payload owner**：负责把 vendor payload、legacy list wrappers、schedule JSON、status rows 等收敛为 protocol plane 的 canonical shape。
- **禁止 raw payload 外泄**：runtime / domain / entity 只能收到 canonical shape；原始 envelope 只能停留在 protocol boundary 内部。
- **compat 只能从 canonical shape 退化**：若仍需旧输出形态，只能由 compat shell 基于 canonical output 生成，而不是 normalizer 直接产生双标准输出。

### 8. `CompatShell / CompatAdapters`

- **唯一 legacy public-name owner**：`LiproClient` 若保留，只能是 `LiproRestFacade` 之外的 transitional compat shell。
- **只允许两类残留**：legacy method names、legacy wrapper envelopes。
- **不得承载正式协议逻辑**：签名、transport、auth recovery、canonical normalization 都不能继续留在 compat shell 内。
- **必须可计数、可删除**：所有 compat entries 都必须出现在 `FILE_MATRIX`、`RESIDUAL_LEDGER`、`KILL_LIST`。

## Formal Ownership Rules

| Concern | Formal Owner | Allowed Collaborators | Must Not Be Owned By |
|---|---|---|---|
| REST public entry | `LiproRestFacade` | endpoint collaborators、compat shell forwarding | `LiproClient`, endpoint mixins |
| session / auth state | `RestSessionState` | `RestAuthRecoveryCoordinator`, `RestTransportExecutor` | façade duplicates, endpoint helpers |
| transport / retry / pacing | `RestTransportExecutor` + `RequestPolicy` | `TransportCore`, `TransportRetry`, `TransportSigning` | ad-hoc helpers in `client.py`, mixin chain |
| auth recovery / replay | `RestAuthRecoveryCoordinator` | `AuthApiService`, token persistence callback, `RestTransportExecutor` | endpoint methods, compat wrappers |
| canonical normalization | payload normalizers | diagnostics / status / schedule / power helpers | runtime/domain/entity consumers |
| compatibility naming / envelopes | compat shell / adapters only | façade forwarding | formal public surface |

## State & Mutation Ownership

| State / Concern | Single Owner | May Read | Must Not Mutate / Own |
|-----------------|--------------|----------|------------------------|
| `aiohttp.ClientSession` | `RestSessionState` | `RestTransportExecutor` | endpoint collaborators、compat shell |
| `access_token` / `refresh_token` / `user_id` / `biz_id` | `RestSessionState`（由 `RestAuthRecoveryCoordinator` 写入） | façade、transport、endpoint collaborators | `RestTransportExecutor`、normalizers |
| refresh single-flight lock | `RestSessionState` + `RestAuthRecoveryCoordinator` | façade（只协调） | endpoint collaborators、compat shell |
| retry / backoff / pacing state | `RequestPolicy` | `RestTransportExecutor` | façade、endpoint collaborators、legacy mixins |
| raw vendor payload | `RestTransportExecutor` / endpoint collaborators（短暂存在） | payload normalizers | runtime/domain/entity |
| canonical protocol payload | payload normalizers | façade、compat shell、downstream formal consumers | legacy mixins |
| legacy names / wrapper envelopes | compat shell | direct consumer tests（暂时） | formal façade、normalizers |

## Boundary Rules

### 1. REST Root Rule
`LiproRestFacade` 是 Phase 2 的唯一正式 REST root；`LiproClient` 若保留，只能是 façade 之外的临时 compat shell。

### 2. Explicit Collaboration Rule
transport / auth recovery / pacing / endpoints / normalizers 都必须通过显式组合出现，而不是通过多重继承聚合。

### 3. Session State Rule
`RestSessionState` 是 auth/session state 的唯一事实源；任一 endpoint/helper 都不得自行缓存 token、refresh lock 或会话句柄。

### 4. Request Policy Rule
rate-limit、busy retry、command pacing 与 replay budget 必须是独立 policy；不允许把 sleep/backoff 继续埋在 façade 或 endpoint mixin 私有方法里。

### 5. Auth Recovery Rule
认证恢复只能经 `RestAuthRecoveryCoordinator` 触发；refresh 后 replay 必须走同一 transport executor，并且只允许显式、安全、有限次重放。

### 6. Normalization-at-Boundary Rule
canonical protocol contracts 必须在 REST protocol boundary 完成；runtime / domain / entity 不直接消费 raw vendor payload 或 legacy wrappers。

### 7. Compat Demotion Rule
compat shell 不得成为文档、测试、消费者默认叙事中的正式根；必须显式登记 residual owner 与 kill condition。

## Request Lifecycle

1. 调用方进入 `LiproRestFacade` 的 canonical method。
2. façade 选择 endpoint collaborator 与 request policy profile。
3. endpoint collaborator 只构造 path/body/request metadata。
4. `RestTransportExecutor` 通过 `RestSessionState` 完成 encoding、signing、HTTP execution、response safety 与 telemetry。
5. 如遇认证失败，由 `RestAuthRecoveryCoordinator` 负责 refresh / replay；transport 本身不直接改 token。
6. response 进入 payload normalizers 形成 canonical output；只有 `LiproClient` compat shell 可以在最后一步退化为 legacy wrappers / legacy names。

## File Governance Guidance

### Keep / Refactor as Core Slice
- `custom_components/lipro/core/api/request_codec.py`
- `custom_components/lipro/core/api/request_policy.py`
- `custom_components/lipro/core/api/transport_core.py`
- `custom_components/lipro/core/api/transport_retry.py`
- `custom_components/lipro/core/api/transport_signing.py`
- `custom_components/lipro/core/api/response_safety.py`
- `custom_components/lipro/core/api/endpoints/*.py`

### Review for Adapter / Delete
- legacy-style list payload wrappers inside `client.py`
- mixin aggregator modules once explicit collaborators land
- tests overfitted to inheritance/private method patching
- direct consumers that still assume `LiproClient` is the formal root

## Execution Shape

### Plan 02-01
- 建立正式设计、文件治理矩阵、残留与删除台账
- 明确 `LiproRestFacade` public surface 与 Phase 2 exit contract

### Plan 02-02
- 重写 façade、session/auth state、transport、auth recovery、pacing/request policy 协作边界
- 让 REST 主链不再以 mixin 继承存在

### Plan 02-03
- 迁移 endpoint collaborators 与 payload normalizers
- 把 helper/service 层收回 canonical protocol contract 叙事

### Plan 02-04
- 收口 compat shell、旧 public names 与 legacy wrappers
- 更新治理产物并完成 Phase 2 handoff 到 Phase 2.5

## Downstream Contract

Phase 2 的输出必须以不与后续 phase 打架为前提：

- **Upstream truth 来自 Phase 1**：Phase 2 只能消费已冻结的 protocol contract baseline，不能重新定义 contract 真相。
- **Phase 2.5 才统一协议根**：`LiproRestFacade` 是 Phase 2 正式 REST root，但它必须天然可挂到 `LiproProtocolFacade`，不能形成第二套长期合法 public surface。
- **Phase 2.6 才 formalize external boundaries**：share / firmware / support payload 的 owner、authority source、fixture 与 drift detection 不在 Phase 2 内拍板。
- **Phase 3 不得直连 protocol plane internals**：control plane 后续只能通过 runtime / public contracts 间接消费协议能力，而不是把 `LiproRestFacade` 拉回控制面当事实根。

## Required Handoff Artifacts

`Phase 2.5` 在解阻前，必须能引用以下 Phase 2 产物：
- `.planning/phases/02-api-client-de-mixin/02-ARCHITECTURE.md`
- `.planning/phases/02-api-client-de-mixin/02-VALIDATION.md`
- `02-01/02/03/04-SUMMARY.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`

## Evolution Path

- **Phase 2**：先完成 `LiproRestFacade`，清空 REST / IoT 历史 mixin 主链的正式地位
- **Phase 2.5**：把 `LiproRestFacade` 与 `LiproMqttFacade` 一起挂接到 `LiproProtocolFacade`
- **After 2.5**：control / runtime / assurance 只面向统一协议根协作
