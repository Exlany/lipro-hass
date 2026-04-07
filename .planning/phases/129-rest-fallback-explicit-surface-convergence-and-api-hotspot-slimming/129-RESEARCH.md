# Phase 129: rest fallback explicit-surface convergence and api hotspot slimming - Research

**Researched:** 2026-04-01
**Domain:** REST child façade 显式 surface 收口 + status fallback binary-split support 瘦身
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- 不新增第二个 REST root；`LiproRestFacade` 仍是唯一正式 REST child façade。
- 不改变 outward behavior；所有 refactor 必须以 focused/full tests 证明语义不变。
- `status_fallback_support.py` 只能 inward 收口职责，不能把 fallback truth 再散落回 wrapper 或 endpoint callers。
- phase 只覆盖 REST hotspot；`command_runtime.py` / `firmware_update.py` 留给后续 `Phase 130`。
- external continuity / private fallback 不在本 phase 伪装为已解决，它们属于后续 governance closeout 议题。

### Claude's Discretion
- 是否通过显式 wrapper/property 替代部分 generic helper。
- 是否将 fallback setup/context 的内部结构收口为更直观的 internal helper，只要不新增 public surface。
- 新增或调整 focused tests 的具体粒度与命名。

### Deferred Ideas (OUT OF SCOPE)
- `command_runtime.py` / `firmware_update.py` 的 deeper decomposition
- repo-wide terminal audit final report 与 governance continuity closeout
- external delegate / private disclosure fallback 现实本身的外部补位
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ARC-40 | `rest_facade.py` 降低 metaprogramming / generic delegation 负担 | 推荐切片 1-2、模式 1、风险 1-2 |
| HOT-59 | `status_fallback_support.py` 理清 setup/context/accumulator/primary path | 推荐切片 3、模式 2、风险 3 |
| TST-50 | 补齐 focused regressions | 测试策略、Validation Architecture |
| QLT-52 | 不靠 helper magic 掩盖正式 surface，边界更清晰 | 推荐切片 1-3、Pitfalls 1-3 |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- `AGENTS.md` 仍是仓库规则真源；`CLAUDE.md` 不创建第二套规则。
- 研究/规划读取顺序必须以 `AGENTS.md` → `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` → `.planning/*` 为主。
- 不再创建或依赖 `agent.md`。
- 当前 route / phase selector truth 以 `.planning/STATE.md` 为准。

## Summary

Phase 129 不是功能扩展，而是把已被承认的 formal homes 继续 inward slimming：`custom_components/lipro/core/api/rest_facade.py` 现在正好卡在 `Phase 113` 预算上限 `360` 行，`custom_components/lipro/core/api/status_fallback_support.py` 也只剩 `7` 行 headroom（`333/340`）。因此本 phase 的正确做法不是再长出新的 helper family，而是把现有 helper magic 换成更直接的 collaborator 调用，并把 fallback orchestration 的主路径显式化。

最优路线是：把 `rest_facade_request_methods.py` 改成直接调用 `_transport_executor` / `_request_gateway` / `_auth_recovery`，借此删除 `rest_facade.py` 中 `_component_method()` / `_component_async_method()` 生成的私有转发层；同时把 `status_fallback_support.py` 的 setup 构造与 primary-query / fallback-after-error 两段逻辑收束成更直观的内部结构，但保留 `query_items_by_binary_split_impl()` 与 `query_with_fallback_impl()` 这两个既有 inward 入口，不重写 public story。

**Primary recommendation:** 先在 `rest_facade_request_methods.py` 直连现有 collaborator、再把 `rest_facade.py` 清回纯组合根；对 fallback 侧只做 orchestration clarity，不改 public home、fallback 语义或 split executor 所有权。

## Standard Stack

### Core
| Library / Tool | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | `>=3.14.2` | 运行时 / typing 基线 | `pyproject.toml` 与 CI 共用同一基线 |
| `aiohttp` | `>=3.12.0,<4.0.0` | REST transport | 现有 protocol-plane 标准依赖 |
| `homeassistant` | `2026.3.1` | HA integration test host | dev extra 明确锁定 |
| `pytest` | `>=7.0.0` | 测试执行 | 全仓既有测试基础设施 |
| `pytest-asyncio` | `>=0.21.0` | async 测试 | fallback / facade 都是 async path |
| `ruff` | `0.15.4` | lint / format guard | CI 与本地命令统一 |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest-homeassistant-custom-component` | `>=0.13.0` | HA custom component fixtures | broader API/integration coverage |
| `mypy` | `>=1.0.0` | strict typing gate | touched seam 涉及 Protocol / typed collaborator 时 |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| 直接 collaborator 调用 | 新增 façade-support wrapper | 会再长一层 second story，不符合 north-star |
| 复用现有 `status_fallback_split_executor.py` | 再拆一个新的 fallback helper 文件 | 只会增加 proof / import locality 成本 |
| 扩展现有 focused suites | 新增宽而厚的 phase mega-test | 与 repo 既有 topicization 方向相反 |

**Installation:**
```bash
uv sync --extra dev
```

**Version verification:** 已按 `pyproject.toml` 与 `.github/workflows/ci.yml` 核对本 phase 涉及的工具链版本；本 phase 不建议引入任何新依赖。

## Architecture Patterns

### Recommended Project Structure
```text
custom_components/lipro/core/api/
├── rest_facade.py                  # REST child façade composition root
├── rest_facade_request_methods.py  # request/auth public surface
├── rest_facade_endpoint_methods.py # endpoint public surface
├── status_fallback.py              # binary-split fallback public home
├── status_fallback_support.py      # setup/context/orchestration support
└── status_fallback_split_executor.py # recursive split executor / logging
```

### Pattern 1: 组合根只保留 wiring，不保留 generic delegation
**What:** `rest_facade.py` 负责 state、collaborator wiring、少量明确保留的 helper；request-facing logic 继续留在 sibling methods 文件。  
**When to use:** 当 façade 需要“显式 surface”而不是“动态 helper 工厂”时。  
**Example:**
```python
async def get_session(self: LiproRestFacade) -> aiohttp.ClientSession:
    return await self._transport_executor.get_session()
```

### Pattern 2: fallback 只允许一条 public story
**What:** `status_fallback.py` 继续作为唯一 public home；`status_fallback_support.py` 只负责 setup/context/orchestration；`status_fallback_split_executor.py` 继续持有递归 split mechanics。  
**When to use:** 需要收窄 fallback 主路径可读性，但不能把 truth 散回 caller / wrapper。  
**Example:**
```python
setup = _BinarySplitSetup.build(...)
try:
    return await setup.context.query_rows(ids, semaphore=asyncio.Semaphore(1))
except setup.context.lipro_api_error as err:
    ...
```

### Anti-Patterns to Avoid
- **新增第二个 REST/fallback home：** 不新增新的 façade support root、compat adapter、wrapper family。
- **为了“瘦身”而改 outward contract：** Phase 129 只允许结构收口，不允许 signature / payload 语义漂移。
- **删除历史护栏再说：** `Phase 99` / `Phase 107` / `Phase 113` 现有 guard 都会对当前实现生效，必须同步迁移或保持兼容。

## Recommended Implementation Slices

| Slice | Files | Action | Exit Criteria | Confidence |
|------|-------|--------|---------------|------------|
| 1 | `rest_facade_request_methods.py` | 把 public request/auth methods 改成直接调用 `_transport_executor` / `_request_gateway` / `_auth_recovery` | public signature 不变，request flow 更直观 | HIGH |
| 2 | `rest_facade.py` | 删除 `_component_method()` / `_component_async_method()` 及其生成的私有 delegate；只保留明确需要的组合根与少量 intentional helpers | 文件仍 `<=360` 行，review 时能直接看到 wiring | HIGH |
| 3 | `status_fallback_support.py` | 把 builder pyramid 收束成单一 setup constructor（推荐 dataclass classmethod），并把 `query_with_fallback_impl()` 显式切成 primary-query / fallback-after-error 两段 | `query_items_by_binary_split_impl()` / `query_with_fallback_impl()` 仍保留，fallback 语义不变 | HIGH |
| 4 | `tests/core/api/*` + planning docs | 在现有 focused suites 中冻结 explicit-surface 与 fallback invariants；必要时同步 verification/testing ledgers | helper magic 回流、budget 破线、fallback 语义漂移时直接失败 | HIGH |

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| façade slimming | 新的 façade-support root / compat shell | 直接 collaborator 调用 + 现有 sibling method modules | 不制造 second story |
| fallback clarity | 新的 split engine / logger | 复用 `status_fallback_split_executor.py` | 递归与 summary logging 已有 formal home |
| proof chain | 新 mega-test / mega-doc | 扩展既有 focused suites 与 ledgers | 更符合 topicized assurance 方向 |

**Key insight:** 本 phase 的“瘦身”必须通过移除间接层完成，而不是通过新增 another helper layer 来伪装简化。

## Runtime State Inventory

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — 本 phase 不改 schema、ID、collection/key 命名 | none |
| Live service config | None — 不涉及 UI/DB 存储的外部服务配置 | none |
| OS-registered state | None — 不涉及 systemd/launchd/Task Scheduler/pm2 名称变更 | none |
| Secrets/env vars | None — 不改 env var / secret key 名称 | none |
| Build artifacts | None — 不改包名、模块根名、entrypoint 名 | none |

## Risks

| Risk | Why it is real now | Mitigation |
|------|--------------------|------------|
| 历史 guard 断裂 | `tests/meta/test_phase99_runtime_hotspot_support_guards.py` 与 `tests/meta/test_phase107_rest_status_hotspot_guards.py` 直接盯代码 token | 改 helper 名/结构时同步迁移 guard，不做 code-only refactor |
| 行数预算失守 | `rest_facade.py` 现为 `360/360`，`status_fallback_support.py` 为 `333/340` | 先删后加；默认不放宽 `Phase 113` budget |
| fallback 语义漂移 | 现有测试已冻结 no-I/O、单次 full-batch fail、fallback depth、non-retriable raise | 仅重排 orchestration，不碰 outward behavior |
| 私有 helper ripple | `_iot_sign`、`_resolve_error_code`、`_unwrap_iot_success_payload` 在其他 focused tests 仍被直接引用 | 只删真正无消费者的 generic delegate；保留被测试的 intentional helper |
| 文档 / proof chain 漂移 | 本仓要求 code、testing map、verification matrix、review ledgers 同轮同步 | 把 docs sync 作为显式 slice，不留到 closeout 再补 |

## Common Pitfalls

### Pitfall 1: 把 helper magic 挪位置，却没有减少 magic
**What goes wrong:** 删掉 `_component_*` 后又新增新的 wrapper/support root。  
**How to avoid:** 直接让 `rest_facade_request_methods.py` 调 collaborator，不造新层。

### Pitfall 2: 只改代码，不改 predecessor/no-growth guards
**What goes wrong:** 当前 focused tests 过了，历史/预算 guard 在 CI 爆。  
**How to avoid:** 同 patch 检查 `Phase 99`、`Phase 107`、`Phase 113` 相关 guard 与 ledger 文本。

### Pitfall 3: 为了“更清晰”改掉 fallback contract
**What goes wrong:** 重新请求 full batch、丢失 fallback depth、把 non-retriable error 吞掉。  
**How to avoid:** 保留现有 `query_with_fallback()` outward contract，用现有 regressions 锁死行为。

## Test Strategy

- **Slice 1 快速回归：** `uv run pytest -q tests/core/api/test_protocol_contract_facade_runtime.py`
- **Slice 2/3 快速回归：** `uv run pytest -q tests/core/api/test_api_status_service_fallback.py tests/core/api/test_api_status_service_regressions.py`
- **历史/预算护栏：** `uv run pytest -q tests/meta/test_phase99_runtime_hotspot_support_guards.py tests/meta/test_phase107_rest_status_hotspot_guards.py tests/meta/test_phase113_hotspot_assurance_guards.py`
- **静态质量：** `uv run ruff check custom_components/lipro/core/api/rest_facade.py custom_components/lipro/core/api/rest_facade_request_methods.py custom_components/lipro/core/api/status_fallback.py custom_components/lipro/core/api/status_fallback_support.py custom_components/lipro/core/api/status_fallback_split_executor.py tests/core/api/test_protocol_contract_facade_runtime.py tests/core/api/test_api_status_service_fallback.py tests/core/api/test_api_status_service_regressions.py`
- **矩阵 / 类型 / broader API：** `uv run python scripts/check_file_matrix.py --check` → `uv run mypy` → `uv run pytest tests/core/api tests/snapshots/test_api_snapshots.py -q`
- **当 planning/governance docs 同步时：** 再跑 `uv run pytest -q tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_version_sync.py`

## Code Examples

### 显式 public method 直接转发 collaborator
```python
async def execute_request(
    self: LiproRestFacade,
    request_ctx: object,
    path: str,
) -> tuple[int, JsonObject, ResponseHeaders]:
    return await self._transport_executor.execute_request(request_ctx, path)
```

### primary-query 失败后才进入 fallback executor
```python
try:
    result_rows = await setup.context.query_rows(ids, semaphore=asyncio.Semaphore(1))
except setup.context.lipro_api_error as err:
    if not setup.context.is_retriable_device_error(err):
        raise
    all_results, max_fallback_depth = await execute_batch_fallback_query(...)
```

## State of the Art

| Old Approach | Current / Recommended Approach | When Changed | Impact |
|--------------|-------------------------------|--------------|--------|
| composition root 内 generic delegate factories | sibling request methods 直接调现有 collaborator，composition root 只保留 wiring | Phase 129 推荐落地 | façade 更可读，helper magic 更少 |
| setup builder 分散 + primary path 混在 fallback path 里 | 单一 setup constructor + 两段式 orchestration | Phase 129 推荐落地 | fallback 更易审阅和守护 |

## Documentation Sync Requirements

- **一定要写 phase 资产：** 本文件、后续 `129-PLAN.md`、`129-SUMMARY.md`、`129-VERIFICATION.md`。
- **如果 focused proof chain 变化：** 同步 `.planning/baseline/VERIFICATION_MATRIX.md` 与 `.planning/codebase/TESTING.md`。
- **如果 file-home / hotspot wording 变化：** 同步 `.planning/reviews/FILE_MATRIX.md`、`.planning/reviews/RESIDUAL_LEDGER.md`、`.planning/reviews/KILL_LIST.md`。
- **只有 public/dependency truth 真变时才更新：** `.planning/baseline/PUBLIC_SURFACES.md`、`.planning/baseline/DEPENDENCY_MATRIX.md`。
- **`docs/developer_architecture.md` 只在当前拓扑叙述真的变化时更新；** 单纯局部 helper 收口不必强行改 current-topology prose。

## Open Questions

1. **是否需要新增 `Phase 129` 专用 meta guard？**
   - What we know: 现有 focused suites + `Phase 113` 预算 guard 已能覆盖大部分 changed surface。
   - What's unclear: 若要冻结 phase-specific planning/ledger 投影，是否现有 guard 足够清晰。
   - Recommendation: 默认先扩现有 suites；只有当 verification/doc 投影断言过于分散时，再加一份薄的 phase-labeled meta guard。
2. **哪些私有 helper 必须保留？**
   - What we know: `_iot_sign`、`_resolve_error_code`、`_unwrap_iot_success_payload` 已被其他测试引用。
   - What's unclear: 是否还有未纳入本次必读集的 focused tests 依赖其他私有 wrapper 名称。
   - Recommendation: 实施前先对 `custom_components/lipro/core/api/rest_facade.py` 的私有符号做一次全仓引用搜索，再删 generic delegate。

## Environment Availability

Skipped — 本 phase 为 code/config-only 收口；不依赖新的外部服务或 CLI，沿仓库既有 `uv` / `pytest` / `ruff` / `mypy` 即可。

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest` + `pytest-asyncio` |
| Config file | `pyproject.toml` |
| Quick run command | `uv run pytest -q tests/core/api/test_protocol_contract_facade_runtime.py tests/core/api/test_api_status_service_fallback.py tests/core/api/test_api_status_service_regressions.py tests/meta/test_phase113_hotspot_assurance_guards.py` |
| Full suite command | `uv run pytest tests/core/api tests/snapshots/test_api_snapshots.py -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ARC-40 | façade surface 显式、无 dynamic delegation 回流 | focused contract | `uv run pytest -q tests/core/api/test_protocol_contract_facade_runtime.py` | ✅ |
| HOT-59 | fallback setup / primary path 清晰且语义不变 | async unit/regression | `uv run pytest -q tests/core/api/test_api_status_service_fallback.py tests/core/api/test_api_status_service_regressions.py` | ✅ |
| TST-50 | touched scope regressions 完整覆盖 | focused regression | `uv run pytest -q tests/core/api/test_protocol_contract_facade_runtime.py tests/core/api/test_api_status_service_fallback.py tests/core/api/test_api_status_service_regressions.py` | ✅ |
| QLT-52 | 不回长 helper magic，且不突破热点预算 | meta guard + lint | `uv run pytest -q tests/meta/test_phase113_hotspot_assurance_guards.py tests/meta/test_phase107_rest_status_hotspot_guards.py` | ✅ |

### Sampling Rate
- **Per task commit:** quick run command + touched-file `ruff check`
- **Per wave merge:** `uv run python scripts/check_file_matrix.py --check` + `uv run mypy` + full suite command
- **Phase gate:** 再补 `tests/meta/test_governance_route_handoff_smoke.py` / `tests/meta/test_version_sync.py`（若 planning/governance docs 有变动）

### Wave 0 Gaps
None — 现有 focused infrastructure 已覆盖本 phase；优先扩现有 suite，而不是新增大而宽的新测试载体。

## Sources

### Primary (HIGH confidence)
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` - north-star 裁决与 single-mainline 原则
- `AGENTS.md` / `CLAUDE.md` - 仓库约束、读序、文档同步规则
- `.planning/{PROJECT.md,ROADMAP.md,REQUIREMENTS.md,STATE.md,MILESTONES.md}` - 当前 route / phase / requirement truth
- `.planning/codebase/{CONCERNS.md,TESTING.md}` - hotspot 排名、现有测试地图
- `.planning/baseline/{DEPENDENCY_MATRIX.md,VERIFICATION_MATRIX.md}` - sanctioned inward dependency 与 proof chain
- `.planning/reviews/{FILE_MATRIX.md,RESIDUAL_LEDGER.md,KILL_LIST.md}` - formal home / residual / kill-target 裁决
- `custom_components/lipro/core/api/{rest_facade.py,rest_facade_request_methods.py,rest_facade_endpoint_methods.py,status_fallback.py,status_fallback_support.py,status_fallback_split_executor.py,status_service.py,request_gateway.py}` - 当前实现切面
- `tests/core/api/{test_protocol_contract_facade_runtime.py,test_api_status_service_fallback.py,test_api_status_service_regressions.py}` 与 `tests/meta/{test_phase99_runtime_hotspot_support_guards.py,test_phase107_rest_status_hotspot_guards.py,test_phase113_hotspot_assurance_guards.py}` - changed-surface / predecessor / budget guards

### Secondary (MEDIUM confidence)
- `docs/developer_architecture.md` - current-topology guide，仅作 developer-facing 辅助视图

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - 全部来自 repo pin / CI / current toolchain
- Architecture: HIGH - north-star、planning truth、code 与 guards 一致
- Pitfalls: HIGH - 直接来自当前 failing-surface 与现有历史 guard 约束

**Research date:** 2026-04-01
**Valid until:** 2026-04-08（active route / hotspot phase，建议 7 天内消费）
