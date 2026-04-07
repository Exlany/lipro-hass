# Phase 69: Residual read-model closure, quality-balance hardening, and honest OSS contract - Research

**Researched:** 2026-03-24
**Domain:** runtime read-model residual / schedule-service residual / checker balance / open-source contract continuity
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

1. `custom_components/lipro/control/runtime_access.py` 继续是唯一 control-plane runtime outward home；`runtime_access_support.py` 只能 inward formalization，不能长回第二 root。
2. schedule public/service path 必须继续把 protocol-shaped parameter choreography 往下压；不允许为“收口”新建第二条 schedule/service story。
3. `custom_components/lipro/core/protocol/boundary/*` 继续是协议 decode authority；MQTT/API wrapper residue 的处理只能 thin inward，不得把 decode/auth/service truth 重新拉回 helper shell。
4. 质量补强必须增加 behavior/integration/checker coverage，而不是只添加更多 prose-coupled meta/budget tests。
5. 开源治理只能讲 honest contract：允许明确记录 live-docs on `main`、machine-readable constraints 的不足与单维护者现实，但不允许虚构组织承诺。
6. `v1.16` 保持 closeout-ready baseline 身份；本 phase 只承接 residual，不回滚 `Phase 68` 的 current-story 完成态。

### Claude's Discretion

- 允许决定 `runtime_access_support.py` 与 `runtime_infra.py` 的最优 inward split 粒度，但必须避免新增 public root。
- 允许决定是补齐 tag-aware docs strategy，还是把 live-docs on `main` 明确写成 honest contract；前提是所有对外入口讲同一条真话。
- 允许调整 focused tests / scripts tests / integration suites 的组合，但必须解释为什么新门禁比旧 meta-only 方案更平衡。

### Deferred Ideas (OUT OF SCOPE)

- `v1.16` 的 milestone archive / complete 流程本身
- 全仓统一重命名所有 historical stable-import homes
- 全面替换所有 meta budget tests；本 phase 只做平衡与补强，不做推倒重来
- 超出 residual family 的新功能、新集成或新的组织流程承诺
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GOV-53 | 区分 `v1.16` archived baseline 与 `v1.17` residual route | `## Summary` / `## Validation Architecture` |
| ARC-16 | runtime/schedule/protocol-service 继续收口到显式 read-model / runtime-intent seam | `## Current Residual Families` / `## Architecture Patterns` |
| HOT-26 | wrapper/shim/lazy-import residue 继续削减 | `## Current Residual Families` / `## Common Pitfalls` |
| HOT-27 | support-only family 要有 no-growth budget 与 discoverability contract | `## Architecture Patterns` / `## Validation Architecture` |
| OSS-09 | docs URL / HA support / continuity wording 讲同一条 honest story | `## Current Residual Families` / `## Common Pitfalls` |
| TST-19 | checker 行为覆盖、focused integration、meta-shell maintainability 更平衡 | `## Validation Architecture` |
| QLT-27 | lint / mypy / checker / pytest gate 继续绿色 | `## Environment Availability` / `## Validation Architecture` |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- `AGENTS.md` 是仓库正式契约；`CLAUDE.md` 不新增第二套规则。
- 读序固定为 `AGENTS.md` → `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` → `.planning/*`。
- 当前里程碑、阶段状态、推荐下一步以 `.planning/STATE.md` 为准。
- 不创建或依赖 `agent.md`。

## Summary

Phase 69 只应处理 4 条 carry-forward residual：`runtime_access_support.py`/`runtime_infra.py` 的 inward read-model formalization、`services/schedule.py` 与 `CoordinatorProtocolService` 的 protocol-shaped choreography 下压、checker coverage 与 focused integration 的再平衡、以及 `pyproject.toml` / `manifest.json` / `docs/README.md` / `SECURITY.md` / `.github/CODEOWNERS` 的 honest public contract continuity。现有 formal home 已经基本正确，风险不在“缺根”，而在“为了变薄又长出第二根”。

当前最值钱的动作不是新 facade，而是收窄 owner 边界：`runtime_access.py` 继续做唯一 outward home；`core/protocol/boundary/*` 继续做唯一 decode authority；schedule service 只保留 user intent、日志与错误翻译；open-source continuity 继续围绕 live docs on `main` + 单维护者真相同步，不虚构 tag-aware docs reality 或 hidden delegate。

**Primary recommendation:** 只做 inward thinning，不做 outward reroot；新增验证优先补 `support budget guard`、`check_translations.py` 直测、以及把 schedule-focused protocol tests 接入 `69-02` focused gate。

## Standard Stack

### Core
| Asset | Version / Source | Purpose | Why Standard |
|------|------------------|---------|--------------|
| `custom_components/lipro/control/runtime_access.py` | repo-local | control-plane runtime outward home | 已被 locked decision 与 baseline 固定 |
| `custom_components/lipro/core/coordinator/services/protocol_service.py` | repo-local | runtime-intent → protocol bridge | 已是正式 runtime protocol service |
| `custom_components/lipro/core/protocol/boundary/*` | repo-local | REST/MQTT decode authority | 已被 locked decision 固定 |
| `scripts/check_architecture_policy.py` + `scripts/check_file_matrix.py` | repo-local | architecture/governance blocking checkers | 已进入 CI 与 pre-push truth |

### Supporting
| Tool / Asset | Version | Purpose | When to Use |
|-------------|---------|---------|-------------|
| `uv` | `0.10.9` | 统一 Python 命令入口 | 所有 lint/type/test/checker |
| `pytest` | `9.0.0` | unit/meta/integration | focused 与 phase gate |
| `mypy` | `1.19.1` | strict typing | full phase gate |
| `ruff` | `0.15.4` | lint gate | full phase gate |
| `custom_components/lipro/quality_scale.yaml` | repo-local | machine-readable HA support posture | metadata/docs continuity 调整时 |

## Current Residual Families

| Residual | Current Evidence | Closure Direction |
|----------|------------------|-------------------|
| runtime read-model/support residual | `runtime_access.py` 仍大面积 re-export `_support`；`runtime_access_support.py` 同时混合 entry/coordinator/device/telemetry/debug | 在 support 内按 read-model family 继续 inward split，但 outward 仍只经 `runtime_access.py` |
| schedule/service wrapper residual | `services/schedule.py` 仍组装 `mesh_gateway_id` / `mesh_member_ids` 并层层传给 `CoordinatorProtocolService` | 让 service 只表达 device + user intent，把 protocol-shaped 参数编排继续下压 |
| checker coverage / integration balance residual | `coverage_diff.py` 有直测；`check_translations.py` 只有 meta/CI 引用；`69-02` focused bundle 未覆盖 `test_protocol_service.py` / `test_api_schedule_service.py` | 给 blocking checker 增 direct behavior test；把 schedule-protocol focused tests 纳入 gate |
| OSS metadata/docs continuity residual | `pyproject.toml` 与 `manifest.json` 使用 `blob/main` 文档 URL；`SECURITY.md` / `CODEOWNERS` / runbook 明确单维护者与 freeze drill | 继续讲 live-docs on `main` 的 honest contract，并同步 machine-readable support / continuity wording |

## Architecture Patterns

### Pattern 1: Outward home 固定，support 只 inward formalize
**What:** `runtime_access.py` 继续是唯一 control-plane runtime outward home；support seam 只做 typed/read-model support。  
**When to use:** 任何 entry lookup、coordinator view、telemetry projection、device lookup 的继续收口。  
**Example:** `runtime_access.py` 统一 re-export `_support` helper，而 diagnostics/system-health/maintenance 继续经 `runtime_access.py` 消费。

### Pattern 2: Schedule service 只持有 runtime intent
**What:** `services/schedule.py` 只保留 user intent 归一化、日志、翻译键与 shared execution；不要让 service 继续像 protocol parameter compiler。  
**When to use:** `get/add/delete schedule` residual closeout。  
**Example:** `async_call_schedule_service()` 统一包装执行，但 mesh/member/device-type 编排应继续向 protocol-side collaborator 下压。

### Pattern 3: Wrapper residue 只能 owner 化，不能升格 authority
**What:** `client.py`、`endpoint_surface.py`、`topics.py`、`payload.py` 这类薄层只能作为 stable import home / localized adapter。  
**When to use:** import cycle、discoverability、稳定 import 名称无法一次性删除时。  
**Example:** MQTT lazy import 只负责桥接到 `core.protocol.boundary`，不得自长 decode truth。

### Anti-Patterns to Avoid
- **把 `runtime_access_support.py` 拆成更多 outward helper：** 会把 support seam 长成第二 root。
- **横向挪动 schedule 参数编排：** 从 `schedule.py` 挪到另一个 helper 仍然是同一 residual。
- **把 lazy-import adapter 当 authority：** `topics.py` / `payload.py` / `message_processor.py` 不能重新定义 decode truth。
- **只改 prose，不改 machine-readable truth：** `pyproject.toml` / `manifest.json` / `quality_scale.yaml` / `CODEOWNERS` 不同步，文档就会漂移。

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| runtime outward home | 新 `runtime_*` facade/root | 继续使用 `control/runtime_access.py` | formal home 已确定；新根只会制造 discoverability debt |
| protocol decode | schedule/MQTT 自定义解析层 | `core/protocol/boundary/*` | authority 已固定，重复解析会分叉真相 |
| service auth/error flow | schedule 私有执行链 | `services/execution.py` + shared executor | 避免复制 coordinator auth/error story |
| governance continuity | 第二套 release/docs/support story | 现有 `docs/README.md` + `SECURITY.md` + `CODEOWNERS` + runbook | 公开契约必须单线叙事 |

**Key insight:** 本 phase 的价值来自“减少第二故事线”，而不是“发明更漂亮的新结构”。

## Common Pitfalls

### Pitfall 1: support seam outward creep
**What goes wrong:** 新 consumer 直接 import `runtime_access_support.py`，绕开 `runtime_access.py`。  
**How to avoid:** 新增 Phase 69 support budget/locality guard，禁止 support seam 被新 outward consumer 直接消费。

### Pitfall 2: schedule 去协议化只做了一半
**What goes wrong:** `schedule.py` 不再直接调底层，但仍持有 mesh/member/device-type 编排。  
**How to avoid:** focused tests 同时证明 service 层更薄、protocol service/API schedule tests 仍通过。

### Pitfall 3: checker balance 继续偏 meta-only
**What goes wrong:** 只加更多 `tests/meta/*`，却不给 blocking script 直测。  
**How to avoid:** 至少补 `check_translations.py` 的直接行为测试，并保留 meta tests 只做 contract guard。

### Pitfall 4: honest contract 漂移
**What goes wrong:** 文档写 release-aware/tag-aware reality，但 metadata 仍指向 `blob/main`，或暗示隐藏 delegate。  
**How to avoid:** 明确把 live docs on `main`、single-maintainer truth、freeze drill 同步到所有 outward entrypoints。

## Code Examples

### Outward home 只聚合 support
```python
# Source: custom_components/lipro/control/runtime_access.py
build_runtime_entry_view = _support.build_runtime_entry_view
find_runtime_device = _support.find_runtime_device
iter_runtime_entries = _support.iter_runtime_entries
```

### Schedule service 仍是 shared executor + protocol service 薄桥接
```python
# Source: custom_components/lipro/services/schedule.py
return await async_call_schedule_service(
    coordinator,
    device,
    protocol_call=coordinator.protocol_service.async_add_device_schedule,
    call_args=(days, times, events),
    ...
)
```

### MQTT thin adapter 继续回到 boundary authority
```python
# Source: custom_components/lipro/core/mqtt/topics.py
canonical = _boundary_decoder_module().decode_mqtt_topic_payload(
    topic,
    expected_biz_id=expected_biz_id,
).canonical
```

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | 全部 Python gate | ✓ | `0.10.9` | — |
| `uv run python` | repo runtime | ✓ | `3.14.3` | — |
| `pytest` | focused/full suite | ✓ | `9.0.0` | — |
| `mypy` | type gate | ✓ | `1.19.1` | — |
| `ruff` | lint gate | ✓ | `0.15.4` | — |
| `gh` | release/runbook verification | ✓ | `2.88.1` | 不做本地 release rehearsal |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest 9.0.0` |
| Config file | `pyproject.toml` |
| Quick run command | `uv run pytest -q tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_unload_reload.py tests/services/test_maintenance.py tests/services/test_services_schedule.py tests/core/coordinator/services/test_protocol_service.py tests/core/api/test_api_schedule_service.py tests/core/mqtt/test_message_processor.py tests/core/mqtt/test_topics.py tests/test_refactor_tools.py tests/meta/test_toolchain_truth.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` |
| Full suite command | `uv run pytest -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| GOV-53 | `v1.16` / `v1.17` truth 不混写 | meta | `uv run pytest -q tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py` | ✅ |
| ARC-16 | runtime read-model + schedule intent 下压 | unit + focused integration | `uv run pytest -q tests/core/test_diagnostics.py tests/core/test_system_health.py tests/services/test_maintenance.py tests/services/test_services_schedule.py tests/core/coordinator/services/test_protocol_service.py tests/core/api/test_api_schedule_service.py` | ✅ |
| HOT-26 | wrapper/lazy-import 不回流 authority | unit + meta | `uv run pytest -q tests/core/mqtt/test_message_processor.py tests/core/mqtt/test_topics.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py` | ✅ |
| HOT-27 | support family no-growth / discoverability | meta budget | `uv run pytest -q tests/meta/test_phase69_support_budget_guards.py` | ❌ Wave 0 |
| OSS-09 | docs/support/security/continuity honest contract | meta | `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` | ✅ |
| TST-19 | checker 直测 + meta balance | unit + meta | `uv run pytest -q tests/test_refactor_tools.py tests/meta/test_toolchain_truth.py tests/meta/test_governance_guards.py` | ✅ |
| QLT-27 | full gate 继续绿色 | lint + type + checker + pytest | `uv run ruff check . && uv run mypy --follow-imports=silent . && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q` | ✅ |

### Sampling Rate
- **Per task commit:** 运行对应 focused suite。  
- **Per wave merge:** 运行上方 Quick run command。  
- **Phase gate:** `ruff` + `mypy` + `check_architecture_policy` + `check_file_matrix` + focused pytest；涉及 metadata/docs 时追加 `tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py`。

### Wave 0 Gaps
- [ ] `tests/meta/test_phase69_support_budget_guards.py` —— 冻结 `runtime_access_support.py`、`runtime_infra.py`、`services/schedule.py`、`core/api/client.py`、`core/api/endpoint_surface.py`、`core/mqtt/payload.py` 的 no-growth / locality 语义。
- [ ] `tests/test_refactor_tools.py` —— 增加 `scripts/check_translations.py` 的直接行为测试；当前只有 CI/meta 引用，没有脚本直测。
- [ ] `69-02` focused verification —— 把 `tests/core/coordinator/services/test_protocol_service.py` 与 `tests/core/api/test_api_schedule_service.py` 接入，避免 schedule 去协议化缺少行为 proof。

## Sources

### Primary (HIGH confidence)
- `AGENTS.md`, `CLAUDE.md`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`
- `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/69-CONTEXT.md`
- `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/69-VALIDATION.md`
- `custom_components/lipro/control/runtime_access.py`, `custom_components/lipro/control/runtime_access_support.py`, `custom_components/lipro/runtime_infra.py`, `custom_components/lipro/services/schedule.py`, `custom_components/lipro/core/coordinator/services/protocol_service.py`
- `pyproject.toml`, `custom_components/lipro/manifest.json`, `custom_components/lipro/quality_scale.yaml`, `docs/README.md`, `SUPPORT.md`, `SECURITY.md`, `.github/CODEOWNERS`
- `tests/test_refactor_tools.py`, `tests/meta/test_toolchain_truth.py`, `tests/meta/test_governance_release_contract.py`, `tests/meta/test_version_sync.py`, `tests/meta/test_dependency_guards.py`

### Secondary (MEDIUM confidence)
- https://developers.home-assistant.io/docs/creating_integration_manifest
- https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/integration-owner/

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — 基于现有 repo formal homes、CI 与已装工具版本。
- Architecture: HIGH — 直接受 north-star、baseline 与 locked decisions 约束。
- Pitfalls: HIGH — 直接来自当前 residual 文件、现有 guards 与 69 validation gap。

**Research date:** 2026-03-24
**Valid until:** 2026-03-31
