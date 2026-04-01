# Phase 127: runtime-access de-reflection, typed runtime entry contracts, and hotspot continuation - Research

**Researched:** 2026-04-01
**Domain:** control-plane runtime access / typed telemetry seam
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- `127-CONTEXT.md` 未提供 `## Decisions`。

### Claude's Discretion
- `127-CONTEXT.md` 未提供 `## Claude's Discretion`。

### Deferred Ideas (OUT OF SCOPE)
- `127-CONTEXT.md` 未提供 `## Deferred Ideas`。

### Other Phase Context (verbatim)
- `## Goal`: 显式推进 `runtime_access` seam：让 typed telemetry contract 成为唯一正式 truth，并把 runtime entry / coordinator narrowing 从反射式 probe 收紧到显式 port / adapter。
- `## Source Findings`: `custom_components/lipro/control/runtime_access.py` 仍会把 typed telemetry 擦回 dict 再用字符串 key 回捞；`custom_components/lipro/control/runtime_access_support_views.py` 仍保留 `type(...).__getattribute__` 主导的窄化方式。
- `## Planned Outcome`: `build_entry_system_health_view()` / `build_runtime_snapshot()` 直接消费 typed telemetry view；runtime entry / coordinator narrowing 有明确 typed contract 或 adapter helper。
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ARC-39 | `runtime_access.build_entry_system_health_view()` 与 `build_runtime_snapshot()` 必须消费 typed telemetry contract，而不是先降为 `dict[str, object]` 再回捞字符串 key。 | 研究确认 canonical truth 已在 `custom_components/lipro/core/telemetry/models.py`；最小收口是让 `runtime_access.py` 直接消费 typed `system_health` sink，并把 `control/models.py` 的 `FailureSummary` 回收到 canonical telemetry type。 |
| HOT-58 | `runtime_access_support_views.py` 的 runtime entry / protocol narrowing 必须退出 `type(...).__getattribute__` 主导的反射式 seam，回到显式 port / adapter story。 | 研究确认 `custom_components/lipro/control/runtime_access_support_members.py` 已有 `_get_explicit_member()` / `_has_explicit_runtime_member()`，且 `runtime_access_support_devices.py` 已有非反射先例；无需新增第二 formal root。 |
| TST-49 | `runtime_access` typed telemetry / de-reflection 收口必须补齐 focused tests，覆盖 slot-backed entry、MagicMock/probe-only object 与 degraded fallback 语义。 | 研究确认 `tests/core/test_runtime_access.py` / `tests/core/test_control_plane.py` 已覆盖大部分行为；Phase 127 只需在现有文件加断言，不必新建测试基础设施。 |
</phase_requirements>

## Summary

Phase 127 的核心不是“新增能力”，而是把仓库里已经存在的 formal truth 真正接上线。`custom_components/lipro/core/telemetry/models.py` 已定义 `SystemHealthTelemetryView`、`TelemetryViews` 等 typed sink contract，但 `custom_components/lipro/control/runtime_access.py:191` 仍把 `export_views().system_health` 降成 `dict[str, object]`，随后在 `custom_components/lipro/control/runtime_access.py:202` 到 `custom_components/lipro/control/runtime_access.py:275` 再按字符串 key 回捞；与此同时，`custom_components/lipro/control/models.py:7` 又定义了第二份更宽的 `FailureSummary = dict[str, str | None]`，把 `custom_components/lipro/core/telemetry/outcomes.py:15` 的 canonical `FailureSummary` TypedDict 再次擦宽。

de-reflection 这半边也不是缺机制，而是没有复用现成机制。`custom_components/lipro/control/runtime_access_support_members.py:22` 已有 `_get_explicit_member()`，`custom_components/lipro/control/runtime_access_support_devices.py:40` 到 `custom_components/lipro/control/runtime_access_support_devices.py:59` 已示范了“先做 explicit-member gate，再走普通属性访问”的无反射模式；但 `custom_components/lipro/control/runtime_access_support_views.py:65` 与 `custom_components/lipro/control/runtime_access_support_views.py:134` 仍以 `type(...).__getattribute__` 作为主路径。最小正确方案不是再造新 adapter root，而是让 `runtime_access_support_views.py` 跟随现有 explicit-member helper 体系。

**Primary recommendation:** 先把 `RuntimeCoordinatorSnapshot.failure_summary` 与 `build_runtime_snapshot()` 对齐到 canonical telemetry truth，再把 `runtime_access_support_views.py` 改成 `_get_explicit_member()` 驱动，最后用现有 focused tests 锁死 slot-backed / probe-only / degraded 语义。

## Project Constraints (from CLAUDE.md)

- `AGENTS.md` 是 canonical repository contract；`CLAUDE.md` 只做兼容入口，不能建立第二套 truth。
- 读取顺序必须先看 `AGENTS.md`，再看 north-star / `.planning/*` 真源。
- 不要创建或依赖 `agent.md`。
- 当前里程碑 / 阶段 / 推荐下一步以 `.planning/STATE.md` 为准。

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `custom_components/lipro/core/telemetry/models.py` | repo-local | formal telemetry sink/view contract (`SystemHealthTelemetryView`, `TelemetryViews`) | 已是 exporter-owned truth，符合 north-star 的单一 telemetry story |
| `custom_components/lipro/core/telemetry/outcomes.py` | repo-local | canonical `FailureSummary` 与 `empty_failure_summary()` | 已冻结 failure taxonomy；不应再被 control-plane 宽化 |
| `custom_components/lipro/control/runtime_access.py` | repo-local | 唯一正式 runtime read-model / snapshot / lookup home | `.planning/baseline/PUBLIC_SURFACES.md` 已明示这是唯一 formal home |
| `custom_components/lipro/control/runtime_access_types.py` | repo-local | runtime entry / coordinator typed views | 现有 narrowing 就围绕它工作 |
| `custom_components/lipro/runtime_types.py` | repo-local | upstream formal runtime/protocol ports | `LiproCoordinator.protocol` / `telemetry_service` 已是正式 contract |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `custom_components/lipro/control/runtime_access_support_members.py` | repo-local | explicit-member gate helpers | 任何需要拒绝 `MagicMock` / `__getattr__` 幽灵成员的 narrowing |
| `custom_components/lipro/control/runtime_access_support_devices.py` | repo-local | de-reflection precedent | 复制其“gate + 普通属性访问”模式到 `support_views` |
| `tests/core/test_runtime_access.py` | repo-local | focused runtime_access regressions | Phase 127 的主验证面 |
| `tests/core/test_control_plane.py` | repo-local | cross-surface contract regressions | 验证 typed snapshot/projection 不泄漏旧 story |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| canonical telemetry `FailureSummary` | control-local `dict[str, str \| None]` | 会把 literal taxonomy 擦宽，重新制造第二 truth |
| explicit-member helper | `type(...).__getattribute__` reflection | 虽能挡住 ghost attrs，但仍保留反射式 seam |
| typed `SystemHealthTelemetryView` | `dict[str, object]` fallback | 继续 stringly-typed 回捞，违背 ARC-39 |

**Installation:** 无新增依赖；Phase 127 只应复用仓内既有 formal contracts。

## Architecture Patterns

### Recommended Project Structure
```text
custom_components/lipro/control/
├── runtime_access.py                # formal runtime snapshot / lookup home
├── runtime_access_support_views.py  # private entry/coordinator narrowing
├── runtime_access_support_members.py# explicit-member gate helpers
├── runtime_access_types.py          # typed runtime entry/coordinator views
├── telemetry_surface.py             # observer-only telemetry bridge
└── models.py                        # control DTOs; 应复用 telemetry truth
```

### Pattern 1: Typed telemetry in, control DTO out
**What:** `runtime_access` 只能从 exporter 的 typed `system_health` sink 读取 `entry_ref`、`device_count`、`mqtt_connected`、`last_update_success`、`failure_summary`；control-plane DTO 只负责投影，不再重新定义 schema。
**When to use:** 生成 `RuntimeCoordinatorSnapshot` / `RuntimeDiagnosticsProjection` 时。
**Example:**
```python
# Source: custom_components/lipro/core/telemetry/models.py
class SystemHealthTelemetryView(TelemetryHeaderPayload):
    failure_summary: FailureSummary
    device_count: int
    last_update_success: bool | None
    mqtt_connected: bool | None
```

### Pattern 2: Explicit-member gate, then normal attribute access
**What:** 先用 `getattr_static`-based helper 排除 `MagicMock` / `__getattr__` 幽灵成员，再做普通 `getattr`/属性访问；不要把 `type(...).__getattribute__` 当成主设计。
**When to use:** narrowing `entry_id`、`options`、`runtime_data`、`protocol` 这类 runtime-facing 成员时。
**Example:**
```python
# Source: custom_components/lipro/control/runtime_access_support_members.py
def _get_explicit_member(obj: object | None, name: str) -> object | None:
    if _get_static_member(obj, name) is _MISSING:
        return None
    try:
        return getattr(obj, name)
    except AttributeError:
        return None
```

### Pattern 3: Preserve live entry identity, materialize only facts/views
**What:** `RuntimeEntryView` 包住 live entry 与 narrowed facts；不要复制/克隆 entry 实例。
**When to use:** `iter_runtime_entries()`、`iter_runtime_entry_views()`、`build_runtime_entry_view()` 这类 control-plane 读模型。
**Example:**
```python
# Source: custom_components/lipro/control/runtime_access_types.py
@dataclass(frozen=True, slots=True)
class RuntimeEntryView:
    entry: RuntimeEntryPort
    entry_id: str
    options: Mapping[str, object]
    coordinator: RuntimeCoordinatorView | None
```

### Anti-Patterns to Avoid
- **Stringly telemetry bridge:** 先 `dict()` 再 `.get("failure_summary")` 会让 typed sink 失去 formal authority。
- **Reflection-first narrowing:** `type(...).__getattribute__` 作为主路径会把 helper 叙事停留在 residual，而不是 explicit contract。
- **Second DTO truth:** 在 `control/models.py` 再造一份更宽的 `FailureSummary`，会让 `core/telemetry/outcomes.py` 失效。
- **Entry cloning:** 若新建 entry wrapper 对象，会直接撞上 live-identity 回归测试。

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| failure summary schema | control-local dict alias | `custom_components/lipro/core/telemetry/outcomes.py::FailureSummary` | canonical taxonomy 已存在，重复定义只会漂移 |
| probe-only object filtering | ad-hoc reflection branch | `_get_explicit_member()` / `_has_explicit_runtime_member()` | 仓内已有机制，且已有 device helper 先例 |
| runtime telemetry bridge | runtime_access 内部手搓 protocol/runtime payload | `RuntimeTelemetryExporter.export_views()` | exporter 已负责 typed sink 生成 |
| runtime entry adaptation | 新增 second adapter root | 复用 `RuntimeEntryPort` + `RuntimeEntryView` | baseline 明确 `runtime_access` 才是 formal home |

**Key insight:** 当前 residual 的根因是“类型被擦宽”，不是“仓库缺 helper”；Phase 127 应该复用既有 formal seams，而不是新增新层。

## Runtime State Inventory

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — 本 phase 不涉及持久化 key / collection / user_id rename；已核对相位上下文、治理文档与 touched code scope。 | none |
| Live service config | None — 研究范围只触及 repo 内 control/runtime helper，与 UI/db 托管配置无关。 | none |
| OS-registered state | None — 不涉及 systemd / launchd / task scheduler / pm2 注册名变更。 | none |
| Secrets/env vars | None — 不涉及 env var 名称、secret key 名称或读取入口重命名。 | none |
| Build artifacts | None — 不涉及包名、可执行名或安装产物 rename；只有 Python helper/type refactor。 | none |

## Common Pitfalls

### Pitfall 1: 只改返回值，不回收 `FailureSummary` 第二真源
**What goes wrong:** `runtime_access.py` 看似改成 typed sink，但 `RuntimeCoordinatorSnapshot.failure_summary` 仍是更宽的 `dict[str, str | None]`。
**Why it happens:** `custom_components/lipro/control/models.py:7` 现在复制了一份同形别名。
**How to avoid:** 让 control DTO 直接依赖 canonical telemetry `FailureSummary` / `empty_failure_summary()`。
**Warning signs:** `dict(projection.snapshot.failure_summary)` 仍被当作必要步骤；mypy/IDE 里 `failure_category` 退化成任意 `str`。

### Pitfall 2: 用裸 `getattr` 取代反射，结果把 ghost attrs 又放回来
**What goes wrong:** `ProbeOnlyEntry` / `MagicMock` 再次被当成有效 runtime port。
**Why it happens:** 仅删除 `type(...).__getattribute__`，却忘了保留 `getattr_static` gate。
**How to avoid:** 先 `_has_explicit_runtime_member()` 或 `_get_explicit_member()`，再做正常属性访问。
**Warning signs:** `tests/core/test_runtime_access.py` 里的 `ProbeOnlyEntry` 回归变红或行为被意外接受。

### Pitfall 3: 让 coordinator facts 覆盖 exporter sink 字段
**What goes wrong:** snapshot 又变成 runtime facts 与 telemetry sink 混搭，formal truth 再次双写。
**Why it happens:** 想保留“兜底修正”时，把 exporter 的 `device_count` / `failure_summary` 当 advisory source。
**How to avoid:** typed sink 存在时信任它；只在 exporter 缺席时退回 coordinator facts。
**Warning signs:** `build_runtime_snapshot()` 同时按 key 读 telemetry，又按 coordinator 字段重写同一语义字段。

### Pitfall 4: 为了“更干净”而新建 adapter root
**What goes wrong:** `runtime_access` 之外又长出第二个 runtime/telemetry bridge home。
**Why it happens:** 误把内部 helper refactor 做成 public surface 扩张。
**How to avoid:** 新 helper 只留在 `runtime_access_support_*` 内；formal import home 仍只认 `runtime_access.py`。
**Warning signs:** baseline/public-surface 文档需要新增第二个 control bridge 名字，或 `control/__init__.py` 被迫导出更多 symbol。

## Code Examples

### Canonical failure-summary truth
```python
# Source: custom_components/lipro/core/telemetry/outcomes.py
class FailureSummary(TypedDict):
    failure_category: FailureCategory | None
    failure_origin: str | None
    handling_policy: HandlingPolicy | None
    error_type: str | None
```

### Existing non-reflection precedent to mirror
```python
# Source: custom_components/lipro/control/runtime_access_support_devices.py
def _read_get_device(coordinator: LiproCoordinator) -> Callable[[str], object] | None:
    if not _has_explicit_runtime_member(coordinator, "get_device"):
        return None
    try:
        getter = coordinator.get_device
    except AttributeError:
        return None
    return getter if callable(getter) else None
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `runtime_access` 先把 `system_health` sink 降成 `dict[str, object]` | exporter 已提供 typed `SystemHealthTelemetryView` | current repo head | Phase 127 应直接消费 typed sink，而不是继续 stringly 回捞 |
| `control/models.py` 自带宽口 `FailureSummary` dict | canonical `FailureSummary` 已在 `core/telemetry/outcomes.py` 冻结 | archived telemetry closure 已完成；当前 residual 只剩消费侧未对齐 | 最小正确收口是删掉第二真源，而非再造第三份 alias |
| `support_views.py` 反射式读取 entry/protocol | `support_members.py` + `support_devices.py` 已示范 explicit-member helper 模式 | current repo head | de-reflection 可以局部完成，无需新 formal root |

**Deprecated/outdated residuals:**
- `custom_components/lipro/control/runtime_access.py:191` 到 `custom_components/lipro/control/runtime_access.py:275` 的 stringly telemetry seam。
- `custom_components/lipro/control/runtime_access_support_views.py:65` 与 `custom_components/lipro/control/runtime_access_support_views.py:134` 的 `type(...).__getattribute__` 主路径。

## Open Questions

1. **`RuntimeCoordinatorView.runtime_telemetry_snapshot` 是否一并收紧到 `TelemetrySourcePayload`？**
   - What we know: `_build_runtime_telemetry_snapshot()` 已做 JSON-safe 归一化，但 `runtime_access_types.py` 仍写成 `Mapping[str, object]`。
   - What's unclear: 是否有下游依赖这个更宽的注解。
   - Recommendation: 作为 `127-03` hotspot continuation 检查项，若 grep 无消费者依赖宽口类型则一起收紧。

2. **`control/telemetry_surface.py` 的 `build_entry_system_health_view()` 要不要同步缩窄返回类型？**
   - What we know: 当前几乎无外部调用点，且它本质上知道自己取的是 `system_health` sink。
   - What's unclear: 是否需要在本 phase 同步修整，还是只修 `runtime_access.py` 即可。
   - Recommendation: 若 `127-01` 已触及 telemetry typing，顺手缩窄；否则保留到 `127-03`。

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | 所有 Python lint/test 命令 | ✓ | `0.10.9` | — |
| `uv run python` | 满足 `pyproject.toml` 的 Python `>=3.14.2` floor | ✓ | `3.14.3` | — |

**Missing dependencies with no fallback:** None.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest`（配置在 `pyproject.toml`） |
| Config file | `pyproject.toml` |
| Quick run command | `uv run pytest tests/core/test_runtime_access.py tests/core/test_control_plane.py -q` |
| Full suite command | `uv run pytest -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ARC-39 | snapshot/system-health 直接消费 typed telemetry truth | unit | `uv run pytest tests/core/test_runtime_access.py tests/core/test_control_plane.py -q` | ✅ |
| HOT-58 | entry/protocol narrowing 退出 reflection 且不放回 ghost attrs | unit | `uv run pytest tests/core/test_runtime_access.py tests/core/test_control_plane.py -q` | ✅ |
| TST-49 | slot-backed / probe-only / degraded fallback 语义保持 | unit | `uv run pytest tests/core/test_runtime_access.py tests/core/test_control_plane.py -q` | ✅ |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/core/test_runtime_access.py tests/core/test_control_plane.py -q`
- **Per wave merge:** `uv run ruff check custom_components/lipro/control/runtime_access.py custom_components/lipro/control/runtime_access_support_views.py custom_components/lipro/control/runtime_access_types.py custom_components/lipro/control/models.py tests/core/test_runtime_access.py tests/core/test_control_plane.py`
- **Phase gate:** `uv run pytest -q`

### Wave 0 Gaps
None — 现有测试基础设施已覆盖本 phase；新增验证应直接落在 `tests/core/test_runtime_access.py` 与 `tests/core/test_control_plane.py`。

## Sources

### Primary (HIGH confidence)
- `custom_components/lipro/control/runtime_access.py` - typed telemetry seam 当前擦宽点与 snapshot/projection builder。
- `custom_components/lipro/control/runtime_access_support_views.py` - reflection-driven narrowing 残留。
- `custom_components/lipro/control/runtime_access_support_members.py` - explicit-member helper 现成机制。
- `custom_components/lipro/control/runtime_access_support_devices.py` - 无反射先例。
- `custom_components/lipro/control/runtime_access_types.py` - typed entry/coordinator read-model。
- `custom_components/lipro/runtime_types.py` - `LiproCoordinator.protocol` / `telemetry_service` formal ports。
- `custom_components/lipro/core/telemetry/models.py` - `SystemHealthTelemetryView` / `TelemetryViews` typed sink contract。
- `custom_components/lipro/core/telemetry/outcomes.py` - canonical `FailureSummary` truth。
- `custom_components/lipro/control/models.py` - control-plane 第二 `FailureSummary` 真源。
- `tests/core/test_runtime_access.py` / `tests/core/test_control_plane.py` - 已冻结的 slot-backed / probe-only / degraded 行为。
- `.planning/ROADMAP.md` / `.planning/REQUIREMENTS.md` / `.planning/PROJECT.md` / `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` / `.planning/baseline/PUBLIC_SURFACES.md` / `.planning/reviews/FILE_MATRIX.md` - 相位目标、formal home 与 north-star 裁决。

### Secondary (MEDIUM confidence)
None.

### Tertiary (LOW confidence)
None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - 全部来自仓内 formal contracts 与 baseline docs。
- Architecture: HIGH - north-star、public-surface 与现有代码形态一致。
- Pitfalls: HIGH - 现有测试与残留代码已直接暴露这些失败模式。

**Research date:** 2026-04-01
**Valid until:** 2026-05-01

## Recommended Plan Split

| Plan | Scope | Touched files | Main risk | Validation |
|------|-------|---------------|-----------|------------|
| `127-01` | typed telemetry seam closure | `custom_components/lipro/control/runtime_access.py`, `custom_components/lipro/control/models.py`, `custom_components/lipro/control/diagnostics_surface.py`, 可选 `custom_components/lipro/control/telemetry_surface.py` | 只改调用点却没回收 `FailureSummary` 第二真源，导致 typed truth 仍双写 | `uv run pytest tests/core/test_runtime_access.py tests/core/test_control_plane.py -q` |
| `127-02` | runtime entry / protocol de-reflection | `custom_components/lipro/control/runtime_access_support_views.py`, `custom_components/lipro/control/runtime_access_support_members.py`, `custom_components/lipro/control/runtime_access_types.py`，必要时最小触及 `custom_components/lipro/runtime_types.py` | 去掉反射后若不保留 explicit-member gate，会重新放回 `MagicMock` / `ProbeOnlyEntry` 幽灵成员 | `uv run pytest tests/core/test_runtime_access.py tests/core/test_control_plane.py -q` + `uv run ruff check custom_components/lipro/control/runtime_access_support_views.py custom_components/lipro/control/runtime_access_support_members.py custom_components/lipro/control/runtime_access_types.py` |
| `127-03` | hotspot continuation + regression lock | `tests/core/test_runtime_access.py`, `tests/core/test_control_plane.py`，以及 `127-01/02` 实际 touched files 的最小补强 | 代码已收口但测试还在 patch dict / reflection 旧 story，导致 residual 回流 | `uv run pytest tests/core/test_runtime_access.py tests/core/test_control_plane.py -q` + `uv run python scripts/check_file_matrix.py --check` + `uv run pytest -q` |

- `127-01`：先收口 typed telemetry seam，删掉 `runtime_access` / `control.models` 的第二 telemetry truth。
- `127-02`：再把 `runtime_access_support_views.py` 改成 explicit-member helper 驱动，退出 `type(...).__getattribute__`。
- `127-03`：最后补 focused regressions 与必要 consumer cleanup，锁死 slot-backed / probe-only / degraded 行为。
