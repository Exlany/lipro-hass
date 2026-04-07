# Phase 73: Service-family deduplication, diagnostics/helper convergence, and runtime-surface formalization - Research

**Researched:** 2026-03-25
**Domain:** Home Assistant control/runtime boundary convergence inside `lipro`
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
`73-CONTEXT.md` 未提供 `## Decisions` 段落；以下为同文件中已明确写死、且必须原样服从的约束原文：

- `custom_components/lipro/services/schedule.py` 应建立正式 runtime service，终结 control/service → protocol 直连。
- `custom_components/lipro/helpers/platform.py` 与 entity runtime strategy 需要从 `entry.runtime_data` / `coordinator.devices` 的直接读取收口到正式 projection/read port。
- `custom_components/lipro/control/runtime_access*` outward home 已成立，但 view/facts/support 结构仍偏绕，需要进一步降低 surface 认知成本。
- diagnostics / telemetry / helper family 要维持单一 outward home，避免 support/helper 语义继续散落。
- 不新增第二条正式主链；所有收敛必须回到既有 formal homes
- root HA adapters 继续保持 thin adapter，不把正式 ownership 长回根层
- compat / helper residual 若暂存，必须局部、可计数、可删除，不得伪装成长期架构
- 所有 Python / test / script 命令统一 `uv run ...`
- 方案应优先“彻底回收热点”而不是临时缝补；若无法同轮完成，必须给出明确 delete gate 与后续 owner

### Claude's Discretion
`73-CONTEXT.md` 未提供 `## Claude's Discretion` 段落。

### Deferred Ideas (OUT OF SCOPE)
`73-CONTEXT.md` 未提供 `## Deferred Ideas` 段落。
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ARC-19 | bootstrap / lifecycle / `runtime_access` / `service_router` / `schedule` formal homes 必须继续收敛到单一 north-star 主链，不得新增 second orchestration root、builder folklore、shadow helper carrier 或 helper-owned public surface。 | 推荐继续复用现有 `control/runtime_access.py`、`core/coordinator/services/schedule_service.py`、`services/execution.py`，并把 platform/entity 读面收回 runtime-owned service/read port，而不是再造 helper root。 |
| HOT-33 | service-router forwarding families、diagnostics/helper duplication、`LiproEntity` runtime strategy 与 `schedule.py` runtime surface 必须完成 formalize / deduplicate，并保持 outward behavior 稳定。 | 研究已定位 4 个热点：router 四层转发、diagnostics helper/support 双生层、platform/entity 直接 runtime 读取、Phase 69 之后仍缺少对 `schedule_service` 的显式 no-growth guard。 |
| TYP-21 | runtime / lifecycle / service / auth seams 必须维持或提升 typed contract honesty，不得用 `Any` / compatibility shell 掩盖 boundary drift。 | 推荐把 platform/entity 改走显式 runtime service protocol（优先 `state_service` / `device_refresh_service` 家族），并补齐 `runtime_types.py` typed surface；避免继续放大 `CoordinatorEntity[Any]` 与 `object` 风格 helper。 |
| TST-22 | 大型 suites 与治理 guards 必须继续 topicize / focused freeze，新增 route / hotspot / no-growth guards 覆盖 `Phase 72 -> 74` touched scope。 | 研究确认现有 topical suites 已覆盖 schedule/diagnostics/system-health/platform，但缺少专门冻结 `schedule_service`、platform/entity 读口、diagnostics helper outward-home 的 Phase 73 meta guard。 |
| QLT-30 | touched scope 必须在 `uv run ruff check .`、`uv run mypy --follow-imports=silent .`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check` 与 focused/full pytest 下持续全绿。 | 本地环境已验证 `uv`、`ruff`、`mypy`、`pytest` 与 Home Assistant dev stack 可用；建议把 focused command 绑定到 router/diagnostics/platform/meta 四组套件。 |
</phase_requirements>

## Summary

Phase 73 不该再“发明”新的 service 或 runtime root。仓内在 `2026-03-25` 这棵树上，`schedule.py` 已经不再直连 `coordinator.protocol_service`，而是走 `coordinator.schedule_service`；真正未完全收口的，是 **router/diagnostics/helper 的重复转发语义** 与 **platform/entity 的 runtime 读取仍停留在过于裸露的 live coordinator shape**。因此，规划重点应放在“继续把调用关系说实话”，而不是再造一层 façade。

最有价值的事实是：runtime plane 已经提供了可复用的正式 service 面——`CoordinatorScheduleService`、`CoordinatorStateService`、`CoordinatorDeviceRefreshService`、`CoordinatorCommandService`。control plane 也已拥有唯一 outward read home `control/runtime_access.py`。所以本 phase 的最佳做法，是让 **control 继续走 `runtime_access`，platform/entity 则走 runtime-owned read port**；不要让 platform 为了摆脱 `entry.runtime_data` 又反向 import `control/runtime_access.py`，那会直接违反现有 `ENF-IMP-PLATFORM-SHELL-NO-CONTROL-LOCATOR` 规则。

**Primary recommendation:** 把 Phase 73 规划成“三段收口”：`service_router` 去重、diagnostics/helper 单一 outward home、platform/entity 切到 runtime-owned typed read port，并用新的 Phase 73 meta guards 冻结这些边界。

## Project Constraints (from CLAUDE.md)

- `AGENTS.md` 是 canonical repository contract；若与 `CLAUDE.md` 冲突，以 `AGENTS.md` 为准。
- Claude 兼容读序应从 `AGENTS.md` → `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` → `.planning/*` → baseline/reviews → `docs/developer_architecture.md` → `docs/adr/README.md`。
- 当前焦点与下一步动作以 `.planning/STATE.md` 为准。
- 不创建、也不依赖 `agent.md`。

## Standard Stack

### Core
| Library / Surface | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `homeassistant` | `2026.3.1` | Integration contract for `runtime_data`, diagnostics, system health, services | 项目已 pin 到该版本；官方 quality-scale 规则直接要求 `runtime_data`、diagnostics、system health 等集成面。 |
| `custom_components/lipro/core/coordinator/services/schedule_service.py` | repo-local | Runtime-owned schedule surface | 已存在正式 runtime service，避免 `services/schedule.py` 再碰 protocol details。 |
| `custom_components/lipro/core/coordinator/services/state_service.py` | repo-local | Read-only runtime device/state access | 这是比 `coordinator.devices` 更诚实的读口；适合 platform/entity 收敛。 |
| `custom_components/lipro/control/runtime_access.py` | repo-local | Control-plane runtime read model | baseline 与 public-surface 文档都已把它定为 control 的唯一 outward runtime read home。 |
| `custom_components/lipro/services/execution.py` | repo-local | Shared auth/error execution | schedule/diagnostics service path 的正式 auth/error 语义已统一到这里。 |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest-homeassistant-custom-component` | `0.13.317` | HA custom integration test harness | 行为回归、service call、config entry、entity/platform smoke。 |
| `pytest` | `9.0.0` | Test runner | Focused topical suites 与 full suite。 |
| `mypy` | `1.19.1` | Typed seam verification | 验证 `runtime_types.py`、service protocol、helper port honesty。 |
| `ruff` | `0.15.4` | Lint / import / complexity guard | Phase 73 touches import locality 与 hotspot trimming。 |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| 再造新的 schedule façade | 继续用现成 `CoordinatorScheduleService` | 当前仓树已具备正式 runtime-owned schedule surface，再造新层只会制造第二故事线。 |
| 让 platform import `control/runtime_access.py` | 暴露 runtime-owned `state_service` / read port | 后者符合现有 dependency guard；前者会破坏 platform shell headless contract。 |
| 继续保留 `helpers.py` + `helper_support.py` 双 outward 语义 | 固定单一 outward helper home，另一个仅私有本地 support | 可读性与 guard 可冻结性更高。 |

**Installation:**
```bash
uv sync --extra dev
```

**Version verification:** 2026-03-25 已本地核验：`uv run python` = `3.14.3`、`homeassistant` = `2026.3.1`、`pytest-homeassistant-custom-component` = `0.13.317`、`pytest` = `9.0.0`、`ruff` = `0.15.4`、`mypy` = `1.19.1`。

## Architecture Patterns

### Recommended Project Structure
```text
custom_components/lipro/
├── control/                    # public control adapters + typed read surfaces
├── services/                   # HA service callback shaping / translation only
├── core/coordinator/services/  # runtime-owned read/write service surfaces
├── helpers/                    # HA platform projection helpers only
└── entities/                   # HA entity adapters over runtime/domain truth
```

### Pattern 1: Root adapters stay thin
**What:** `diagnostics.py`、`system_health.py` 只做 HA callback 适配，不拥有新的 runtime/control truth。
**When to use:** 所有根层 HA entrypoint。
**Example:**
```python
# Source: custom_components/lipro/diagnostics.py
async def async_get_config_entry_diagnostics(hass, entry):
    return await _async_get_config_entry_diagnostics_surface(
        hass,
        entry,
        get_anonymous_share_manager=_get_anonymous_share_manager_for_diagnostics,
        async_redact_data=async_redact_data,
    )
```

### Pattern 2: Runtime-owned service surfaces, not service-layer protocol peeking
**What:** service callback home 只调 runtime service；protocol context 拼装留在 runtime plane。
**When to use:** `schedule`、command-like capability reads、未来任何 device-scoped runtime call。
**Example:**
```python
# Source: custom_components/lipro/core/coordinator/services/schedule_service.py
@dataclass(slots=True)
class CoordinatorScheduleService:
    protocol_service: CoordinatorProtocolService

    async def async_get_schedules(self, device):
        return await self.protocol_service.async_get_device_schedules_for_device(device)
```

### Pattern 3: Control reads runtime through `runtime_access`
**What:** diagnostics / system health / router support 继续只走 `control/runtime_access.py` outward home。
**When to use:** control-plane runtime enumeration、entry→coordinator lookup、diagnostics/system-health projections。
**Example:**
```python
# Source: custom_components/lipro/control/diagnostics_surface.py
projection = build_runtime_diagnostics_projection(entry)
devices_info = [
    build_device_diagnostics_fn(device)
    for device in iter_runtime_devices_for_entry(entry)
]
```

### Pattern 4: Platform/entity read via runtime-owned read ports
**What:** platform/entity 不 import `control/runtime_access.py`，也不直接遍历 `entry.runtime_data` / `coordinator.devices`；改走 runtime-owned typed surface。
**When to use:** `helpers/platform.py` entity construction、`LiproEntity.device` live refresh strategy。
**Example:**
```python
# Source: custom_components/lipro/core/coordinator/services/state_service.py
@dataclass(slots=True)
class CoordinatorStateService:
    def get_device(self, serial):
        return self.state_runtime.get_device_by_serial(serial)
```

### Anti-Patterns to Avoid
- **Platform 借 control locator 自救：** 绝不要让 `helpers/platform.py` 为了摆脱 `entry.runtime_data` 而改 import `control/runtime_access.py`。
- **Router 四层空转：** `service_router.py` → `handlers.py` → service helper → support helper 若只是在转参数，就是热点噪音。
- **Helper 名称伪装 ownership：** `helper_support.py` 若被多个 outward modules 当 public helper 使用，就已经在长第二 outward home。
- **Typed seam 借 `Any` 脱责：** `CoordinatorEntity[Any]`、`dict[str, object]`、`object` 参数若越过真正边界，会掩盖 drift。

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Service auth / reauth / API error mapping | 每个 service 自己写 auth chain | `custom_components/lipro/services/execution.py` | 统一翻译 key、reauth 语义与 failure taxonomy。 |
| Schedule mesh context shaping | 手写 gateway/member 解析 | `build_schedule_mesh_context()` + `CoordinatorScheduleService` | mesh/IR gateway 细节已集中到 runtime plane。 |
| Control runtime snapshots | 在 diagnostics/system_health/service helper 里手搓 dict | `control/runtime_access.py` + `control/telemetry_surface.py` | 现有 baseline 已规定它们是唯一 outward home。 |
| Platform/entity live device lookup | 直接读 `coordinator.devices` 或重新遍历 config entries | runtime-owned read port（优先 `state_service` / `device_refresh_service` family） | 避免把 runtime registry shape 洩漏到 adapter 层。 |
| Diagnostics capability polling | 新写 coordinator auth/fault-tolerance helper | 继续复用 `services/diagnostics/helpers.py` 中 shared execution path | 认证退避与 per-coordinator degrade 已有成熟行为测试。 |

**Key insight:** 本 phase 最大价值不是“再整理一次文件名”，而是把 **谁拥有 read/write/runtime truth** 说清楚，并用 typed contract + meta guard 把它冻结。

## Runtime State Inventory

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — 代码与 planning 审计里未发现数据库/`.storage`/外部 datastore 把 `service_router`、`runtime_access`、`schedule` 等符号作为持久键保存；`ConfigEntry.runtime_data` 仅是内存态。 | **Code edit only**；无需数据迁移。 |
| Live service config | None repo-visible — HA service registry 由代码注册动态生成；未发现 UI-only workflow/外部 SaaS 配置把这些 helper 名称作为独立配置项。 | **Code edit only**；本地运行实例需 reload integration 以刷新服务面。 |
| OS-registered state | None — 搜索未发现 systemd/launchd/pm2/Task Scheduler 等把这些 phase 目标绑定为 OS 注册对象。 | 无。 |
| Secrets/env vars | None — 未发现环境变量名或 secrets key 直接绑定 `runtime_access`/`service_router`/`schedule` 家族。 | 无。 |
| Build artifacts | `.mypy_cache/`、`.pytest_cache/`、`.venv/` 已存在，且会缓存 touched module 的旧分析结果。 | **Code edit + cache refresh**：重跑 `uv run mypy` / `uv run pytest` / `uv run ruff check .`；无需迁移。 |

## Common Pitfalls

### Pitfall 1: 用错收口方向
**What goes wrong:** 为了去掉 `entry.runtime_data` 直接读取，平台层反向 import `control/runtime_access.py`。
**Why it happens:** `runtime_access` 已经是现成 read-model，看起来最顺手。
**How to avoid:** 对 control 保持 `runtime_access`，对 platform/entity 选择 runtime-owned read port。
**Warning signs:** `helpers/platform.py` 新增 `from ..control.runtime_access import ...`。

### Pitfall 2: 误判 `schedule.py` 仍直连 protocol
**What goes wrong:** 计划里又新增一个“正式 schedule runtime service”。
**Why it happens:** 审计语句沿用了旧表述。
**How to avoid:** 以当前树为准：`services/schedule.py` 已调 `coordinator.schedule_service`，真正缺的是 no-growth guard 与余留命名/测试同步。
**Warning signs:** 新建第二个 schedule façade / wrapper，或把 `schedule_service.py` 再包一层。 

### Pitfall 3: diagnostics/helper 只换文件名，不减 outward homes
**What goes wrong:** `helpers.py`、`helper_support.py`、`handlers.py` 仍都对外暴露相似协作语义。
**Why it happens:** 只做局部搬运，没有定义“谁是 outward home”。
**How to avoid:** 固定一个 outward helper home，其余模块只允许局部 importer；新增 import-locality guard。
**Warning signs:** 新测试/新模块同时 import `helpers.py` 与 `helper_support.py`。

### Pitfall 4: typed contract 没落到 runtime_types
**What goes wrong:** 生产代码改走新 read port，但 `runtime_types.py` 不承认它，最后靠 `Any` 或 `MagicMock` 维持测试。
**Why it happens:** 先改实现，后补协议，导致 contract honesty 倒挂。
**How to avoid:** Phase 73 任何新的 runtime read surface 先写 Protocol，再迁移 helper/entity/platform。
**Warning signs:** `runtime_types.py` 不含新 surface，mypy 只能靠宽类型通过。

## Code Examples

Verified patterns from current tree and official HA guidance:

### Thin root adapter
```python
# Source: custom_components/lipro/system_health.py
async def async_register(hass, register):
    del hass
    register.async_register_info(system_health_info)
```

### Runtime-owned schedule surface
```python
# Source: custom_components/lipro/core/coordinator/services/schedule_service.py
async def async_add_schedule(self, device, days, times, events):
    return await self.protocol_service.async_add_device_schedule_for_device(
        device, days, times, events
    )
```

### Shared service execution
```python
# Source: custom_components/lipro/services/execution.py
async def async_execute_coordinator_call(coordinator, *, call, raise_service_error, handle_api_error=None):
    await _async_ensure_authenticated(coordinator)
    return await call()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `schedule.py` 直接碰 protocol-shaped operations | `CoordinatorScheduleService` 作为 runtime-owned schedule surface | Phase 69 / v1.17 closeout (`2026-03-24`) | Phase 73 不该重造 service，只需补 guard 与整理剩余心智负担。 |
| control surfaces 自己拼 runtime internals | `runtime_access.py` + typed projections | Phase 43、48、70 | control side boundary 已定型，后续应减复杂度而非迁移 owner。 |
| helper/support 大文件混杂 outward 语义 | support cluster inward split + locality guards | Phase 69、70 | 现在的目标是再缩窄 outward home，而不是回退到 megafile。 |
| platform/entity 直接裸读 coordinator shape | runtime-owned service/read port（本 phase 待完成） | 仍在进行中 | 这是 Phase 73 最大剩余缺口。 |

**Deprecated/outdated:**
- “再新建一层 helper/forwarding shell 让文件更薄”——这会违背单一 formal home 原则。
- “platform 借 `control/runtime_access.py` 读 runtime”——与现有 dependency guard 冲突。

## Open Questions

1. **platform/entity 应收口到 `state_service` 还是 `device_refresh_service`？**
   - What we know: 两者都已存在；`state_service` 更像纯读口，`device_refresh_service` 同时持有 refresh 语义。
   - What's unclear: 是否希望 platform/entity 统一只接触一个 runtime-owned read surface。
   - Recommendation: 读操作优先 `state_service`，refresh/registry-trigger 仍留给 `device_refresh_service`；若只允许一个 outward read port，就以 `state_service` 为主。 

2. **diagnostics outward helper home 最终保留 `helpers.py` 还是收进 `handlers.py`？**
   - What we know: file-matrix 已把 `helpers.py` 记为稳定 helper home，`helper_support.py` 记为 mechanics support seam。
   - What's unclear: 继续保留双模块是否仍值得。
   - Recommendation: 维持 `helpers.py` 作为 outward helper home，把 `helper_support.py` 严格私有化；若行数允许，可直接合并 support 逻辑回 `helpers.py`。

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | 全部 Python / test / lint / script 命令 | ✓ | `0.10.9` | — |
| `uv run python` | 项目实际解释器 | ✓ | `3.14.3` | **必须用它**；系统 `python3` 仅 `3.13.5`，不符合项目目标基线。 |
| `homeassistant` | Integration contract + tests | ✓ | `2026.3.1` | — |
| `pytest` | Focused/full suites | ✓ | `9.0.0` | — |
| `pytest-homeassistant-custom-component` | HA custom component test harness | ✓ | `0.13.317` | — |
| `ruff` | Lint gate | ✓ | `0.15.4` | — |
| `mypy` | Type gate | ✓ | `1.19.1` | — |

**Missing dependencies with no fallback:**
- None.

**Missing dependencies with fallback:**
- None; 但必须避免裸 `python3`，统一用 `uv run python`。

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest 9.0.0` + `pytest-homeassistant-custom-component 0.13.317` |
| Config file | `pyproject.toml` |
| Quick run command | `uv run pytest -q tests/services/test_services_schedule.py tests/services/test_services_diagnostics.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_init_service_handlers_schedules.py tests/platforms/test_entity_behavior.py tests/platforms/test_platform_entities_behavior.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_phase69_support_budget_guards.py tests/meta/test_phase70_governance_hotspot_guards.py` |
| Full suite command | `uv run pytest -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ARC-19 | control/runtime/service homes remain singular | meta + focused integration | `uv run pytest -q tests/services/test_services_registry.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py` | ✅ |
| HOT-33 | schedule/diagnostics/platform/entity outward behavior stays stable during dedup | unit + service + behavior | `uv run pytest -q tests/services/test_services_schedule.py tests/services/test_services_diagnostics.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_init_service_handlers_schedules.py tests/platforms/test_entity_behavior.py tests/platforms/test_platform_entities_behavior.py` | ✅ |
| TYP-21 | new runtime read ports / contracts stay typed | type + focused unit | `uv run mypy --follow-imports=silent .` | ✅ |
| TST-22 | add Phase 73 no-growth guards | meta | `uv run pytest -q tests/meta/test_phase73_service_runtime_surface_guards.py` | ❌ Wave 0 |
| QLT-30 | touched scope passes full quality gate | lint + type + policy + meta + pytest | `uv run ruff check . && uv run mypy --follow-imports=silent . && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q` | ⚠️ 部分 guard 待补 |

### Sampling Rate
- **Per task commit:** `uv run pytest -q` 跑对应 topical suites + `uv run mypy --follow-imports=silent .`（仅 touched surface）
- **Per wave merge:** `uv run ruff check .` + `uv run python scripts/check_architecture_policy.py --check` + topical pytest bundle
- **Phase gate:** full lint/type/policy green + `uv run pytest -q`

### Wave 0 Gaps
- [ ] `tests/meta/test_phase73_service_runtime_surface_guards.py` — 冻结 `schedule_service`、platform/entity runtime read port、diagnostics helper outward-home。
- [ ] `tests/core/coordinator/services/test_schedule_service.py` — 直接验证 runtime-owned schedule surface，而不是只靠 service-layer 间接覆盖。
- [ ] `tests/platforms/test_platform_runtime_surface.py`（或并入既有平台测试）— 明确证明 platform/entity 不再裸读 `entry.runtime_data` / `coordinator.devices`。

## Sources

### Primary (HIGH confidence)
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` - north-star planes, dependency direction, formal homes
- `.planning/baseline/PUBLIC_SURFACES.md` - canonical public surfaces for control/runtime/service/telemetry
- `.planning/baseline/DEPENDENCY_MATRIX.md` - concrete rules for `runtime_access`, `telemetry_surface`, `schedule.py`, platform shell locality
- `.planning/reviews/RESIDUAL_LEDGER.md` - already-closed residual families and current carry-forward truth
- `.planning/reviews/V1_19_TERMINAL_AUDIT.md` - Phase 73 seed list
- `pyproject.toml` - project/runtime/test toolchain truth
- `https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/runtime-data/` - official `runtime_data` rule
- `https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/diagnostics/` - official diagnostics requirement
- `https://developers.home-assistant.io/docs/core/integration_system_health/` - official system health contract
- `https://developers.home-assistant.io/docs/dev_101_services/` - official service action/error handling guidance
- `https://developers.home-assistant.io/docs/integration_fetching_data/` - official coordinator/data-fetching guidance

### Secondary (MEDIUM confidence)
- `.planning/reviews/V1_17_EVIDENCE_INDEX.md` - confirms Phase 69 schedule/runtime-access closeout intent
- `scripts/check_file_matrix_registry.py` - machine-readable file-home labels used by governance tooling

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - 主要由本地 `pyproject.toml` / installed versions + official HA docs验证。
- Architecture: MEDIUM - formal homes 很清晰，但 platform/entity 最终应收口到 `state_service` 还是 `device_refresh_service` 仍需 planner 做一次裁决。
- Pitfalls: HIGH - 现有 dependency/public-surface/meta guards 已把多数回退路径写成显式规则。

**Research date:** 2026-03-25
**Valid until:** 2026-04-24
