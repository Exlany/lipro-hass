# Phase 02 Research: API Client De-Mixin

**Updated:** 2026-03-12
**Research mode:** implementation / architecture baseline
**Decision stance:** 不受历史成本约束，以 Home Assistant + Python async 生态下的最优终态为准

## Research Framing

本 research 不回答“如何最便宜地改动现有代码”，而回答：

- 在当前 Home Assistant 集成最佳实践下，`API Client` 的**正式终态**应该是什么？
- 哪些能力应当由现成标准模式承担，哪些必须保留为本仓库的显式自定义设计？
- 哪些“看起来很现代”的做法其实不值得引入？

结论先行：

- **正式终态应为显式 façade + focused collaborators + canonical contracts**
- **不应继续把 mixin、多重继承、散落 compat wrappers 当作协议层正式设计**
- **最先进的方向不是更重的框架，而是更强的边界纪律、类型边界、自动化护栏与观测能力**

## Standard Stack

### 1. Home Assistant 标准运行模式

**Use**:
- `DataUpdateCoordinator` 作为协调式轮询 / 刷新主链的标准模式
- `ConfigEntry.runtime_data` 作为 typed runtime state 的正式承载位置
- `diagnostics` + `async_redact_data` 作为支持面 / 故障排查标准出口

**Why**:
- Home Assistant 官方在 `Fetching data` 中明确把 `DataUpdateCoordinator` 作为 coordinated polling 的标准模式，并建议在可比较数据上利用 `always_update=False` 降低无效更新。
- Home Assistant 官方质量规范要求使用 `ConfigEntry.runtime_data` 存储 runtime data，并与 strict typing 配合。
- diagnostics 文档要求敏感信息脱敏，且 diagnostics 是一等支持面，不应由 ad-hoc 日志替代。

### 2. Python 类型与轻量建模标准

**Use**:
- `@dataclass(slots=True)` / frozen dataclass：运行时状态、配置快照、session state、telemetry context
- `TypedDict`：canonical payload / contract shape
- `Protocol`：边界协作者接口，但仅作为静态协定，不在热路径滥用 runtime protocol checks

**Why**:
- Python 官方文档表明 `TypedDict` 适合描述 dict-like typed contracts，运行时仍保持轻量 dict 形态。
- `Protocol` 提供结构化静态子类型；但 Python 官方也提醒 runtime-checkable protocol 的 `isinstance()` 在性能敏感路径可能偏慢。
- `dataclass` 提供轻量、透明、无框架成本的数据承载方式，适合本项目这种显式架构。

### 3. aiohttp 标准客户端能力

**Use**:
- 重用长期存活的 `aiohttp.ClientSession`
- 用 `TraceConfig` 做请求级观测钩子
- 若使用 middlewares，必须保持单一职责、顺序明确、循环有界

**Why**:
- aiohttp 官方明确建议不要按请求创建 session，而应复用 persistent session 以利用连接池。
- aiohttp 官方提供 `TraceConfig` 作为请求开始 / 结束 / 异常等观测入口。
- aiohttp middleware cookbook 明确指出：middleware 应单一职责，顺序重要，重试必须有界，并避免内部递归。

## Architecture Patterns

### 1. Formal Facade as the Only End-State Root

**Recommended pattern**:
- 绝对终态应为 `LiproProtocolFacade` 作为唯一正式 protocol-plane root
- `LiproRestFacade` 与 `LiproMqttFacade` 是其下属子门面
- `LiproClient` 不属于终态架构
- 若迁移期确有需要，`LiproClient` 只能短期存在为 compatibility shell / delegation

**Reasoning**:
- 终态必须让 formal root 与真实职责一致；历史 public name 不能继续定义内部架构。

### 2. Explicit Protocol Execution Pipeline

**Recommended pipeline**:

```text
LiproProtocolFacade
    ├── LiproRestFacade
    ├── LiproMqttFacade
    ├── RestSessionState
    ├── RestTransportExecutor
    │   ├── RequestSigner
    │   ├── RetryPolicy
    │   ├── RateLimitPolicy
    │   └── ResponseGuard
    ├── RestAuthRecoveryCoordinator
    ├── EndpointCollaborators
    ├── PayloadNormalizers
    └── CompatAdapters
```

**Implication**:
- transport / auth / retry / pacing 是协作对象，不是继承层级
- 端点行为按域聚合，但通过组合暴露
- canonical contract 在 protocol plane 边界完成

### 3. Contracts at the Boundary, not in the Runtime Core

**Recommended pattern**:
- protocol plane 吐出 canonical payload / DTO / rows
- runtime plane 只消费 canonical outputs
- vendor quirks、双 shape payload、legacy response 包裹都在 protocol plane 收口

**Reasoning**:
- 这能让 Phase 1 contract suite 成为真正稳定的行为护栏，也能避免 runtime / entity 被供应商 payload 绑架。

### 4. Typed Runtime Ownership

**Recommended pattern**:
- config entry 的 runtime 依赖对象用 typed `runtime_data` 管理
- façade 与其协作者组合出的 runtime root 应可被 HA setup/unload 生命周期安全接管

**Reasoning**:
- 这更符合官方 `runtime_data` 与 strict typing 方向，也更利于 unload / cleanup / diagnostics。

### 5. Observability as a Built-in Layer

**Recommended pattern**:
- 为 protocol plane 引入 request-scoped telemetry context
- 使用 `TraceConfig` 或等价轻量 hooks 记录：请求开始、结束、异常、重试、auth refresh、rate limit
- 不引入全局事件总线，只做显式 hooks

## Don't Hand-Roll

以下内容不应在本阶段“自研复杂版”重造：

1. **通用 DI 容器**
   - 当前依赖图规模不需要，显式 wiring 更清楚。

2. **全局事件总线**
   - 会模糊调用链，破坏单一正式主链。

3. **按请求创建 HTTP session**
   - aiohttp 官方已给出 persistent session 标准做法。

4. **无界重试 / 无界恢复链**
   - aiohttp cookbook 明确建议使用有界循环，避免无限重试。

5. **热路径 runtime protocol introspection**
   - `Protocol` 适合静态边界，不应在性能敏感路径大量 `isinstance()`。

6. **重量级 schema 框架先行**
   - 现阶段优先 `TypedDict + dataclass + golden fixtures + tests`；只有边界复杂度继续上升时再评估更重工具。

## Common Pitfalls

1. **把 request middleware 当成 session middleware 的补充**
   - aiohttp 官方说明 request-level middlewares 会替换 session middlewares，而不是叠加。

2. **在 middleware 中复用同一 session 发内部请求**
   - aiohttp cookbook 警告这可能导致递归；若必须这样做，要用 `middlewares=()` 或独立 session。

3. **把 compat wrappers 散落在 façade 与 endpoints 内部**
   - 这会让删除路径不清晰，最终形成第二套合法结构。

4. **让 raw vendor payload 穿透 protocol plane**
   - 会导致 runtime / domain / entities 被供应商细节污染。

5. **在 diagnostics 中暴露 token / account data**
   - Home Assistant 官方 diagnostics 文档明确要求脱敏。

6. **用未经类型化的 runtime roots 承载长期对象**
   - 与 `runtime_data` / strict typing 方向冲突，也更难在 setup/unload 中安全管理。

## Code Examples

### Example A: Public Shell + Internal Facade

```python
class LiproProtocolFacade:
    rest: LiproRestFacade
    mqtt: LiproMqttFacade
```

### Example B: Explicit Transport Executor

```python
@dataclass(slots=True)
class RestSessionState:
    access_token: str | None = None
    refresh_token: str | None = None
    user_id: str | None = None

class RestTransportExecutor:
    async def request_iot(self, path: str, body: dict[str, object]) -> dict[str, object]:
        ...
```

### Example C: Endpoint Collaborator

```python
class StatusEndpoints:
    def __init__(self, transport: RestTransportExecutor, normalize: PayloadNormalizers) -> None:
        self._transport = transport
        self._normalize = normalize

    async def query_device_status(self, device_ids: list[str]) -> list[DeviceStatusRow]:
        payload = await self._transport.request_iot("/status/query", {"deviceIds": device_ids})
        return self._normalize.device_status_rows(payload)
```

### Example D: Compat Adapter

```python
class CompatAdapters:
    def wrap_list_payload(self, rows: list[dict[str, object]]) -> dict[str, object]:
        return {"data": rows}
```

## Recommendation

### Locked Recommendation

**Phase 2 的最优实现路线应为：**

1. 明确 `LiproProtocolFacade` 是唯一正式 protocol-plane root
2. Phase 2 先完成 `LiproRestFacade`，为 Phase 2.5 的统一协议根做准备
3. 若必须兼容旧调用方，再提供短期 `LiproClient` shell，但不承载正式逻辑
4. 先把 transport / auth recovery / retry / pacing 变为显式协作者
5. 再迁移 endpoint collaborators，并在 Phase 2.5 合并 MQTT 根
6. 最后把 compat wrappers 收拢到单独 adapter 层并逐步删除

### What Makes This “Advanced”

不是“用了更多框架”，而是：

- 正式主链清晰
- 类型边界轻量而严格
- session / retry / middleware / telemetry 遵循成熟标准
- 契约测试与 diagnostics 成为正式治理面
- 所有历史残留都有 owner 和删除条件

## Confidence

- **High**: `runtime_data`、diagnostics、coordinator、persistent session、bounded retry / focused middleware 这些建议都有官方文档支撑。
- **High**: `TypedDict + dataclass + Protocol` 作为轻量边界建模组合，在当前项目复杂度下优于引入更重框架。
- **Medium**: `TraceConfig` 的具体落点（session-level vs executor-level）需在实际 Phase 2 改造时结合现有 observability 代码落位。
- **Low**: 若迁移期仍保留 `LiproClient` shell，其存在时间仅由调用方迁移节奏决定，不影响终态判断。

## Official Sources

- Home Assistant Developer Docs — Fetching data: https://developers.home-assistant.io/docs/integration_fetching_data/
- Home Assistant Developer Docs — Integration quality scale: https://developers.home-assistant.io/docs/core/integration-quality-scale/
- Home Assistant Developer Docs — Use ConfigEntry.runtime_data to store runtime data: https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/runtime-data/
- Home Assistant Developer Docs — Strict typing: https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/strict-typing/
- Home Assistant Developer Docs — Integration diagnostics: https://developers.home-assistant.io/docs/core/integration_diagnostics/
- aiohttp docs — Advanced Client Usage: https://docs.aiohttp.org/en/latest/client_advanced.html
- aiohttp docs — Client Middleware Cookbook: https://docs.aiohttp.org/en/stable/client_middleware_cookbook.html
- Python docs — typing: https://docs.python.org/3/library/typing.html
- Python docs — dataclasses: https://docs.python.org/3.12/library/dataclasses.html
