# Phase 65: Runtime-access de-reflection and anonymous-share hotspot closure - Research

**Researched:** 2026-03-23
**Domain:** control-plane runtime read-model de-reflection, device extras projection formalization, anonymous-share contract slimming
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- `custom_components/lipro/control/runtime_access.py` 继续保留 formal import home；允许 inward rewrite `runtime_access_support.py` 与相关 tests，但 outward surface 不得漂移。
- `DeviceExtras` / `LiproDevice` 继续保留现有 outward home；允许把 gateway / alias / mesh identity 读取进一步收口到 typed extras/runtime projection，但不恢复第二条 raw-sidecar story。
- `anonymous_share` family 继续以 `manager.py` / `share_client.py` 为 outward home；允许 inward split state / submit / finalize concerns，但不新增第二条 public submit story。
- touched docs 与治理真相必须同轮同步：至少更新 `ROADMAP` / `REQUIREMENTS` / `STATE` / `PROJECT` / `MILESTONES` / `FILE_MATRIX`。
- focused tests 必须随 refactor 同轮补齐；不能只迁文件不增强 proof。

### Claude's Discretion
- runtime-access 去反射化时，可改用 typed fake / explicit stub 替代 MagicMock-heavy proof，但必须保留行为覆盖。
- device extras / identity 收口可以采用 `DeviceExtras` property、runtime projection helper 或更窄 typed alias，只要不再让 raw `extra_data` 充当主读取面即可。
- anonymous-share split 的粒度可按 scope-state access / submit orchestration / success finalization 仲裁，但不要一次性过度抽象。

### Deferred Ideas (OUT OF SCOPE)
- `RequestPolicy` pacing state object 化：仍是值得跟进的 maintainability hotspot，但不把 pacing-state surgery 与 runtime/device/share 三类 surgery 硬塞成一个超大 phase。
- `Coordinator.__init__` 进一步 builder 化 / slimming：可在下一轮 runtime hotspot review 中继续推进。
- 单维护者 continuity / delegate 制度化：属于治理与人员决策问题，不在本 phase 以文案假装解决。
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| HOT-20 | runtime-access 退出 MagicMock-aware reflection / materialized-member probing | 推荐显式 fake entry/coordinator port + 直接 attribute projection；生产代码只读正式 port，不再识别 mock internals |
| HOT-21 | anonymous-share inward decomposition，降低跨文件私有状态耦合 | 推荐把 manager 拆成 state access + submit orchestration + finalize-success 三段，不改 outward home |
| TYP-18 | raw `extra_data` reads / implicit alias sidecars / dynamic probing 收敛为 typed projections | 推荐新增/强化 `DeviceExtras` 与 runtime identity projection，control/runtime consumers 不再直接读 sidecar 决策 |
| TST-15 | touched hotspots 伴随 focused regressions/fixtures 收口 | 推荐 control-plane fake fixtures + anonymous-share focused tests 同轮更新 |
| GOV-49 | 冻结 runtime-access / device-extras / anonymous-share 新 topology truth | 需要同步 `ROADMAP / REQUIREMENTS / STATE / PROJECT / MILESTONES / FILE_MATRIX` |
| QLT-23 | `ruff`、guard、focused/full pytest 同时通过 | 研究给出最小充分验证矩阵 |
</phase_requirements>

## Summary

`Phase 65` 最安全、最根因级的推进方式，不是继续在生产代码里“识别 MagicMock 幽灵”或“给 raw extra_data 再加一层例外”，而是把 **测试需求与生产 contract 完整分离**：生产路径只消费显式的 runtime entry/coordinator port、typed device-extras projection 与 anonymous-share outcome-native submit contract；测试侧则改用明确的 fake/stub，而不是让 `MagicMock` 的动态属性语义反向塑造正式实现。

对 `runtime_access` 而言，最小安全改法是：**把 reflective/mock-aware probing 从 production truth 移除**，让 `build_runtime_entry_view()`、`find_runtime_device()`、telemetry/exporter bridge 只读取 `RuntimeEntryPort` / `LiproCoordinator` 的正式字段与方法。现有 `tests/core/test_control_plane.py` 中大量 `MagicMock()` proof 是反射残留的直接来源，最值得先换成显式 fake entry / fake coordinator / fake mqtt-service / fake telemetry-service。

对 `DeviceExtras` 与 `anonymous_share` 而言，最佳切口都不是“新建第二根”，而是 **把已有 outward home 讲得更诚实**：gateway/member/identity alias 真相应由 `DeviceExtras` 或 runtime projection 暴露，而不是让 control/runtime consumers 在主路径直接读 `device.extra_data`；anonymous-share 则应让 `manager.py` 只做 orchestrator，把 submit-state、submit-flow 与 finalize-success 留给更窄协作者，且 typed outcome 成为唯一正式 submit story。

**Primary recommendation:** 以 `65-01 runtime_access 去反射化` → `65-02 device extras projection formalization` → `65-03 anonymous-share 单轨 submit contract + manager slimming` 的顺序执行；先切断测试污染生产，再收口 sidecar truth，最后收薄 share hotspot。

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python `dataclasses` / `slots=True` | stdlib | 明确状态/投影模型 | 当前仓库已有大量稳定用法，最契合“不引新依赖、显式组合优于隐式反射” |
| Python `Protocol` / `TypedDict` | stdlib typing | 端口接口与 payload 契约 | 当前 `runtime_types.py`、`runtime_access_types.py`、`core/api/types.py` 已是正式 typed contract 基础 |
| Home Assistant `ConfigEntry` / coordinator 模式 | repo existing | runtime root / control bridge 协作模式 | 当前仓库正式 story 已围绕 HA root thin adapter + coordinator/runtime formal home 建立 |
| `pytest` | repo existing | focused regression proof | 当前测试矩阵厚，适合用 focused suites 降低 failure radius |
| `ruff` | repo existing | lint / import / style gate | CI 与本地统一门禁 |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `unittest.mock` | stdlib | 仅用于局部 patch seam | 只保留真正需要 patch 行为的点，避免再把 MagicMock 当正式 runtime double |
| `MappingProxyType` / plain dataclass fakes | stdlib | fake runtime/device state | 当测试需要稳定只读投影时使用 |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| 继续 `MagicMock` 驱动 runtime_access proof | 显式 fake entry/coordinator dataclass | fake 稍多一点样板，但彻底切断生产代码对 mock internals 的耦合 |
| 继续在 consumer 端读取 `device.extra_data` | 在 `DeviceExtras`/projection 增加正式属性 | 会多一个局部 accessor，但 ownership 更诚实 |
| 继续让 manager 代理 `_state` 全部字段 | 拆分 submit-state access / orchestrator helpers | 文件会增加少量小协作者，但 manager hotspot 半径明显下降 |

## Architecture Patterns

### Recommended Project Structure
```text
custom_components/lipro/
├── control/                  # control-plane formal homes
├── core/device/              # device/extras/runtime truth
├── core/anonymous_share/     # share formal homes + inward collaborators
└── tests/                    # focused regression suites / explicit fakes
```

### Pattern 1: Production code reads explicit ports; tests provide honest fakes
**What:** 正式实现只依赖 `Protocol` / dataclass / direct attribute contract，测试通过显式 fake 提供这些字段和方法；不在生产代码里检测 mock internals。
**When to use:** runtime_access、device lookup、telemetry/exporter bridge 这类 control → runtime 读取路径。
**Example:**
```python
@dataclass(slots=True)
class FakeMqttService:
    connected: bool

@dataclass(slots=True)
class FakeTelemetryService:
    payload: Mapping[str, object]

    def build_snapshot(self) -> Mapping[str, object]:
        return self.payload

@dataclass(slots=True)
class FakeCoordinator:
    config_entry: object | None
    update_interval: object | None
    last_update_success: bool
    mqtt_service: FakeMqttService
    telemetry_service: FakeTelemetryService
    protocol: object | None
    devices: Mapping[str, object]

    def get_device(self, device_id: str) -> object | None:
        return self.devices.get(device_id)
```
来源：当前项目在 `runtime_access_types.py`、`runtime_types.py` 的正式 port 设计 + `tests/core/test_control_plane.py` 现有使用场景。

### Pattern 2: Side-car data only mutates locally; outward readers use typed projections
**What:** `device.extra_data` 允许作为 local mutator / compatibility side-car 存在，但 control/runtime/diagnostics 主路径不直接读它，而是经 `DeviceExtras` 或 runtime projection。
**When to use:** gateway device id、group member ids、identity aliases、IR gateway projection。
**Example:**
```python
# producer side
sync_mesh_group_extra_data(device, row)

# consumer side
gateway_id = device.mesh_gateway_device_id
member_ids = device.mesh_group_member_ids
```
来源：`custom_components/lipro/core/device/group_status.py` + `custom_components/lipro/core/device/extras_features.py` + `services/schedule.py` 已采用的模式。

### Pattern 3: Outward home stays stable; inward collaborator split narrows ownership
**What:** `manager.py` / `share_client.py` 保持 outward home，不改 import 路由；内部把 state access、submit orchestration、success finalization 分给更窄协作者。
**When to use:** anonymous-share family 这类 architecturally-correct but still thick 的热点。
**Example:**
```python
async def submit_report(manager, session, *, force: bool) -> bool:
    if manager.is_aggregate_view():
        return await _submit_aggregate_report(manager, session, force=force)
    return await _submit_scoped_report(manager, session, force=force)
```
来源：`custom_components/lipro/core/anonymous_share/manager_submission.py` 的现有 outward-home + inward-helper pattern。

### Anti-Patterns to Avoid
- **生产代码识别 `MagicMock` internals：** `inspect.getattr_static` / `__dict__` / `_mock_children` 读取说明测试语义正在定义正式实现，应改成 fake/stub。
- **consumer 直接读取 raw `extra_data`：** 这会让 side-car 变成第二条正式 truth；应该改走 `DeviceExtras` / projection。
- **manager 既代理 state 又负责 submit flow 又做 finalize side effects：** 会让修改半径过大，难以证明 ownership。
- **为一次性逻辑再长出 `*_support.py`：** 当前阶段应优先留在现有 family inward split，不要创造新 helper root。

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| runtime double | 依赖 `MagicMock` 动态属性+生产代码反射规避 | 显式 fake dataclass / Protocol stub | 简单、可读、不会污染生产 contract |
| device identity projection | 每个 consumer 自己读 `extra_data` | `DeviceExtras` property / localized projection helper | ownership 单一，减少 side-car drift |
| anonymous-share submit state | manager 私下代理全部 `_state` 字段 | 小型 submit state accessor + focused orchestrator helpers | 降低 manager 热点耦合和回归半径 |

**Key insight:** 这类热点最大的问题不是“功能缺失”，而是 **测试/历史兼容语义正在塑造正式实现**。最优解不是再补例外，而是让正式实现只认识正式 port，兼容与测试回到本地边界。

## Common Pitfalls

### Pitfall 1: 先改生产代码，再补 fake tests
**What goes wrong:** 为了让旧 `MagicMock` proof 继续通过，又把反射/ghost handling 写回正式实现。
**Why it happens:** 以现有测试形状为先，而不是以正式 port 为先。
**How to avoid:** 先定义/实现 fake entry + fake coordinator，再删 production reflection。
**Warning signs:** 新代码继续读取 `_mock_children`、`__dict__`、`getattr(..., None)` 来区分真假对象。

### Pitfall 2: 用 projection helper 复制第二套 truth
**What goes wrong:** 想减少 `extra_data` 读取，结果在 control/runtime 又造一套 dict projection，长期与 `DeviceExtras` 漂移。
**Why it happens:** 不愿意把正确字段真正归还给 `DeviceExtras`/runtime formal home。
**How to avoid:** 优先扩 `DeviceExtras` 或 localized projection，并让 consumer 直接消费它。
**Warning signs:** 新 helper 返回 `dict[str, object]`，而不是明确属性/typed alias。

### Pitfall 3: anonymous-share 过度拆分
**What goes wrong:** 一次性拆出太多小模块，反而让 outward home 更难跟踪。
**Why it happens:** 追求“文件更小”而不是“ownership 更诚实”。
**How to avoid:** 只按 submit-state access / orchestration / finalize-success 三个责任切。
**Warning signs:** 新增多个 `support/helper/utils` 文件，但每个只被单点调用一次。

## Code Examples

Verified patterns from current codebase:

### Runtime port style
```python
class RuntimeEntryPort(Protocol):
    entry_id: str
    runtime_data: LiproCoordinator | None
    options: Mapping[str, object]
```
来源：`custom_components/lipro/control/runtime_access_types.py`

### Device extras projection style
```python
def mesh_gateway_device_id(self: DeviceExtras) -> str | None:
    return normalize_iot_device_id(self._extra_data.get("gateway_device_id"))
```
来源：`custom_components/lipro/core/device/extras_features.py`

### Share outward-home + inward submit helper style
```python
async def submit_report(
    manager: AnonymousShareSubmitManagerLike,
    session,
    *,
    force: bool,
) -> bool:
    if manager.is_aggregate_view():
        return await _submit_aggregate_report(manager, session, force=force)
    return await _submit_scoped_report(manager, session, force=force)
```
来源：`custom_components/lipro/core/anonymous_share/manager_submission.py`

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| broad runtime introspection + hidden-root cleanup前的多入口 | typed runtime read-model + control-owned RuntimeAccess | Phase 63 | 已有正式方向，但 runtime_access_support 仍残留 test-driven reflection |
| raw side-car 直接被 service/control 读取 | `DeviceExtras` / device facade 属性逐步承接 extras truth | Phase 62/64 follow-through | schedule 已改善，但 diagnostics/runtime identity 仍有 residual reads |
| anonymous-share thick home | outward home + inward collaborator split | Phase 61 | 方向正确，但 manager / submit flow 仍偏厚 |

**Deprecated/outdated:**
- 生产代码中读取 `_mock_children` / `__dict__` / materialized mock internals：应视为待删除残留，而非长期合法模式。
- control/runtime consumers 直接以 `device.extra_data[...]` 作为主决策源：应继续下沉到 extras/projection formal contract。

## Open Questions

1. **`identity_aliases` 最终应归谁？**
   - What we know: 当前 `core/coordinator/runtime/state/index.py` 仍从 `device.extra_data` 取 alias。
   - What's unclear: 应进 `DeviceExtras` 正式属性，还是进 runtime identity projection。
   - Recommendation: 若只有 runtime index 使用，则优先做 localized runtime projection；若 control/device consumers 都会读，则升级到 `DeviceExtras`。

2. **anonymous-share manager 的最小拆分粒度是什么？**
   - What we know: `manager_submission.py` 已承担 outward-home 下的 submit helper；`manager.py` 仍保留大量 `_state` 代理属性。
   - What's unclear: 是否需要新建 state access helper。
   - Recommendation: 先把 submit-state read/write 与 finalize-success 抽成现有 family 内 helper；若仍过厚，再开第二刀。

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest` + Home Assistant test helpers |
| Config file | `pyproject.toml` / repo-local pytest setup |
| Quick run command | `uv run pytest -q tests/core/test_control_plane.py tests/core/device/test_extras_features.py tests/core/anonymous_share/test_manager_submission.py` |
| Full suite command | `uv run pytest -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HOT-20 | runtime-access 不再依赖 reflection / mock internals | unit | `uv run pytest -q tests/core/test_control_plane.py tests/core/test_system_health.py tests/core/test_diagnostics.py` | ✅ |
| HOT-21 | anonymous-share manager/submit flow 更薄且 contract 单轨 | unit | `uv run pytest -q tests/core/anonymous_share/test_manager_recording.py tests/core/anonymous_share/test_manager_submission.py tests/core/test_share_client.py tests/services/test_services_share.py` | ✅ |
| TYP-18 | raw extra_data 读取被 typed projections 取代 | unit | `uv run pytest -q tests/core/device/test_extras_features.py tests/core/device/test_network_extensions.py tests/core/test_diagnostics.py` | ✅ |
| TST-15 | focused regressions / fixtures 同轮落地 | unit | `uv run pytest -q tests/core/test_control_plane.py tests/core/device/test_extras_features.py tests/core/anonymous_share/test_manager_submission.py` | ✅ |
| GOV-49 | docs / file matrix / current-story 同步 | meta | `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance*.py` | ✅ |
| QLT-23 | 全门禁通过 | mixed | `uv run ruff check . && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q` | ✅ |

### Sampling Rate
- **Per task commit:** `uv run pytest -q` 针对 touched focused suites
- **Per wave merge:** `uv run ruff check . && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check`
- **Phase gate:** `uv run pytest -q`

### Wave 0 Gaps
- [ ] `tests/core/test_control_plane.py` 中 runtime_access proof 需要引入显式 fake entry/coordinator，避免继续依赖 `MagicMock` ghost semantics
- [ ] 若 diagnostics/runtime identity 改到新 projection，需补 focused assertions 到 `tests/core/test_diagnostics.py`
- [ ] 若 anonymous-share manager 新增局部 helper，需要把 focused suite 拆到真正触达 submit/finalize 语义的断言

## Sources

### Primary (HIGH confidence)
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` - formal-home / single-root / boundary purity constraints
- `.planning/ROADMAP.md` - Phase 65 goal and success criteria
- `.planning/REQUIREMENTS.md` - Phase 65 requirement basket
- `.planning/phases/65-runtime-access-de-reflection-and-anonymous-share-hotspot-closure/65-CONTEXT.md` - locked scope / deferred ideas
- `custom_components/lipro/control/runtime_access*.py` - runtime-access current topology and residual reflection
- `custom_components/lipro/core/device/{device,extras,extras_features}.py` - device extras formal-home reality
- `custom_components/lipro/core/anonymous_share/{manager,manager_submission,share_client,share_client_flows}.py` - share current topology and hotspot split points
- `tests/core/test_control_plane.py`, `tests/core/test_diagnostics.py`, `tests/core/test_system_health.py`, `tests/core/device/test_extras_features.py`, `tests/core/device/test_network_extensions.py`, `tests/core/anonymous_share/test_manager_recording.py`, `tests/core/anonymous_share/test_manager_submission.py`, `tests/core/test_share_client.py`, `tests/services/test_services_share.py` - existing regression coverage and fixture pressure points

### Secondary (MEDIUM confidence)
- `.planning/phases/61-formal-home-slimming-for-large-but-correct-production-modules/61-SUMMARY.md` - anonymous-share slimming precedent
- `.planning/phases/63-governance-truth-realignment-typed-runtime-access-and-hidden-root-closure/63-SUMMARY.md` - runtime-access initial closure precedent
- `.planning/phases/64-telemetry-typing-schedule-contracts-and-diagnostics-hotspot-slimming/64-SUMMARY.md` - latest closeout precedent

### Tertiary (LOW confidence)
- None — this research is grounded in current repository truth rather than external ecosystem claims.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - phase relies on existing repo stack and stdlib typing/testing primitives
- Architecture: HIGH - conclusions derive from current north-star docs, roadmap, and touched source files
- Pitfalls: HIGH - each pitfall is directly observable in current production/tests topology

**Research date:** 2026-03-23
**Valid until:** stable until Phase 65 scope changes or a new milestone supersedes v1.14
