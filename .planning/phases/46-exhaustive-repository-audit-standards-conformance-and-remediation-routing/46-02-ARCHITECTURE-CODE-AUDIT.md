# Phase 46 Architecture, Code, Test-Topology, and Typed-Budget Audit

## Scope and Method

- 审阅基线：`docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`docs/developer_architecture.md`、`.planning/baseline/PUBLIC_SURFACES.md`、`.planning/baseline/DEPENDENCY_MATRIX.md`、`.planning/reviews/RESIDUAL_LEDGER.md`、`46-01-REPO-INVENTORY.md`。
- 审阅对象：`264` 个生产 Python 文件（约 `39071` LOC）与 `286` 个测试文件（约 `51478` LOC）。
- 审阅重点：formal roots、public surfaces、dependency direction、热点与命名、mega-test topology、typing/exception budget、旧残留与后续路由。
- 量化补充：当前生产代码粗粒度统计为 `Any=534`、`type: ignore=0`、`broad catch=0`；测试代码为 `Any=227`、`type: ignore=13`、`broad catch=2`。这说明生产路径的异常语义已经相当克制，但类型债仍明显集中在若干 API surface 与 read-model heavy 模块。

## Formal Roots

### Root Verdict Matrix

| Surface | Current signal | Strengths | Gaps | Verdict | Priority |
|---|---|---|---|---|---|
| `custom_components/lipro/core/protocol/facade.py:39` | `475` LOC，单类根 | 单一 protocol root 叙事稳固；child façade 组合明确；没有退回 split-root | 根类仍偏厚；多类 REST/MQTT convenience 入口继续堆叠在单文件 | `keep + split inward` | `P1` |
| `custom_components/lipro/core/api/rest_facade.py:39` | `454` LOC，`Any` 热点 | REST formal child façade 身份明确；collaborator-based construction 正确 | `Any` 密度高；request/unwrap/endpoint forwarding 仍重；容易继续长成“第二根” | `keep + forbid growth + split inward` | `P1` |
| `custom_components/lipro/core/coordinator/coordinator.py:53` | `444` LOC，runtime root | 单一 runtime root 仍成立；协调器主链没有被 service/control 旁路替代 | runtime orchestration 仍偏厚；entity lifecycle / update flow / service orchestration 聚在一起 | `keep + split inward` | `P1` |
| `custom_components/lipro/control/runtime_access.py:155` | `467` LOC，多 projection helper | 成功成为 control plane 唯一 runtime read-model home；阻断散落 `runtime_data` 读取 | 已从“唯一 helper home”膨胀成大型 projection library；telemetry/system-health/diagnostics 读模型逻辑持续加码 | `keep + split inward + forbid growth` | `P0` |
| `custom_components/lipro/__init__.py:400` | `417` LOC，factory wiring root | 工厂式按需装配保住了测试 patchability；没有回退 eager singleton | 入口生命周期、options snapshot、reload/auth wiring 仍挤在根模块 | `keep + slim wiring` | `P1` |
| `custom_components/lipro/control/entry_lifecycle_controller.py:100` | `412` LOC | `Protocol` + dataclass + 显式 factory 注入设计成熟 | listener / reload / setup artifacts / coordinator factories 仍在单体 controller 中 | `keep + split inward` | `P1` |
| `custom_components/lipro/diagnostics.py:78` + `custom_components/lipro/system_health.py:16` | adapter entry | diagnostics / system health 都通过正式 surface 暴露，而非私有 backdoor | 仍受 `RuntimeAccess` 体量与 redaction helper 粘连影响 | `keep` | `P2` |

### Root-by-Root Notes

- `LiproProtocolFacade` 仍是仓库里最像“正式主链”的对象：文件头直接声明 unified protocol root，child façade composition 清晰，`CanonicalProtocolContracts`、`ProtocolDiagnosticsContext`、`ProtocolTelemetry` 的集中持有方式是优点，而不是负担。
- `LiproRestFacade` 现在更像“合法 child façade + 仍未拆薄完成的请求聚合器”。它不再是错误架构，但若继续向里塞 `Any`、unwrap 和 endpoint glue，就会再次接近“隐形第二根”。
- `Coordinator` 的架构位置是对的：单一 runtime root 与 `protocol_service` 的边界故事没有倒退。但测试和文件体量都说明它仍是高杠杆热点，下一轮应继续往 polling / lifecycle / runtime facet inward decomposition。
- `RuntimeAccess` 是当前最需要警惕的“非根巨石”。它不是架构错误，相反它是对的 helper home；问题是对的 helper home 正在承载过多 projection、telemetry、snapshot、device lookup 语义。
- `__init__.py` 的 patch-friendly 工厂设计必须保留；任何 eager module binding、模块级 singleton 回退都将直接破坏 `tests/core/test_init*.py` 这类回归面。
- `EntryLifecycleController` 的方向对，但体量已经提示应引入更清楚的 collaborator slicing，而不是继续向 controller 本体追加新场景。

## Public Surfaces and Ownership

- 当前 public surface 叙事总体健康：`LiproProtocolFacade` 是唯一正式 protocol-plane root，`LiproRestFacade` 与 `LiproMqttFacade` 是 child façade，`Coordinator` 是唯一 runtime root，control/services/platforms 主要通过正式 surface 协作。
- `custom_components/lipro/core/api/client.py:1` 仅剩稳定 import home 身份，这比继续公开 legacy root name 更诚实。
- `custom_components/lipro/core/coordinator/services/protocol_service.py` 与 `runtime_types.LiproCoordinator.protocol_service` 把 runtime-owned protocol capability port 固定下来，这是一条非常值得保留的正式 seam。
- `custom_components/lipro/control/runtime_access.py:155` 继续是 control plane 唯一允许的 runtime read-model 入口，说明 control/public surface 没有倒退为 scattered locator story。
- `services/execution.py` 只保留正式 service execution facade 身份；残留账本明确禁止把它重新写成 runtime auth seam。这个裁决目前仍被遵守。

### Ownership Quality

- 优点：`core/protocol`、`core/api`、`core/coordinator`、`control`、`services`、`flow`、`entities`、top-level platform entries 的目录边界总体清楚。
- 优点：`Protocol`、`OperationOutcome`、`reason_code`、`Protocol*` / `*Surface` / `*Service` 等命名在多数情况下能反映 ownership。
- 缺点：`*_support.py`、`*_surface.py`、`*_service.py` 的数量开始变多，单靠文件名已不足以判断“正式 surface”还是“内部 helper”。
- 缺点：`request_gateway.py`、`endpoint_surface.py`、`status_fallback.py` 这类命名虽然诚实，但仍偏抽象，需要进一步减少 `Any` 才能真正成为 typed public helper，而不是“结构看起来对”。

## Dependency Direction and Boundary Seams

- 依赖方向总体是本仓库的强项之一：`tests/meta/test_dependency_guards.py` 与 `tests/meta/test_public_surface_guards.py` 已把 protocol/runtime/control/entity/platform 的禁行方向固定成门禁。
- `DEPENDENCY_MATRIX` 明确要求 control 不得旁路 runtime public surface、protocol 不得感知上层宿主语义、compat shell 不得反向定义 public surface；当前代码没有出现明显故事线回流。
- `MqttRuntime`、`EntryLifecycleController`、`BackgroundTaskManager`、`diagnostics_api_service.py` 中大量 `Protocol` / collaborator 注入信号表明仓库已经从继承聚合切换到组合式架构，这一点符合国际优秀开源实践。
- 真正的风险不在“是否有第二套架构”，而在“正确架构上的 helper 家族是否继续变巨”。`RuntimeAccess`、`RestFacade`、`AnonymousShareManager` 都属于这个类别。

## Hotspots and Naming Discipline

### Formal-root hotspots

- `custom_components/lipro/core/protocol/facade.py` — `475` LOC：正式根、不是错误，但应把子能力继续 inward；避免继续堆 convenience surface。
- `custom_components/lipro/core/api/rest_facade.py` — `454` LOC：`Any` 热点之一；建议把 request/unwrap/payload path 再往 `request_gateway` / typed endpoint helpers inward。
- `custom_components/lipro/core/coordinator/coordinator.py` — `444` LOC：运行根仍然太宽，优先继续向 runtime/service helpers 切薄。
- `custom_components/lipro/control/runtime_access.py` — `467` LOC：当前最需要守住“唯一 helper home，不等于无限 helper home”。
- `custom_components/lipro/__init__.py` — `417` LOC：工厂 wiring 正确，但 lifecycle / auth / options snapshot 体量需要继续压缩。
- `custom_components/lipro/control/entry_lifecycle_controller.py` — `412` LOC：显示性与可测试性都很好，但 controller 本体仍偏厚。

### Non-root helper hotspots

- `custom_components/lipro/core/anonymous_share/manager.py` — `536` LOC：这是全仓最大的生产 Python 文件；它更像“成熟但巨大的 helper family root”，不是 formal root。必须避免误把它当成架构主链问题，但也应列为下一轮 helper decomposition 热点。
- `custom_components/lipro/core/api/request_policy.py` — `463` LOC：职责相对聚焦在 pacing / retry policy，是“体量偏大但语义集中”的 helper，优先级低于 formal roots。
- `custom_components/lipro/core/api/diagnostics_api_service.py` — `442` LOC：`OperationOutcome`、`reason_code` 语义非常好，说明 typed failure contract 已进入 API 层；但 OTA query、cloud metadata、history fetch 聚在单文件。
- `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py` — `420` LOC：依赖注入与 protocolized collaborators 是优点，说明不是“坏巨石”；但 runtime lifecycle 仍有继续 topicize 的空间。
- `custom_components/lipro/core/api/request_gateway.py` — `293` LOC：从 RestFacade 中剥出的 gateway 是进步，但仍然是 `Any` 高密度区域。
- `custom_components/lipro/core/api/endpoint_surface.py` — `256` LOC：`Any` 命中数仓库最高（按当前粗粒度热点统计为 `29`）；这是 typed surface 最大短板之一。

### Naming verdict

- **优点**：大多数命名已经从 legacy/client/mixin folklore 升级为 `Facade`、`Service`、`Surface`、`Protocol`、`Runtime`、`Outcome`、`Snapshot` 等可解释术语。
- **缺点**：命名收敛仍未彻底压缩“语义同类但文件名前缀不同”的现象，特别是 `*_support`、`*_surface`、`*_service`、`*_fallback` 在 API/control/services 之间会给初次审阅者制造认知摩擦。
- **总体裁决**：命名规范度已达中高水位；真正欠缺的不是 rename，而是继续把命名背后的 ownership 压实，让“看起来像 surface 的文件”都真正承担 typed / narrow 的 surface 责任。

## Mega-Test Topology

### Hotspot matrix

| File | LOC | Coverage surface | Main issue | Verdict | Priority |
|---|---:|---|---|---|---|
| `tests/meta/test_governance_closeout_guards.py:84` | `922` | milestone archive / promoted evidence / phase closeout truth | megaguard 吸附过多 phase story，失败半径大 | `topicize` | `P0` |
| `tests/core/test_coordinator.py:69` | `791` | runtime root / services / lifecycle / update flow | 多故事线混放，运行根验证巨石 | `topicize` | `P0` |
| `tests/core/test_diagnostics.py:22` | `718` | redaction / entry diagnostics / device diagnostics / failure summary | diagnostics 行为与 redaction story 混放 | `topicize` | `P0` |
| `tests/core/api/test_api_command_surface.py:18` | `1168` | command surface / error handling / 429 / IoT branch | 已按类分段，但单文件覆盖面仍过宽 | `topicize selectively` | `P1` |
| `tests/core/mqtt/test_transport_runtime.py:17` | `1081` | transport lifecycle / subscriptions / decode / reconnect loop | 结构比 coordinator 更清楚，但仍太宽 | `topicize selectively` | `P1` |
| `tests/platforms/test_update.py:24` | `1041` | manifest / certification / install / cache / arbitration | 主题集中但平铺过长，平台 megatest 典型 | `topicize` | `P1` |
| `tests/meta/test_public_surface_guards.py:43` | `413` | public exports / adapter bans / helper-only rules | 跨 phase 叙事叠加，继续长胖风险高 | `split by concern` | `P1` |
| `tests/platforms/test_light.py:15` / `test_fan.py:13` / `test_select.py:15` | `696~851` | 单平台语义 | 仍大，但领域聚焦好于 governance megaguards | `defer after P0/P1` | `P2` |

### Strength zones

- `tests/core/api/test_protocol_contract_matrix.py`、`tests/core/api/test_protocol_replay_rest.py`、`tests/core/mqtt/test_protocol_replay_mqtt.py`、`tests/integration/test_protocol_replay_harness.py`、`tests/meta/test_protocol_replay_assets.py` 形成了漂亮的 protocol contract → replay → harness → asset authority 闭环。
- external-boundary hardening 链路成熟：`tests/meta/test_external_boundary_fixtures.py`、`tests/meta/test_external_boundary_authority.py`、`tests/core/test_share_client.py`、`tests/services/test_services_diagnostics.py`、`tests/core/ota/test_firmware_manifest.py` 与 `tests/platforms/test_update.py` 共同构成高质量 assurance chain。
- fixture / shared builders 入口设计健康，`tests/conftest.py` 与 `tests/conftest_shared.py` 没有明显沦为无边界万能工厂。

## Failure Localization Radius

- 当前 failure-localization 最差的不是平台 tests，而是治理 megaguards：`test_governance_closeout_guards.py`、`test_public_surface_guards.py` 往往在首个 phase/doc/token 断言处炸掉，读者需要大量上下文才能定位真实 drift。
- `tests/core/test_coordinator.py` 与 `tests/core/test_diagnostics.py` 的失败半径也偏大，因为一个 suite 同时覆盖多个 runtime/diagnostics 子故事线。
- `tests/platforms/test_update.py` 虽然很长，但因为主题聚焦在 firmware/update，失败解释性反而强于 governance megaguards。
- 最佳实践方向不是“把所有大测试都拆成更多文件”，而是优先拆那些同时吸附多故事线、首炸点信息量低、参数化维度高的 megas。

## Typing and Exception Budget

### What is already strong

- `pyproject.toml` 开启 `mypy strict = true`，说明仓库不再把类型检查当装饰品。
- `tests/meta/test_phase31_runtime_budget_guards.py` 与 `tests/meta/test_phase45_hotspot_budget_guards.py` 已把 touched-zone `Any` / `broad catch` / `type: ignore` 变成 no-growth contract。
- 生产代码当前 `type: ignore=0`、`broad catch=0`，这是一个很强的信号：异常语义与类型豁免已经从“无序借口”收敛到“少量显式预算”。
- `OperationOutcome` + `reason_code` 在 `diagnostics_api_service.py`、`mqtt_runtime.py`、`anonymous_share/share_client.py` 等模块中的使用非常成熟，这是 typed failure semantics 的亮点，而非 debt。

### Current pressure points

- `custom_components/lipro/core/api/endpoint_surface.py`：`Any` 热点最高；核心问题不是文件大，而是 surface 本身仍暴露了过多弱类型 mapping。
- `custom_components/lipro/core/api/rest_facade.py`：`Any` 命中高，且 `unwrap` / `_require_mapping_response` / payload plumbing 继续堆在 façade 内部。
- `custom_components/lipro/core/api/request_gateway.py` 与 `rest_facade_request_methods.py`：说明 REST typed surface 已开始 inward split，但 split 还未完成。
- `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py` 与 `core/utils/background_task_manager.py`：这里的 `Any` 大多属于 asyncio / coroutine typing friction，可被视作相对可接受的 sanctioned backlog。
- `tests/conftest.py` 与若干 meta/test helpers 的 `Any` 命中并不意外，但它们会放大 repo-wide 粗粒度指标，因此 Phase 47+ 应把“生产债”和“测试/guard 自描述字面量”分开统计。

### Budget verdict

- **sanctioned / structurally understandable**：`mqtt_runtime.py`、`background_task_manager.py` 这类 asyncio-protocol friction；`diagnostics_api_service.py` / `share_client.py` 中带 `OperationOutcome` 与 `reason_code` 的桥接型 `Any`。
- **guarded backlog**：`rest_facade.py`、`request_gateway.py`、`rest_facade_request_methods.py`、`endpoint_surface.py` 的 mapping-heavy API surface。
- **unguarded but low-risk**：若干 test helper / fixture builder / harness 文件中的 `Any`，短期不会破坏生产契约，但会继续污染 repo-wide 指标。
- **must-reduce-next**：`endpoint_surface.py` 与 `rest_facade.py` 的 public-ish helper surface；这两处若不继续 typed reduction，会持续拖慢 REST child façade 的可信度。

## Residual and Legacy Routing

### Historical only

- `compat / mixin / legacy public-name residual` 已在 earlier phases 关闭；`LiproClient` compat shell、`LiproMqttClient` legacy naming、private runtime auth seam、API aggregate endpoint mixin 均已退出 active residual 家族。
- 当前不应再把这些旧名字当成 active architectural concern，它们已经是历史解释成本，而不是当前主链的实债。

### Sustainment debt

- formal roots 体量偏大，但都还在正确边界上。
- `RuntimeAccess` 从唯一 helper home 继续长成 projection megafile 的风险。
- REST surface `Any` 聚集，特别是 `endpoint_surface.py` / `rest_facade.py` / `request_gateway.py`。
- mega-tests 尤其是 governance megaguards、coordinator、diagnostics 与 update 平台 suite 的 failure-localization debt。
- helper family hotspots：`AnonymousShareManager`、`diagnostics_api_service.py`、`request_policy.py`。

### Must-delete-next / must-move-next

- 生产代码当前没有需要“立刻物理删除”的 active residual family。
- 测试侧存在若干应 re-home 的仓顶文件：`tests/test_coordinator_public.py`、`tests/test_coordinator_runtime.py`、`tests/test_refactor_tools.py`；它们更像目录 home 不对，而不是应该删除。
- 下一轮更像 `topicize / re-home / typed-reduce / forbid-growth`，而不是 `rm legacy shell`。

## Priority Findings

### P0

1. **限制 `RuntimeAccess` 增长并开始 projection topicization**：这是当前最像“正确 helper 变成新热点根”的对象。
2. **拆 `tests/meta/test_governance_closeout_guards.py`、`tests/core/test_coordinator.py`、`tests/core/test_diagnostics.py`**：优先改善 failure localization，而不是继续堆断言。
3. **把 typed budget 统计明确分成 production debt 与 guard/test literal debt**：否则 repo-wide `Any` 指标会继续掺噪。

### P1

1. **继续 inward split `LiproRestFacade` / `RestRequestGateway` / `RestEndpointSurface`**，重点是减少 mapping-heavy `Any` 面积。
2. **继续瘦身 `Coordinator`、`EntryLifecycleController`、`__init__.py`**，保持 single-root 但降低决策密度。
3. **topicize `tests/platforms/test_update.py` 与 `tests/core/mqtt/test_transport_runtime.py`**，把“长但聚焦”的 suite 进一步变得可诊断。
4. **把 `AnonymousShareManager`、`diagnostics_api_service.py` 从“大而正确”推向“更小而同样正确”**。

### P2

1. **命名降噪**：不是大规模 rename，而是逐步减少 `*_support` / `*_surface` / `*_service` 的职责歧义。
2. **保留 contract-hardening 主链不动**：尤其是 protocol contract / replay / external-boundary 这组亮点，不要为了拆分而破坏其 authority chain。
3. **整理仓顶零散 tests 的 domain home**，提升目录可发现性与维护体验。
