# Phase 91: Protocol/runtime decomposition and typed boundary hardening - Research

**Researched:** 2026-03-28
**Domain:** Python strict typing / Home Assistant runtime surface / protocol-boundary canonicalization
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### Runtime / Protocol formal-home strategy
- **D-01:** `custom_components/lipro/core/coordinator/runtime/command_runtime.py`、`custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py`、`custom_components/lipro/core/api/rest_facade.py`、`custom_components/lipro/core/api/request_policy.py` 继续是 formal homes；若需要拆分，只能 inward 到同 family 的 support helper / typed model，formal-home 文件保留 owner 身份。
- **D-02:** `custom_components/lipro/__init__.py`、`custom_components/lipro/control/runtime_access.py`、`custom_components/lipro/entities/base.py`、`custom_components/lipro/entities/firmware_update.py` 若被触碰，只允许做 typed projection / alias 收口；不得新增 orchestration、runtime/protocol internals 读取或第二条故事线。

### Typed boundary hardening
- **D-03:** protocol/runtime 共享 contract 优先复用现有 `core/api/types.py`、`core/command/result_policy.py` 与 `runtime_types.py`；避免在 coordinator / entity / diagnostics 层继续平行发明匿名 `dict[str, Any]` 语义。
- **D-04:** `core/protocol/boundary/schema_registry.py` 与 `core/protocol/boundary/result.py` 优先改为协变/erased-object registry，而不是继续把 `Any` 作为 decoder family 总线类型。
- **D-05:** `core/protocol/boundary/rest_decoder_support.py` 必须把 raw payload 处理收敛到 `object` + narrow mapping helpers；canonical payload 仍通过 boundary family 返回，不允许 raw vendor mapping 向 runtime/entity 继续穿透。
- **D-06:** `core/command/trace.py` 与 command-runtime telemetry 必须共享单一 trace contract；不要在 trace helpers、runtime telemetry、tests 之间维持多套 loosely-typed 字典故事。

### Verification / no-growth policy
- **D-07:** Phase 91 必须新增 focused no-growth guard：对上述 typed-boundary 文件的 `Any` / broad dynamic 面积做显式预算，漂移时第一时间失败。
- **D-08:** Phase 91 的验证优先 focused pytest + `uv run mypy` + `uv run ruff check .` + `uv run python scripts/check_file_matrix.py --check`；同时同步 baseline/review/docs/current-route truth，确保路线清晰推进到 Phase 92。

### Claude's Discretion
- 在不改变 ownership 的前提下，自主决定最小而彻底的 typed helper 拆分点。
- 自主选择最小充分的 focused tests / meta guards 组合。
- 自主决定是否把局部 alias 收敛到 shared type home，只要不引入第二 root 或新 public surface。

### Deferred Ideas (OUT OF SCOPE)
- `control/redaction.py` 与 `core/anonymous_share/sanitize.py` 的统一 redaction registry → `Phase 92`。
- diagnostics/share/exporters 的 redaction contract 收口与 test topicization → `Phase 92`。
- assurance topicization、microbenchmark / hotspot budget 与更广泛 quality freeze → `Phase 93`。
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| `ARC-24` | `custom_components/lipro/__init__.py`、`custom_components/lipro/control/runtime_access.py`、`custom_components/lipro/entities/base.py`、`custom_components/lipro/entities/firmware_update.py` 必须继续保持 thin adapter / projection / typed access 角色，避免重新吸附 orchestration。 | `## Current Hotspots`、`## Architecture Patterns`、`## Risks`、`## Recommended Plan Split` 明确把这些文件限定为 protected thin shells，仅允许类型别名/投影收口。 |
| `TYP-23` | `custom_components/lipro/runtime_types.py`、`custom_components/lipro/core/coordinator/types.py`、`custom_components/lipro/core/protocol/boundary/rest_decoder_support.py`、`custom_components/lipro/core/protocol/boundary/schema_registry.py`、`custom_components/lipro/core/command/trace.py` 的 `Any` / dynamic payload surface 必须继续缩减，并补 no-growth guard。 | `## Current Hotspots`、`## Concrete Implementation Approach`、`## Code Examples`、`## Validation Architecture` 给出具体收缩路径、 guard 方案与验证矩阵。 |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- `AGENTS.md` 仍是仓库唯一 canonical contract；若与 `CLAUDE.md` 冲突，以 `AGENTS.md` 为准。
- 研究/规划必须优先服从既定读取顺序：`AGENTS.md` → `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` → `.planning/*` → `docs/developer_architecture.md`。
- 不新增第二套 truth source；`CLAUDE.md` 只提供兼容入口，不覆盖 `.planning/*`、`docs/*` 或代码真源。
- 不再创建或依赖 `agent.md`。
- 当前里程碑、phase、推荐下一步以 `.planning/STATE.md` 为准。

## Summary

Phase 90 已把 five hotspots 与 four protected thin shells 冻结成 current truth，因此 Phase 91 的最优实施方式不是“再争一次 formal home”，而是把真正的 typed-boundary debt 收回到几个 hub 类型文件，然后让 `command_runtime.py`、`mqtt_runtime.py`、`rest_decoder_support.py` 等正式 owner 消费这些收紧后的契约。现有代码已经提供了可复用真源：`custom_components/lipro/core/api/types.py`、`custom_components/lipro/core/command/result_policy.py`、`custom_components/lipro/core/telemetry/models.py` 与 `custom_components/lipro/control/runtime_access_support_telemetry.py`。这意味着本 phase 可以做“类型真源收敛 + 局部 inward split + no-growth guard”，不需要发明新的 root。

本织师已验证当前基线健康：目标文件子集的 `uv run mypy` 通过，聚焦 suite `44 passed`，`uv run python scripts/check_file_matrix.py --check` 通过，范围化 `ruff check` 通过。这说明 Phase 91 不需要先修遗留故障；应直接围绕 typed contract 开刀。真正需要规划的是 blast radius：`core/coordinator/types.py` 与 `runtime_types.py` 是枢纽类型 home，任何 alias 收紧都会向 runtime/device/mqtt/status/service 流经十余个文件；因此计划必须先改 hub 类型，再改 formal homes，最后补 meta guard 与治理文档。

**Primary recommendation:** 以 `object` + narrow helper 处理 raw payload、以 `TypedDict` / shared payload alias 表达 canonical contract、以新的 `tests/meta/test_phase91_typed_boundary_guards.py` 冻结 `Any` 预算，并把 trace / telemetry contract 收敛到单一真源。

## Current Hotspots

| File | Hotspot finding | Why it matters | Confidence |
|------|-----------------|----------------|------------|
| `custom_components/lipro/core/coordinator/runtime/command_runtime.py` | 471 行，仍同时承担命令编排、失败摘要、trace 缓冲、metrics 输出；匹配到 5 条动态类型热点。 | `CommandTrace` 和运行指标从这里辐射到 sender/builder/service/test，多点同时引用，最容易产生 contract drift。 | HIGH |
| `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py` | 420 行，连接/断线通知、重连、去重、message apply、metrics 混在一个 formal home；匹配到 5 条动态类型热点。 | 这是 formal owner，不能外移所有逻辑，但很适合 inward split 纯 typed helper 或 metrics/event model。 | HIGH |
| `custom_components/lipro/core/protocol/boundary/rest_decoder_support.py` | 366 行，`_normalize_properties_payload()`、identity/status row helper 仍靠 `Mapping[str, Any]` + `cast` 驱动；匹配到 7 条动态类型热点。 | 这是 raw vendor payload 进入 canonical contract 前的最后安全边界；这里不收紧，runtime/entity 迟早会再次吃到宽类型。 | HIGH |
| `custom_components/lipro/core/coordinator/types.py` | 234 行，是 runtime hub 类型 home，但 `PropertyValue`、`CommandTrace`、`RuntimeMetrics` 仍保留广义 `Any`。 | 该文件被 runtime/device/status/mqtt/outlet 等多处引用，任何收口都必须先从这里统一。 | HIGH |
| `custom_components/lipro/runtime_types.py` | outward runtime protocol 大体健康，但 `async_get_city()` / `async_query_user_cloud()` 仍返回 `dict[str, object]`，`build_snapshot()` 仍是 `Mapping[str, Any]`。 | 协议层真实返回已经是 `JsonObject`，运行时表面仍比真实 contract 更宽，导致外层只能跟着放宽。 | HIGH |
| `custom_components/lipro/core/coordinator/services/telemetry_service.py` | 165 行，connect/group signal event 与 snapshot 仍是 `dict[str, Any]` / `list[dict[str, Any]]`；匹配到 5 条动态类型热点。 | `core/telemetry/models.py` 与 `control/runtime_access_support_telemetry.py` 已存在 JSON-safe contract，但 runtime 侧尚未对齐。 | HIGH |
| `custom_components/lipro/core/protocol/boundary/schema_registry.py` + `result.py` | registry 仍以 `BoundaryDecoder[Any]` 储存 heterogeneous decoder，`BoundaryDecodeResult` 默认不协变。 | 这是 protocol boundary 的类型总线；若继续用 `Any`，上层 wrappers 永远只能靠 cast 收尾。 | HIGH |
| `custom_components/lipro/__init__.py`、`custom_components/lipro/control/runtime_access.py`、`custom_components/lipro/entities/base.py`、`custom_components/lipro/entities/firmware_update.py` | 当前守卫已把它们冻结为 protected thin shells；本轮无需主动加逻辑。 | `Phase 89/90` 守卫和聚焦测试已证明这些 outward shells 现在是正确形态；本 phase 只能做 alias/projection 级配套收口。 | HIGH |

**Measured baseline:** 目标 11 个源码文件共计 `2680` 行；`rg` 命中的 `Any` / broad dynamic line 约 `49` 行，主要集中在 `rest_decoder_support.py`、`core/coordinator/types.py`、`command_runtime.py`、`mqtt_runtime.py`、`telemetry_service.py`、`confirmation.py`、`trace.py`、`schema_registry.py`。

## Concrete Implementation Approach

| Step | Primary files | Concrete action | Expected effect |
|------|---------------|-----------------|-----------------|
| 1 | `custom_components/lipro/core/protocol/boundary/result.py`, `custom_components/lipro/core/protocol/boundary/schema_registry.py` | 把 `BoundaryDecodeResult` / `BoundaryDecoder` 的类型参数改为协变；registry 以 `BoundaryDecoder[object]` 做 erased storage，而不是 `BoundaryDecoder[Any]`。 | 保留 heterogeneous decoder registry，同时让具体 wrapper 保持精准返回类型；减少 `Any` 在 protocol 总线上的传播。 |
| 2 | `custom_components/lipro/core/protocol/boundary/rest_decoder_support.py` | 把 raw payload helper 全面收口到 `object` + `Mapping[str, object]` / `Sequence[object]` narrowing；只在 canonical return 处保留必要 cast。 | 把动态输入隔离在 boundary helper 内，不再把 `Any` 带到 runtime/domain。 |
| 3 | `custom_components/lipro/core/coordinator/types.py`, `custom_components/lipro/runtime_types.py`, 相邻 `custom_components/lipro/core/coordinator/services/protocol_service.py` | 优先复用 `core/api/types.py` 的 `JsonValue` / `JsonObject` / `DevicePropertyMap`，以及 `core/telemetry/models.py` 的 `TelemetrySourcePayload`；让 `PropertyValue`、`CommandTrace`、`build_snapshot()`、`async_get_city()`、`async_query_user_cloud()` 讲同一条类型故事。 | 先收 hub 类型，再推导 formal homes，降低改动涟漪与重复 alias。 |
| 4 | `custom_components/lipro/core/command/trace.py`, `custom_components/lipro/core/coordinator/runtime/command_runtime.py`, `custom_components/lipro/core/coordinator/runtime/command/confirmation.py`, `custom_components/lipro/core/coordinator/services/telemetry_service.py`, `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py` | 把 trace/metrics/event payload 统一到单一 shared contract：trace 优先复用 `core/command/result_policy.py`，runtime telemetry 优先复用 `TelemetrySourcePayload` 或新的 `TypedDict(total=False)`。仅当 formal home 仍过重时，向同 family 提取 support-only typed helper。 | 减少 `dict[str, Any]` 在 command/mqtt/telemetry 之间来回复制，且不改变 formal-home ownership。 |
| 5 | `tests/core/api/test_protocol_contract_boundary_decoders.py`, `tests/core/coordinator/runtime/test_runtime_telemetry_methods.py`, `tests/core/coordinator/runtime/test_command_runtime_orchestration.py`, `tests/core/coordinator/services/test_telemetry_service.py`, 新增 `tests/meta/test_phase91_typed_boundary_guards.py` | 现有 focused suite 继续验证行为；新增 meta guard 显式冻结 Phase 91 的 `_TYPE_GUARD_TARGETS`、`_ANY_BUDGET`、`type: ignore=0` 与必要 broad-dynamic marker。 | 把“这次缩掉了哪些 `Any`”从口头承诺变成 machine-checkable truth。 |
| 6 | `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/reviews/{FILE_MATRIX.md,RESIDUAL_LEDGER.md}`, `docs/developer_architecture.md`, 视 public type surface 变化同步 `.planning/baseline/{PUBLIC_SURFACES.md,DEPENDENCY_MATRIX.md}` | 同步 formal-home ownership 不变、typed-boundary no-growth policy、新测试入口与 route truth。 | 防止下一轮 phase 把本次收口讲成“只是局部代码整理”。 |

### 建议执行顺序

1. **先改 hub 类型 home**：`core/coordinator/types.py`、`runtime_types.py`、`result.py`、`schema_registry.py`。
2. **再改 formal homes**：`rest_decoder_support.py`、`trace.py`、`command_runtime.py`、`confirmation.py`、`telemetry_service.py`、`mqtt_runtime.py`。
3. **最后收 guard 与 docs**：meta tests、focused unit tests、`VERIFICATION_MATRIX` / `FILE_MATRIX` / `RESIDUAL_LEDGER` / `developer_architecture.md`。

### 邻接波纹面（需要纳入计划，但不是主战场）

- `custom_components/lipro/core/coordinator/services/protocol_service.py`：若 `runtime_types.py` 把 `async_get_city()` / `async_query_user_cloud()` 收紧为 `JsonObject`，这里必须同步收紧。
- `tests/conftest.py`、`tests/services/test_services_diagnostics.py`、`tests/core/test_init_service_handlers_debug_queries.py`：测试 double 目前也在使用宽返回类型；需要跟着 typed surface 一起改。
- `custom_components/lipro/control/runtime_access_support_telemetry.py`：已有 telemetry JSON-safe coercion helper，可作为 runtime telemetry contract 的目标形态，而不是再造第二套 sanitizer。

## Standard Stack

### Core

| Library / Runtime | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python typing stdlib | Python `>=3.14.2` | `TypedDict`、`Protocol`、`TypeVar`、`Mapping` 等静态契约 | 当前仓库已启用严格 mypy；Phase 91 不需要新依赖，只需把已有 typing 能力用到 boundary/runtime 枢纽。 |
| Home Assistant | `2026.3.1` | typed `ConfigEntry.runtime_data` 与 integration runtime contract | 官方质量规则要求 runtime-data typed 且一致使用；本仓库已基于该模式演进。 |
| `mypy` | `1.19.1` | strict typing gate | 当前环境已可运行，且项目 `strict = true`；是本 phase 的核心回归门。 |

### Supporting

| Library / Tool | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest` | `9.0.0` | focused regression / topicized suites | 每次修改 protocol/runtime contract 后先跑最小回归矩阵。 |
| `ruff` | `0.15.x` | lint / import / style gate | 每个 plan 收尾时跑 touched scope；phase gate 跑全仓。 |
| `uv` | `0.10.9` | 统一 Python 执行入口 | 本仓所有 Python 命令必须走 `uv run ...`。 |
| `node` | `20.19.2` | GSD route / phase metadata tooling | phase 规划与治理 route 校验需要。 |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `object` + narrowing | `Any` | `Any` 更省事，但会关闭类型检查并向调用链扩散；只应保留在极少数 sanctioned seam。 |
| `TypedDict` / shared alias | 匿名 `dict[str, object]` / `dict[str, Any]` | 匿名 dict 写起来快，但 schema 无法 machine-check，也不利于 tests / telemetry 共用 contract。 |
| covariant erased registry | family-specific ad-hoc registry / cast-heavy registry | ad-hoc registry 容易复制故事线；协变 erased registry 更贴合当前 boundary architecture。 |

**Recommended bootstrap:**

```bash
uv sync --extra dev
```

**Version verification:**

- Python floor：`pyproject.toml` 声明 `requires-python = ">=3.14.2"`
- Home Assistant：已通过 `uv run python -c "from importlib.metadata import version; print(version('homeassistant'))"` 验证为 `2026.3.1`
- `mypy 1.19.1`、`pytest 9.0.0`、`uv 0.10.9`、`node 20.19.2`、`ruff 0.15.x` 均在当前环境可用

## Architecture Patterns

### Recommended Project Structure

```text
custom_components/lipro/
├── core/
│   ├── protocol/boundary/         # raw payload -> canonical contract
│   ├── coordinator/runtime/       # command/mqtt formal homes
│   ├── coordinator/services/      # runtime telemetry / public services
│   ├── command/                   # shared command result / trace policy
│   └── telemetry/                 # exporter JSON-safe contract truth
├── control/                       # protected thin runtime access / telemetry adapters
├── entities/                      # protected thin projections only
└── runtime_types.py               # outward runtime protocol home

tests/
├── core/api/                      # boundary decoder / protocol contract suites
├── core/coordinator/runtime/      # runtime orchestration / telemetry suites
├── core/coordinator/services/     # telemetry-service focused tests
└── meta/                          # phase no-growth / governance guards
```

### Pattern 1: Hub Types First, Formal Homes Second
**What:** 先收紧 `runtime_types.py`、`core/coordinator/types.py`、`boundary/result.py`、`boundary/schema_registry.py` 这些类型枢纽，再修改 `command_runtime.py` / `mqtt_runtime.py` / `rest_decoder_support.py` 等 formal homes。
**When to use:** 某个宽类型 alias 被 3 个以上 runtime/protocol consumer 共用时。
**Example:**

```python
# Source: https://mypy.readthedocs.io/en/stable/protocols.html
from typing import Protocol, TypeVar

CanonicalT_co = TypeVar("CanonicalT_co", covariant=True)


class BoundaryDecoder(Protocol[CanonicalT_co]):
    def decode(self, payload: object) -> BoundaryDecodeResult[CanonicalT_co]: ...
```

### Pattern 2: Raw Input Uses `object`, Canonical Output Uses `TypedDict`
**What:** raw vendor payload 入口统一收成 `object` / `Mapping[str, object]`；只有 canonical contract 才使用 `TypedDict` / shared alias。
**When to use:** decoder / trace / telemetry builder 需要先做 runtime narrowing，再暴露稳定 schema 时。
**Example:**

```python
# Source: https://mypy.readthedocs.io/en/stable/dynamic_typing.html
from collections.abc import Mapping

type RawObjectMap = Mapping[str, object]


def normalize_payload(payload: object) -> RawObjectMap | None:
    if isinstance(payload, Mapping):
        return payload
    return None
```

### Pattern 3: Single Trace / Telemetry Contract
**What:** `core/command/result_policy.py` 与 `core/telemetry/models.py` 是共享 trace / telemetry 语言；runtime formal homes 只负责填充，不再各自定义 `dict[str, Any]` 版本。
**When to use:** command failure trace、MQTT metrics、runtime telemetry snapshot 会被 tests / services / diagnostics 共用时。
**Example:**

```python
# Source: https://mypy.readthedocs.io/en/stable/typed_dict.html
from typing import TypedDict


class ConnectStateEvent(TypedDict):
    device_serial: str
    timestamp: float
    is_online: bool


class RuntimeTelemetrySnapshot(TypedDict, total=False):
    device_count: int
    polling_interval_seconds: int | None
    mqtt: dict[str, object]
    signals: dict[str, object]
```

### Pattern 4: Protected Thin Shells Stay Outside the Blast Radius
**What:** `__init__.py`、`control/runtime_access.py`、`entities/base.py`、`entities/firmware_update.py` 只接受 alias/projection 级配套修改。
**When to use:** outward adapter 只是消费 runtime public surface，而不是 formal owner 时。

### Anti-Patterns to Avoid
- **在 thin shell 里补 orchestration：** 这会直接违反 `ARC-24` 与 `Phase 89/90` 冻结结果。
- **把 raw vendor mapping 继续往 runtime/entity 透传：** 一旦 decoder helper 没有收紧，typed boundary hardening 就会失败。
- **为 trace / telemetry 再造第三套字典协议：** 项目已经有 `TracePayload` 与 `TelemetrySourcePayload`，继续复制只会制造 drift。
- **把 Phase 92 redaction 工作提前塞进 Phase 91：** 本 phase 只处理 typed boundary；脱敏 contract 是下一 phase。

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| heterogeneous decoder registry | 新的 family-specific registry 或任意 cast 总线 | `BoundaryDecoderRegistry` + `BoundaryDecoderKey` + 协变 generic | 保持单一 protocol-boundary inventory truth，并让 wrapper 保持精准返回类型。 |
| runtime telemetry JSON 化 | control-plane 再写一套 ad-hoc sanitizer | `core/telemetry/models.py` + `control/runtime_access_support_telemetry.py` | 现有 exporter/runtime-access 已证明此 contract 可用。 |
| command trace schema | runtime / tests / services 各维护一份 trace dict | `core/command/result_policy.py` / `core/command/trace.py` 的单一 shared contract | 避免同名不同义的 trace key 持续漂移。 |
| runtime locator | 新的 coordinator internals backdoor | `control/runtime_access.py` | thin-shell guard 已冻结，不应重开读取旁路。 |

**Key insight:** Phase 91 的关键不是“造更多 helper”，而是把已有类型真源真正变成唯一语言；只有 formal home 仍过厚时，才向同 family inward split 纯 typed helper。

## Risks

| Risk | Why Phase 91-specific | Mitigation |
|------|-----------------------|------------|
| hub alias 改动波及面过大 | `PropertyValue`、`CommandTrace`、`build_snapshot()` 被多处导入 | 先改类型 home，再用 targeted mypy + import-site suites 验证，不要反向从 consumer 倒推。 |
| 过早把 `get_city` / `query_user_cloud` 收成过窄 schema | 上游返回已是 `JsonObject`，但下游 service/test doubles 可能仍当作宽 dict 使用 | 第一轮先收成 `JsonObject`，不要直接发明更窄 `TypedDict`；若需要，再基于 fixture 新增 named schema。 |
| protocol registry 协变化后出现 runtime 心智负担 | `BoundaryDecoder[Any]` 改成 erased-object 后，调用者需要明确 wrapper owner | 保持 registry 只在 boundary family 内部暴露，具体 decoder 仍通过 `decode_*_payload()` helper 出口。 |
| trace/telemetry 收口时 scope 漫出到 redaction | trace key 与 telemetry key 很容易顺手改名或加敏感字段 | 只做 typing/shape 收口，不改 redaction 规则；未知 secret-like 字段统一留给 Phase 92。 |
| formal-home inward split 变成“偷偷换 root” | 热点文件很大，容易借拆分之名把 ownership 搬走 | 新 helper 只能是 sibling/support family；`FILE_MATRIX` / `developer_architecture` 必须明确 owner 不变。 |

## Common Pitfalls

### Pitfall 1: `Any` 从 Hub Alias 一路扩散
**What goes wrong:** 只在 formal home 局部把 `Any` 改掉，但 `core/coordinator/types.py` / `runtime_types.py` 仍维持宽 alias，导致下游继续跟着宽化。
**Why it happens:** 改动从 consumer 开始，而不是从 shared type home 开始。
**How to avoid:** 先收紧 hub alias，再逐个修 formal home；每步都跑 targeted mypy。
**Warning signs:** 一个文件改完后，需要在 4 个以上 consumer 里补 `cast()` 才能通过检查。

### Pitfall 2: 把 Raw Payload 当作 Canonical Contract
**What goes wrong:** decoder helper 里直接把 `Mapping[str, Any]` 向上传递，runtime/entity 再自己猜 key。
**Why it happens:** 图省事，把“先判断 shape”与“已经 canonicalized”混成一层。
**How to avoid:** raw payload 一律先收成 `object` / `Mapping[str, object]`，只有 canonical output 才使用 `TypedDict`。
**Warning signs:** `dict[str, Any]` 出现在 boundary family 以外，或者 tests 需要知道 vendor key 名。

### Pitfall 3: Protocol 属性不小心触发不变性问题
**What goes wrong:** 在 `Protocol` 中声明可写属性，结果更窄实现类型无法赋值给更宽 protocol。
**Why it happens:** Protocol 默认会对可变属性做不变性检查。
**How to avoid:** 若协议只需要读，优先用方法或 `@property` 暴露 read-only surface。
**Warning signs:** mypy 报告 implementation 与 protocol “member type conflicts”，尤其是 attribute 类型从 `object` 到具体类型的收窄场景。

### Pitfall 4: Telemetry Snapshot 与 Exporter 讲两种语言
**What goes wrong:** runtime telemetry 继续返回 `dict[str, Any]`，而 control/exporter 再做第二次 JSON-safe 规整。
**Why it happens:** runtime/service 与 control/exporter 各自演进，没有共用 `TelemetrySourcePayload`。
**How to avoid:** 以 `core/telemetry/models.py` 为 shared payload 目标；`control/runtime_access_support_telemetry.py` 只做 compatibility narrowing，不再承担事实真源。
**Warning signs:** 同一 snapshot key 在 `telemetry_service.py` 和 exporter tests 中有两套命名/类型解释。

### Pitfall 5: 守卫只管“有没有文件”，不管“有没有变宽”
**What goes wrong:** 只保留 Phase 89/90 的 shell/home guard，却没有新增 typed-budget guard，导致 `Any` 回流时 CI 不报错。
**Why it happens:** 认为 mypy 足够，但 `Any` 往往让 mypy 静默通过。
**How to avoid:** 新增 `tests/meta/test_phase91_typed_boundary_guards.py`，显式记录 `_ANY_BUDGET` / `type: ignore=0` / broad-dynamic marker。
**Warning signs:** 新增 `Any` 后 unit tests 仍全绿，只有人工 code review 能看出来。

## Code Examples

Verified patterns from official sources:

### 协变 decoder registry
```python
# Source: https://mypy.readthedocs.io/en/stable/protocols.html
from typing import Protocol, TypeVar

CanonicalT_co = TypeVar("CanonicalT_co", covariant=True)


class BoundaryDecoder(Protocol[CanonicalT_co]):
    @property
    def authority(self) -> str: ...

    def decode(self, payload: object) -> BoundaryDecodeResult[CanonicalT_co]: ...
```

### `object` 先收口，再窄化成映射
```python
# Source: https://mypy.readthedocs.io/en/stable/dynamic_typing.html
from collections.abc import Mapping


def as_object_mapping(value: object) -> Mapping[str, object] | None:
    if isinstance(value, Mapping):
        return value
    return None
```

### 用 `TypedDict` 固定 event / snapshot schema
```python
# Source: https://mypy.readthedocs.io/en/stable/typed_dict.html
from typing import TypedDict


class ConnectStateEvent(TypedDict):
    device_serial: str
    timestamp: float
    is_online: bool


class CommandRuntimeMetrics(TypedDict, total=False):
    debug_enabled: bool
    trace_count: int
    last_failure: dict[str, object] | None
    confirmation: dict[str, object]
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| raw/dynamic 值默认用 `Any` | 对未知输入优先用 `object`，再做类型收窄 | 现行 mypy 官方文档（当前 stable） | `Any` 不再静默关闭检查，类型债更早暴露。 |
| runtime-data / outward surface 只求“能存取” | Home Assistant 官方要求 typed `runtime_data` 并全程一致使用 typed `ConfigEntry` | 当前 Home Assistant quality rule | `__init__.py` / runtime glue 更适合保持 thin typed adapter，不再长回 orchestrator。 |
| trace / telemetry / tests 各用一份 dict 约定 | 以 shared contract 统一 key 语义，再用 focused tests + guard 冻结 | 项目自 `Phase 64` 持续演进，`Phase 89/90` 已完成 ownership freeze | 这次可以把类型与 formal-home freeze 合并收口，而不是继续靠人为约定。 |

**Deprecated/outdated:**
- 把 `dict[str, Any]` 当默认边界类型：对本 phase 来说已不再是可接受默认值。
- 在 runtime/control/entity 层复述 vendor payload key：违反 north-star 的 boundary normalization 原则。

## Open Questions

1. **`get_city` / `query_user_cloud` 最终要不要升级成 named `TypedDict`？**
   - What we know: protocol façade / rest port 已返回 `JsonObject`；runtime protocol surface 仍放宽为 `dict[str, object]`。
   - What's unclear: 现有服务/测试 double 是否依赖“任意可变 dict”语义。
   - Recommendation: Phase 91 先收口到 `JsonObject`，不要直接发明更窄 `TypedDict`；若后续 fixture 证明 schema 稳定，再在后续小计划中提升。

2. **`CommandTrace` 的正式 home 应该落在 `core/command/result_policy.py` 还是 `core/command/trace.py`？**
   - What we know: `TracePayload` 已在 `result_policy.py`，`core/coordinator/types.py` 又定义了 `CommandTrace = dict[str, Any]`，当前存在重复。
   - What's unclear: planner 是否希望由 command domain owning alias，再让 coordinator 层 re-export。
   - Recommendation: 由 command domain 统一定义 shared trace alias / `TypedDict`，coordinator/types 仅 re-export 或引用，不再二次发明。

3. **`CoordinatorTelemetryService.build_snapshot()` 的公开返回型别要多精确？**
   - What we know: downstream exporter/runtime-access 已能把它规整为 `TelemetrySourcePayload`。
   - What's unclear: 直接返回 `TelemetrySourcePayload` 是否会让测试断言丢失结构可读性。
   - Recommendation: 内部使用 `TypedDict(total=False)` 表达结构，public edge 返回 JSON-safe mapping；测试继续断言具体 key，而不是依赖 `Any`。

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | 全部 Python 命令与测试 | ✓ | `0.10.9` | — |
| `python` (via `uv`) | typing / tests / scripts | ✓ | `3.14.x` runtime from project env | — |
| `mypy` | strict typing gate | ✓ | `1.19.1` | 无；这是 Phase 91 的硬门禁 |
| `ruff` | lint / import / no-regression | ✓ | `0.15.x` | 无；至少需跑 touched scope |
| `pytest` | focused regression suites | ✓ | `9.0.0` | 无；本 phase 明确依赖 topicized suites |
| Home Assistant dev dependency | integration runtime / component tests | ✓ | `2026.3.1` | 无；相关 tests 已在当前环境可跑 |
| `node` | GSD route / phase tooling | ✓ | `20.19.2` | — |

**Missing dependencies with no fallback:**
- None

**Missing dependencies with fallback:**
- None

## Recommended Plan Split

### `91-01`：收紧 protocol/runtime hub 类型真源
- **Scope:** `runtime_types.py`、`core/coordinator/types.py`、`boundary/result.py`、`boundary/schema_registry.py`、相邻 `protocol_service.py`
- **Goal:** 先把 `Any` / wide alias 从 hub type homes 移除或分类为明确预算
- **Why first:** 这些是 blast radius 最大的文件；先收口可以减少 formal home 内部反复改签名
- **Done when:** protocol/runtime outward signatures 已改用 `JsonObject` / `JsonValue` / `TelemetrySourcePayload` / covariant generic story

### `91-02`：formal homes 内部 trace / telemetry / decoder 收口
- **Scope:** `rest_decoder_support.py`、`trace.py`、`command_runtime.py`、`confirmation.py`、`telemetry_service.py`、`mqtt_runtime.py`
- **Goal:** 用 shared contract 替代局部 `dict[str, Any]`，必要时只做同 family inward split
- **Why second:** formal homes 必须消费第 1 步输出的 hub types；反过来做只会制造过渡 alias
- **Done when:** `TracePayload` / runtime metrics / boundary helper 不再各讲各话，且 owner 身份保持不变

### `91-03`：guard、focused tests、governance freeze
- **Scope:** 新增 `tests/meta/test_phase91_typed_boundary_guards.py`，扩展 focused suites，更新 `.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/reviews/{FILE_MATRIX.md,RESIDUAL_LEDGER.md}`、`docs/developer_architecture.md`
- **Goal:** 把本轮收口冻结为 machine-checkable truth，并把 follow-up route 明确推到 Phase 92
- **Why third:** 没有前两步的稳定 contract，就无法定义 honest 的 `_ANY_BUDGET`
- **Done when:** meta guard、focused suites、route docs 同步承认新的 typed-boundary baseline

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest 9.0.0` + `mypy 1.19.1` + `ruff 0.15.x` |
| Config file | `pyproject.toml` |
| Quick run command | `uv run pytest -q tests/core/api/test_protocol_contract_boundary_decoders.py tests/core/coordinator/runtime/test_runtime_telemetry_methods.py tests/core/coordinator/runtime/test_command_runtime_orchestration.py tests/core/coordinator/services/test_telemetry_service.py tests/meta/test_phase89_runtime_boundary_guards.py tests/meta/test_phase90_hotspot_map_guards.py` |
| Full suite command | `uv run pytest -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| `ARC-24` | protected thin shells 不回流 orchestration | meta | `uv run pytest -q tests/meta/test_phase89_runtime_boundary_guards.py tests/meta/test_phase90_hotspot_map_guards.py tests/meta/test_phase91_typed_boundary_guards.py` | ❌ Wave 0（需新增 Phase 91 guard） |
| `TYP-23` | protocol boundary decoders 维持 canonical contract 且不再增长 `Any` | unit + static | `uv run pytest -q tests/core/api/test_protocol_contract_boundary_decoders.py && uv run mypy custom_components/lipro/core/protocol/boundary/rest_decoder_support.py custom_components/lipro/core/protocol/boundary/schema_registry.py custom_components/lipro/core/protocol/boundary/result.py` | ✅（existing unit） / ❌（new meta guard） |
| `TYP-23` | runtime trace / telemetry / command orchestration 共享单一 typed contract | unit + static | `uv run pytest -q tests/core/coordinator/runtime/test_runtime_telemetry_methods.py tests/core/coordinator/runtime/test_command_runtime_orchestration.py tests/core/coordinator/services/test_telemetry_service.py tests/core/coordinator/runtime/test_mqtt_runtime_support.py && uv run mypy custom_components/lipro/runtime_types.py custom_components/lipro/core/coordinator/types.py custom_components/lipro/core/command/trace.py custom_components/lipro/core/coordinator/runtime/command_runtime.py custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py custom_components/lipro/core/coordinator/runtime/command/confirmation.py custom_components/lipro/core/coordinator/services/telemetry_service.py` | ✅ |

### Sampling Rate
- **Per task commit:** 运行受影响 topical suites + 对应 mypy 子集 + touched scope `ruff check`
- **Per wave merge:** `uv run python scripts/check_file_matrix.py --check` + meta guard 子集
- **Phase gate:** Quick run matrix + `uv run mypy` + `uv run ruff check .` + `uv run pytest -q tests/meta`

### Wave 0 Gaps
- [ ] `tests/meta/test_phase91_typed_boundary_guards.py` — 显式冻结 Phase 91 `_TYPE_GUARD_TARGETS` / `_ANY_BUDGET` / `type: ignore=0`
- [ ] `tests/core/coordinator/services/test_telemetry_service.py` — 补一条“typed snapshot key set / signal event TypedDict”断言，避免 snapshot 又退回匿名 dict 叙事
- [ ] `tests/conftest.py` / diagnostics-service related doubles — 跟随 `JsonObject` / typed runtime surface 调整 test double 返回型别

**Current baseline evidence:**
- `uv run pytest -q tests/core/api/test_protocol_contract_boundary_decoders.py tests/core/coordinator/runtime/test_runtime_telemetry_methods.py tests/core/coordinator/runtime/test_command_runtime_orchestration.py tests/meta/test_phase89_runtime_boundary_guards.py tests/meta/test_phase90_hotspot_map_guards.py` → `44 passed`
- `uv run mypy <11 target source files>` → `Success: no issues found`
- `uv run python scripts/check_file_matrix.py --check` → `All checks passed!`

## Sources

### Primary (HIGH confidence)
- Repository governance + code truth:
  - `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
  - `.planning/ROADMAP.md`
  - `.planning/REQUIREMENTS.md`
  - `.planning/phases/91-protocol-runtime-decomposition-and-typed-boundary-hardening/91-CONTEXT.md`
  - `.planning/phases/90-hotspot-routing-freeze-and-formal-home-decomposition-map/90-VERIFICATION.md`
  - `custom_components/lipro/runtime_types.py`
  - `custom_components/lipro/core/coordinator/types.py`
  - `custom_components/lipro/core/protocol/boundary/rest_decoder_support.py`
  - `custom_components/lipro/core/protocol/boundary/schema_registry.py`
  - `custom_components/lipro/core/protocol/boundary/result.py`
  - `custom_components/lipro/core/command/trace.py`
  - `custom_components/lipro/core/coordinator/runtime/command_runtime.py`
  - `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py`
  - `custom_components/lipro/core/coordinator/runtime/command/confirmation.py`
  - `custom_components/lipro/core/coordinator/services/telemetry_service.py`
- Context7: `/python/mypy` — `Any` vs `object`、`TypedDict`、`Protocol` / generics guidance
- Official docs:
  - https://mypy.readthedocs.io/en/stable/dynamic_typing.html
  - https://mypy.readthedocs.io/en/stable/typed_dict.html
  - https://mypy.readthedocs.io/en/stable/protocols.html
  - https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/runtime-data
  - https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/strict-typing

### Secondary (MEDIUM confidence)
- None

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - `pyproject.toml`、环境探针、Home Assistant / mypy 官方文档一致。
- Architecture: HIGH - `Phase 90` 冻结输入 + 当前代码热点扫描 + focused baseline tests 一致。
- Pitfalls: MEDIUM - 既有官方 typing 指南为高可信，但具体 blast radius 与 future consumer drift 仍含项目内推断成分。

**Research date:** 2026-03-28
**Valid until:** 2026-04-04
