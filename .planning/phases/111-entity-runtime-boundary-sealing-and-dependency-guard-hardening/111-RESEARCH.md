# Phase 111: Entity-runtime boundary sealing and dependency-guard hardening - Research

**Researched:** 2026-03-31
**Domain:** entity/control → runtime public-surface sealing, policy-driven dependency guards, changed-surface validation
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### Boundary sealing
- `custom_components/lipro/entities/**` 不再直接 import concrete `Coordinator`，也不再通过 concrete cast 读取 runtime internals。
- entity adapters 必须改为依赖 sanctioned runtime public surface、runtime view type、或更局部的 typed contract；不能以兼容为名把 concrete runtime root 重新暴露给 entity 层。
- control surfaces 若仍存在 direct runtime concrete bypass，也必须一并收口到 sanctioned helper / contract，不得新增第二条 runtime access story。

### Guard hardening
- `tests/meta/test_dependency_guards.py` 与相关 architecture-policy checks 必须把 entity / control → `core.coordinator` direct dependency 纳入 machine-checkable 规则。
- 守卫失败信息必须能明确指出 forbidden import / forbidden cast / forbidden private-state reach-through，而不是只给模糊断言。

### Validation scope
- focused validation 必须覆盖：
  - entity runtime binding 正常工作；
  - 新 dependency guards 能抓到越界；
  - changed surface 相关 failure branches 至少覆盖 command/request guard 的关键错误路径。
- 不允许用 repo-wide line coverage 代替本阶段的 targeted proof。

### North-star constraints
- 不得引入 compat shell、second root、friend-style bypass、全局单例回退。
- 不得为通过测试而把 concrete runtime internals 重新包装成 outward public surface。
- 命名调整应朝 formal-home discoverability 前进，而不是制造新的中间术语层。

### Claude's Discretion
- 可自行决定以 `Protocol`、runtime view dataclass、或更局部 helper contract 承载 entity 所需最小能力，只要不破坏现有 outward behavior。
- 可自行决定 dependency guards 落在 `tests/meta`、`scripts/check_architecture_policy.py`、或二者组合，只要 machine-checkable 且 CI 可复用。

### Deferred Ideas (OUT OF SCOPE)
- `ARC-29` / `GOV-72` 的 formal-home discoverability 与 stale governance anchors 留到 `Phase 112`。
- `QLT-46` 的 broader hotspot burn-down 留到 `Phase 113`。
- `OSS-14` / `SEC-09` 的 public reachability honesty 与 security-surface normalization 留到 `Phase 114`。
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ARC-28 | entity/control 只依赖 runtime public surface / control contracts；移除 concrete `Coordinator` import、cast 与 private reach-through | 采用“HA typed base + 最小 runtime verb protocol”双层约束；control 继续只经 `runtime_access.py` 暴露 runtime read-model |
| GOV-71 | dependency guards / architecture policy / focused tests machine-check bypass drift | 规则真源写入 `ARCHITECTURE_POLICY.md`，由 `scripts/check_architecture_policy.py` + `tests/meta/*guards*` 双轨消费 |
| TST-38 | changed-surface validation 覆盖 command/request failure branches、new dependency guards、renamed read-model seams | 聚焦 `test_entity_base.py`、`test_runtime_access.py`、`test_init_service_handlers_commands.py`、`test_init_service_handlers_debug_queries.py` |
</phase_requirements>

## Summary

仓库已经把 entity 运行时行为大体收口到 `custom_components/lipro/runtime_types.py` 暴露的命名动词上，但 `custom_components/lipro/entities/base.py` 仍保留一个高价值漏口：它直接 import `core.coordinator.coordinator.Coordinator`，并用 `cast(Coordinator, coordinator)` 只为喂给 `CoordinatorEntity`。这不是行为必需，而是 typing 桥接遗留；最安全的修法是把 HA 基类约束压缩成 `DataUpdateCoordinator[...]` 的本地 typed bridge，把真实运行时交互继续锁在最小 protocol verb surface 上。

control 侧 outward story 已经以 `custom_components/lipro/control/runtime_access.py` 为正式 home，但 support 层仍依赖 `entry.runtime_data` + reflective member narrowing + unsound cast 来构造 read-model。这里不应把反射扩散到调用方，也不应再发明第二条 helper story；应把“从 `runtime_data` 缩窄到 control 可读视图”的私边界继续封在 `runtime_access_support_*` 单点，并给它加 machine-checkable no-regrowth guards。

**Primary recommendation:** entity 侧改成“HA `DataUpdateCoordinator` typed bridge + 最小 runtime protocol”；control 侧把 `runtime_data` 缩窄逻辑压回 `runtime_access_support_*` 单点；所有 import/cast/private-state regressions 都写入 `ARCHITECTURE_POLICY.md`，由脚本与 meta tests 双轨执行。

## Direct Answers

1. **最小 sanctioned runtime public surface（entity 真正需要的）**
   - `last_update_success`
   - `get_device(device_id)`
   - `register_entity(entity)` / `unregister_entity(entity)`
   - `async_send_command(device, command, properties)`
   - `async_apply_optimistic_state(device, properties)`
   - `async_request_refresh()`
   - `async_query_device_ota_info(device, *, allow_rich_v2_fallback)`（仅 `firmware_update.py` 需要）
   - **额外说明：** `CoordinatorEntity` 只需要一个 `DataUpdateCoordinator[...]` 实例来完成 HA 基类绑定；这应是本地 typed bridge，不应继续成为 entity 侧 concrete runtime import 的理由。

2. **当前违反 north-star 的 concrete import / cast / private reach**
   - `custom_components/lipro/entities/base.py`：`from ..core.coordinator.coordinator import Coordinator`
   - `custom_components/lipro/entities/base.py`：`class LiproEntity(CoordinatorEntity[Coordinator])`
   - `custom_components/lipro/entities/base.py`：`super().__init__(cast(Coordinator, coordinator))`
   - `custom_components/lipro/control/runtime_access_support_views.py`：`cast(LiproCoordinator, coordinator)` 把 `runtime_data` 无证明上抬到 richer control surface
   - `custom_components/lipro/control/runtime_access_support_views.py` / `runtime_access_support_devices.py` / `runtime_access_support_telemetry.py`：围绕 `entry.runtime_data`、`config_entry`、`mqtt_service.connected`、`protocol`、`telemetry_service.build_snapshot` 的 reflective narrowing 仍是 control → runtime 私边界；它们必须继续局限在 `runtime_access_support_*`，不能泄漏到调用方
   - **未发现的新散落 bypass：** 代码扫描未发现 `custom_components/lipro/control/**` 直接 import `core.coordinator.coordinator`；control 调用方当前大多仍经 `runtime_access.py`

3. **guards 应放哪里**
   - **结论：两处都要。**
   - `ARCHITECTURE_POLICY.md`：唯一规则真源，新增 rule ids / targeted bans
   - `scripts/check_architecture_policy.py`：maintainer/CI fail-fast，适合快速发现 import/cast/private-literal 漂移
   - `tests/meta/test_dependency_guards.py` + `tests/meta/test_public_surface_guards.py`：pytest 入口、开发体验更好，并保护“测试命令本身也能抓到 drift”
   - **落点建议：**
     - direct import 继续走 structural rule（扩展现有 entity/control plane rules）
     - concrete cast / raw `runtime_data` literal / leaked support helper 走 targeted ban（`file_contains_disjoint`）

4. **Phase 111 应补的 TST-38 targeted tests**
   - 新增 `tests/meta/test_phase111_runtime_boundary_guards.py`：锁死 entity concrete import/cast 与 control-side raw narrowing literal 不回流
   - 更新 `tests/core/test_runtime_access.py`：增加“`runtime_data` 存在但不满足 control public surface 时拒绝/降级”的 seam 测试
   - 更新 `tests/core/test_init_service_handlers_debug_queries.py`：补 service-level `query_command_result` 的 `failed` / `unconfirmed` 终态分支，不只测 confirmed polling
   - 保持并在必要时更新 `tests/core/test_init_service_handlers_commands.py`：`invalid_command_request`、push failed、API error、busy/offline translation 仍是 changed-surface fail path 基线
   - 视 entity bridge 改法，微调 `tests/platforms/test_entity_base.py`：确保 typed bridge 改动后，命令失败触发 refresh、debounce failure clear、register/unregister 行为不变

5. **最安全的分解顺序**
   1. 先引入 entity typed bridge / control narrowing helper，不改 outward behavior
   2. 再移除 `entities/base.py` concrete import/cast，并只保留最小 runtime verbs
   3. 如有必要，再把 control 侧 unsound cast 收口到单一 narrowing helper，避免 support seam 外溢
   4. 接着补 `ARCHITECTURE_POLICY.md` rule ids、脚本 inventory、meta inventory
   5. 最后补 TST-38 focused tests，并跑最小充分套件

## Project Constraints (from CLAUDE.md)

- `AGENTS.md` 高于 `CLAUDE.md`；若冲突，以 `AGENTS.md` 为准
- `CLAUDE.md` 只是兼容入口，不得建立第二套 truth source
- 必须按 read order 以 `AGENTS.md`、north-star、planning/baseline docs 为先
- 不再创建或依赖 `agent.md`
- 当前 focus 以 `.planning/STATE.md` 为准

## Standard Stack

### Core
| Library / Asset | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Home Assistant `CoordinatorEntity` + `DataUpdateCoordinator` | `homeassistant==2026.3.1` | HA entity base / typed bridge | 这是 entity 接入 HA update coordinator 的正式基类；只应用于 HA 绑定，不应用来扩大 runtime public surface |
| `custom_components/lipro/runtime_types.py` | repo-local | entity/control 使用的 runtime public protocols | 现有 north-star 已把 runtime verbs 与 richer control surface 收口在这里 |
| `custom_components/lipro/control/runtime_access.py` | repo-local | control 唯一 runtime read-model/home | `DEPENDENCY_MATRIX.md` 已把它裁定为 control 读取 runtime 的正式 helper home |
| `ARCHITECTURE_POLICY.md` + `scripts/check_architecture_policy.py` + meta guards | repo-local | machine-checkable boundary enforcement | 仓库已存在单真源 + 双执行器，不应再造第三套 guard 机制 |

### Supporting
| Library / Asset | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `tests/platforms/test_entity_base.py` | repo-local | entity command/debounce/failure behavior proof | entity bridge / runtime verb 改动后 |
| `tests/core/test_runtime_access.py` | repo-local | control read-model seam proof | 调整 `runtime_data` 缩窄或 view builder 时 |
| `tests/core/test_init_service_handlers_commands.py` | repo-local | command/request failure branch proof | command request path touched 时 |
| `tests/core/test_init_service_handlers_debug_queries.py` | repo-local | `query_command_result` polling/failure branch proof | diagnostics request path touched 时 |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| entity protocol + HA typed bridge | `from ..coordinator_entry import Coordinator` | 仍把 concrete runtime root 暴露给 entity adapter，只是换了 sanctioned import home，无法满足 ARC-28 的“最小 surface”目标 |
| script + meta 双轨 | 只保留 tests 或只保留 script | 单轨要么 fail-fast 差，要么开发反馈差，而且 inventory 容易漂移 |
| localized control narrowing | 在 diagnostics/service/developer call sites 直接读 `runtime_data` | 会重开第二条 runtime access story，违反既有 baseline |

**Installation:**
```bash
uv sync --extra dev
```

**Version verification:** 项目当前 pin 见 `pyproject.toml`；本机验证到 `uv 0.10.9`、`uv run python 3.14.3`、`node 20.19.2`。

## Architecture Patterns

### Recommended Project Structure
```text
custom_components/lipro/
├── entities/base.py                    # HA entity bridge + minimal runtime verbs
├── entities/firmware_update.py         # OTA-specific entity verbs
├── runtime_types.py                    # runtime public protocols
├── control/runtime_access.py           # control formal runtime read surface
└── control/runtime_access_support_*.py # localized narrowing/private edge only
```

### Pattern 1: HA Typed Bridge + Minimal Entity Runtime Protocol
**What:** `CoordinatorEntity` 只保留 HA 基类绑定；所有运行时行为都走最小 protocol verbs。
**When to use:** `entities/base.py` 与 `entities/firmware_update.py`。
**Example:**
```python
# Source: custom_components/lipro/entities/base.py + homeassistant.helpers.update_coordinator.CoordinatorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

type _EntityCoordinatorBase = DataUpdateCoordinator[dict[str, LiproDevice]]

class LiproEntity(CoordinatorEntity[_EntityCoordinatorBase]):
    def __init__(self, coordinator: LiproEntityRuntime, device: LiproDevice) -> None:
        super().__init__(cast(_EntityCoordinatorBase, coordinator))
        self._runtime = coordinator
```

### Pattern 2: Localized Control Narrowing at `runtime_access`
**What:** `entry.runtime_data` 与 reflective member probing 只能停留在 `runtime_access_support_*`，对外统一导出 `RuntimeEntryView` / `RuntimeCoordinatorView`。
**When to use:** diagnostics、system health、developer services、device lookup。
**Example:**
```python
# Source: custom_components/lipro/control/runtime_access.py
runtime_entry = build_runtime_entry_view(entry)
if runtime_entry is None or runtime_entry.coordinator is None:
    return None
return runtime_entry.coordinator
```

### Pattern 3: Policy-Driven Dual Enforcement
**What:** rule ids 只在 `ARCHITECTURE_POLICY.md` 定义；脚本与 pytest 共同消费。
**When to use:** import、cast、private-state literal、support seam locality bans。
**Example:**
```text
ARCHITECTURE_POLICY.md
  -> scripts/check_architecture_policy.py
  -> tests/meta/test_dependency_guards.py
  -> tests/meta/test_public_surface_guards.py
```

### Anti-Patterns to Avoid
- **Concrete entity coordinator import:** `entities/base.py` 继续 import `core.coordinator.coordinator.Coordinator`
- **Typing escape hatch:** 用 `CoordinatorEntity[Any]` 或更宽泛的 `Any` 逃避 Phase 94 typed-boundary guard
- **Scattered runtime_data reads:** 在 `services/**`、`diagnostics_surface.py`、`developer_router_support.py` 重新读取 `entry.runtime_data`
- **Guard split-brain:** 只在 tests 或只在 script 写规则，不回写 `ARCHITECTURE_POLICY.md`
- **Surface inflation:** 为了少改代码，把 `command_service` / `protocol_service` 再塞回 entity-facing protocol

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| entity runtime locator | 新的 entity 专用 coordinator wrapper | `runtime_types.py` 最小 protocol + HA typed bridge | wrapper 容易再次把 concrete runtime root 合法化 |
| control runtime traversal | 调用方自己读 `entry.runtime_data` | `control/runtime_access.py` | 仓库已明确它是唯一 control/runtime helper home |
| architecture drift scan | ad hoc `rg`/regex tests | `ARCHITECTURE_POLICY.md` + policy script + meta consumers | 现成 infra 已能统一 inventory、错误消息与 CI 入口 |
| command failure mapping | 自己重新翻译错误 | `custom_components/lipro/services/command.py` / diagnostics handlers | 已有 translation key、failure summary 与 logging contract |

**Key insight:** Phase 111 的价值不在新增抽象，而在把“已存在的正式 surface + guard infra”补成闭环。

## Runtime State Inventory

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — 本阶段不改持久化 key / collection / schema；未发现需迁移的 runtime boundary 标识 | none |
| Live service config | None — 本阶段不涉及 UI/外部服务配置中的命名迁移 | none |
| OS-registered state | None — 不涉及 systemd/launchd/Task Scheduler/pm2 注册名 | none |
| Secrets/env vars | None — 不改 env var / secret key 名称 | none |
| Build artifacts | None — 不涉及包名/镜像/tag 重命名；最多需要重新跑本地测试 | none |

## Common Pitfalls

### Pitfall 1: 用 `CoordinatorEntity[Any]` 逃避 concrete import
**What goes wrong:** 虽然去掉了 `Coordinator` import，但会直接撞上既有 typed-boundary guard，并把 public surface 重新抹宽。
**Why it happens:** 只盯着 import，不盯着 Phase 94 既有约束。
**How to avoid:** 用 `DataUpdateCoordinator[...]` 做本地 typed bridge，runtime 行为继续走最小 protocol。
**Warning signs:** `entities/base.py` 出现 `Any`、`CoordinatorEntity[Any]`。

### Pitfall 2: 把 `runtime_data` 缩窄逻辑散落到 control 调用方
**What goes wrong:** diagnostics / services / developer surfaces 又开始各自讲 runtime access 故事。
**Why it happens:** 觉得 `runtime_access_support_*` 太绕，直接在调用方偷读更快。
**How to avoid:** 缩窄逻辑只放在 `runtime_access_support_*`，调用方只吃 typed views。
**Warning signs:** `services/**` 或 `control/*surface*.py` 出现 `.runtime_data`、`_get_explicit_member`。

### Pitfall 3: 只在一个执行器里加 guard
**What goes wrong:** `pytest` 能抓、script 抓不到，或反过来；inventory tests 也会失配。
**Why it happens:** 忘了仓库已把 policy checker / governance inventory 做成双轨。
**How to avoid:** 同时更新 `ARCHITECTURE_POLICY.md`、`scripts/check_architecture_policy.py` 的 expected ids、`tests/meta/test_governance_guards.py` inventory。
**Warning signs:** `test_architecture_policy_rule_inventory_is_stable` 或 policy checker inventory 开始失败。

## Code Examples

### Entity-side minimal bridge
```python
# Source: custom_components/lipro/entities/base.py
device = self.runtime_coordinator.get_device(self._device.serial) or self._device
await self.runtime_coordinator.async_apply_optimistic_state(device, optimistic_state)
success = await self.runtime_coordinator.async_send_command(device, command, properties)
if not success:
    await self.runtime_coordinator.async_request_refresh()
```

### Control-side typed runtime view
```python
# Source: custom_components/lipro/control/runtime_access.py
runtime_entry = build_runtime_entry_view(entry)
if runtime_entry is None or runtime_entry.coordinator is None:
    return None
snapshot = build_runtime_snapshot(runtime_entry.entry)
```

### Policy-driven targeted ban
```text
# Source: .planning/baseline/ARCHITECTURE_POLICY.md
Prefer a targeted ban that forbids:
- `core.coordinator.coordinator`
- `cast(Coordinator, coordinator)`
- leaked `runtime_data` literals outside runtime_access support
```

## State of the Art

| Old Approach | Current / Recommended Approach | When Changed | Impact |
|--------------|-------------------------------|--------------|--------|
| entity 直接 import/cast concrete `Coordinator` | entity 只保留 HA typed bridge，行为走 minimal runtime protocol | Phase 111 target | 去 concrete bypass，不改 outward behavior |
| control 调用方散落 runtime lookup | `runtime_access.py` 统一导出 typed views | 已在 Phase 73/89/91 收敛，Phase 111 继续封口 | 保持单一 control/runtime story |
| guards 各写各的 | `ARCHITECTURE_POLICY.md` 单真源，script + pytest 双执行 | 已建立，Phase 111 扩展 | 降低 drift，失败信息更清晰 |

**Deprecated/outdated:**
- `custom_components/lipro/entities/base.py` 直连 `core.coordinator.coordinator.Coordinator`
- 在 `runtime_access_support_*` 之外读取 `entry.runtime_data` 或复制 reflective narrowing helpers

## Open Questions

1. **要不要新增 `LiproEntityRuntime` protocol 名称？**
   - What we know: 当前 `LiproRuntimeCoordinator` 已覆盖 entity 所需动词，但比最小需求略宽。
   - What's unclear: 是否值得为了更窄命名再波及 `helpers/platform.py` / 各 entity 构造签名。
   - Recommendation: 若改动能局限在 `entities/**` + `helpers/platform.py`，可新增；否则先保留现名，只把 concrete import/cast 移除。

2. **control 侧要不要彻底去掉 reflective narrowing？**
   - What we know: 当前反射已局部化在 `runtime_access_support_*`，且主要用于防止 MagicMock ghost probing。
   - What's unclear: 当前 phase 是否值得再把它替换成显式 adapter construction。
   - Recommendation: 本阶段至少先 guard locality + unsound cast；若替换实现会放大 churn，可留待后续更聚焦的 runtime_access cleanup。

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | tests / lint / local script runs | ✓ | `0.10.9` | — |
| `uv run python` | project Python execution | ✓ | `3.14.3` | — |
| `node` | `gsd-tools` / repo scripts | ✓ | `20.19.2` | — |
| bare `python3` | ad hoc shell usage | ✓ | `3.13.5` | use `uv run python` per repo rule |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:** bare `python3` is below the project target; use `uv run python` instead.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest` (`pyproject.toml`; dev extras include `pytest>=7.0.0`) |
| Config file | `pyproject.toml` |
| Quick run command | `uv run pytest tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/core/test_runtime_access.py tests/platforms/test_entity_base.py tests/core/test_init_service_handlers_commands.py tests/core/test_init_service_handlers_debug_queries.py -q` |
| Full suite command | `uv run pytest -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ARC-28 | entity/control 只经 sanctioned runtime surface 交互 | unit + meta | `uv run pytest tests/platforms/test_entity_base.py tests/core/test_runtime_access.py tests/meta/test_phase111_runtime_boundary_guards.py -q` | `❌ Wave 0` |
| GOV-71 | forbidden import/cast/private reach 被 machine-check 拒绝 | meta | `uv run pytest tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py -q` | `✅` |
| TST-38 | command/request failure branches + read-model seam changes可被 focused runs 暴露 | unit | `uv run pytest tests/core/test_init_service_handlers_commands.py tests/core/test_init_service_handlers_debug_queries.py tests/core/test_runtime_access.py tests/platforms/test_entity_base.py -q` | `✅` |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/core/test_runtime_access.py tests/platforms/test_entity_base.py -q`
- **Per wave merge:** `uv run pytest tests/core/test_init_service_handlers_commands.py tests/core/test_init_service_handlers_debug_queries.py -q`
- **Phase gate:** `uv run pytest -q` after guard inventory and targeted suites are green

### Wave 0 Gaps
- [ ] `tests/meta/test_phase111_runtime_boundary_guards.py` — concrete import/cast/private-state no-regrowth proof for ARC-28/GOV-71
- [ ] `tests/core/test_runtime_access.py` — malformed / underspecified `runtime_data` rejection or degraded-read-model case
- [ ] `tests/core/test_init_service_handlers_debug_queries.py` — service-level `failed` / `unconfirmed` terminal branches for `query_command_result`
- [ ] `tests/meta/test_governance_guards.py` + `scripts/check_architecture_policy.py` inventories — sync new rule ids in the same change

## Sources

### Primary (HIGH confidence)
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — north-star dependency direction and formal homes
- `.planning/baseline/DEPENDENCY_MATRIX.md` — runtime_access uniqueness and entity/control dependency law
- `.planning/baseline/ARCHITECTURE_POLICY.md` — current structural rules and targeted-ban mechanism
- `custom_components/lipro/entities/base.py` — current concrete import/cast leak
- `custom_components/lipro/runtime_types.py` — existing runtime public protocols
- `custom_components/lipro/control/runtime_access.py` — sanctioned control runtime surface
- `custom_components/lipro/control/runtime_access_types.py` — typed runtime read-models
- `custom_components/lipro/control/runtime_access_support_views.py` — current narrowing/cast seam
- `custom_components/lipro/control/runtime_access_support_devices.py` — current device lookup narrowing seam
- `custom_components/lipro/control/runtime_access_support_telemetry.py` — current telemetry narrowing seam
- `tests/meta/test_dependency_guards.py` / `tests/meta/test_public_surface_guards.py` / `tests/meta/test_governance_guards.py` — guard execution topology
- `tests/core/test_runtime_access.py` — current runtime_access seam coverage
- `tests/platforms/test_entity_base.py` — entity failure/debounce/lifecycle focused coverage
- `tests/core/test_init_service_handlers_commands.py` — command failure branch coverage
- `tests/core/test_init_service_handlers_debug_queries.py` — `query_command_result` service polling coverage
- `pyproject.toml` — toolchain / test framework / pinned dev dependencies
- Local HA source inspection via `uv run python` — confirmed `CoordinatorEntity` is parameterized by `DataUpdateCoordinator[...]`

### Secondary (MEDIUM confidence)
- None.

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - 全部来自 repo truth + local env inspection
- Architecture: HIGH - north-star、dependency matrix、runtime_types 与 actual code scan 一致
- Pitfalls: HIGH - 由现存 guard suites、code grep 与 focused tests 共同支持

**Research date:** 2026-03-31
**Valid until:** 2026-04-30 or until `runtime_types.py` / `runtime_access*.py` / `ARCHITECTURE_POLICY.md` changes
