# Phase 49: Mega-test topicization and failure-localization hardening - Research

**Date:** 2026-03-21
**Status:** Final
**Plans / Waves:** 4 plans / 3 waves
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- `tests/meta/test_governance_closeout_guards.py` 的拆分必须保持治理诚实：phase / doc / token / promoted asset 仍需 machine-checkable，不能因切分而放松断言。
- runtime / diagnostics / update platform 测试的 topicization 只能改善文件粒度、夹具归属、断言命名与失败摘要；不得借机改变正式 public surface 或实际业务行为。
- stray top-level tests 必须进入更自然的 domain home；若移动文件，需同步更新 file-matrix / import-path / pytest discovery 相关真相，不能留下第二个影子入口。
- assertion ids、parameterization labels、helper names 必须以实际 concern 为中心，优先暴露 `(phase, doc, token)`、runtime facet、platform concern，而不是抽象的 case 序号。
- 本 phase 若需触碰 `.planning/reviews/FILE_MATRIX.md`、baseline 或 closeout guards，只能做与测试 topicization / truth sync 直接相关的最小更改。

### Claude's Discretion
- governance megaguards 可拆成同文件内按 concern family 的 test class / helper cluster，也可拆分到多个 meta test 文件；只要最终 failure-localization 明显提升且 truth 不漂移即可。
- runtime megatests 可通过新增 focused test modules、抽取共享 fixtures/helpers、移动 stray tests 到 `tests/core/` 子树等方式收敛；选择最少扰动且最清晰的 home。
- update-platform megatests 可按 parser / arbitration / entity install flow / certification policy concern 切分，但无需为了“切分”而制造过细碎文件。
- 允许在测试中引入更明确的 helper factory / parametrized ids / assertion messages，但不要引入新的测试框架、插件或额外依赖。

### Deferred Ideas (OUT OF SCOPE)
- 不在本 phase 内改变产品代码或协议/runtime/control formal roots；
- 不在本 phase 内执行 `Phase 50` 的 REST typed-surface reduction、command/result ownership convergence、diagnostics auth-error duplication closure；
- 不把 execution-trace 资产自动 promoted；promotion 仍只针对 closeout evidence；
- 不为测试切分引入新依赖、snapshot framework 或复杂测试生成器。
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| `TST-09` | 治理 megaguards、runtime-root megatests 与 platform megatests 必须按 concern topicize，减少 giant-file failure triage 成本。 | 现有热点已天然映射到 `meta` closeout families、`tests/core/coordinator/**`、`tests/core/ota/**` 与 `tests/platforms/**`；无需新框架。 |
| `QLT-17` | 测试与治理守卫的 failure localization 必须直接标出 phase / doc / token / runtime facet，避免“一个断言管全仓”的模糊失败面。 | 可直接用 `pytest` ids、显式 helper 名、断言消息与 file-home 同步达成；关键是最后一波统一收口 truth anchors。 |

</phase_requirements>

## Summary

`Phase 46` 已把测试问题定性为“topology / failure UX”，不是 coverage 不足：Tests 维度得分 `7.8/10 (B+)`，主要短板正是 governance megaguards、runtime-root megatests 与 update platform megatest 的失败定位成本。`PROJECT / ROADMAP / REQUIREMENTS / STATE` 也已把 `Phase 49` 正式锁定为下一步，requirements 明确是 `TST-09` 与 `QLT-17`。

当前仓库其实已经给出正确方向：`tests/core/coordinator/**`、`tests/core/ota/**`、`tests/platforms/test_firmware_update_entity_edges.py`、`tests/platforms/test_update_task_callback.py` 都是现成的 topic home。`Phase 49` 最优解不是再造测试基础设施，而是把剩余巨石文件继续沿这些现有 seams inward topicize，并在最后一波统一补齐 ids、断言消息、`FILE_MATRIX` 与命令文档锚点。

**Primary recommendation:** 采用 `4 plans / 3 waves`；前两 plans 并行切开 governance 与 runtime/diagnostics，第三 plan 收口 OTA/update 与 stray tests，最后一 plan 专做 failure-localization 与 truth sync。

## Current State

| File | Lines | Tests | 现状 | 推荐归宿 |
|------|------:|------:|------|----------|
| `tests/meta/test_governance_closeout_guards.py` | 1150 | 28 | 单文件承载 promoted assets、archive snapshots、`v1.1 / v1.2 / v1.5 / v1.6` closeout、`Phase 28 -> 48` route truth | 保留此路径作为已知 anchor；再按 concern family 拆出 1-2 个 sibling meta suites |
| `tests/core/test_coordinator.py` | 805 | 31 | 已有 `Services / Runtime / EntityLifecycle / UpdateFlow` 四大簇，但仍停在巨石根文件 | 优先回到 `tests/core/coordinator/services/**`、`tests/core/coordinator/runtime/**`，必要时新增小型 lifecycle / update files |
| `tests/core/test_diagnostics.py` | 718 | 30 | 混合 redaction helpers、常量集、config-entry diagnostics、device diagnostics | 继续留在 `tests/core/`，拆成 `test_diagnostics_redaction.py`、`test_diagnostics_config_entry.py`、`test_diagnostics_device.py` 这类同层专题面 |
| `tests/platforms/test_update.py` | 1041 | 25 | 混合 parser、install policy、row arbitration、cache、setup-entry、entity certification、version compare | helper/selector/manifest 归 `tests/core/ota/**`；平台集成与 entity 行为留 `tests/platforms/**` |
| `tests/test_coordinator_public.py` | 55 | 1 | 顶层 stray file，只测 coordinator public delegation | 吸收到 `tests/core/coordinator/test_public_surface.py` 或等价 home |
| `tests/test_coordinator_runtime.py` | 41 | 1 | 顶层 stray file，只测 `async_setup_entry` runtime_data wiring | 吸收到 `tests/core/test_init_runtime_setup_entry.py` |

补充约束已确认：
- `docs/developer_architecture.md`、`CONTRIBUTING.md`、`.planning/baseline/VERIFICATION_MATRIX.md` 仍直接引用 `tests/test_coordinator_public.py` / `tests/test_coordinator_runtime.py`；
- `scripts/check_file_matrix.py` 对 `tests/core/test_coordinator.py` 有 runtime 特判；
- `.planning/reviews/FILE_MATRIX.md` 仍把两份 stray files 记成 top-level Cross-cutting truth。

## Risk Notes

- **治理诚实回退**：若拆 `test_governance_closeout_guards.py` 时遗漏 promoted-asset allowlist、pull-only 约束或 phase/doc/token 断言，等于把守卫“切薄”成失真。
- **路径漂移未同步**：若移动 stray tests 或新增 topical files，却不同时更新 `FILE_MATRIX`、`scripts/check_file_matrix.py`、`VERIFICATION_MATRIX`、`docs/developer_architecture.md` 与 `CONTRIBUTING.md`，会立刻出现 truth drift。
- **过度碎片化**：`tests/platforms/test_update.py` 已有 `tests/core/ota/**`、`tests/platforms/test_firmware_update_entity_edges.py`、`tests/platforms/test_update_task_callback.py` 这些邻近专题面；再切成过多单测文件会降低 discoverability。
- **只分文件、不分语义**：如果 test 名、`pytest.param(id=...)`、helper 名仍是抽象 case 编号，failure-localization 改善会停留在表面。
- **错误归宿**：`tests/test_coordinator_runtime.py` 更像 init/runtime wiring，不应误塞进 coordinator runtime subtree；否则会模糊 control/runtime 边界。

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| `pytest` | `9.0.0` | 测试收集、node id、参数化 | 仓库既有标准；无需新插件即可表达 `(phase, doc, token)` ids |
| `pytest-asyncio` | `1.3.0` | async 测试运行 | 目标套件大量依赖 async Home Assistant 场景 |
| `pytest-homeassistant-custom-component` | `0.13.317` | HA 测试夹具 | `MockConfigEntry`、`hass` 等既有测试面都依赖它 |
| `homeassistant` | `2026.3.1` | 运行时真相 | repo dev target，Phase 49 不应偏离 |
| `uv run` | repo contract | 命令入口 | 项目契约强制统一使用 |
| `scripts/check_file_matrix.py` | repo script | 文件归宿真相校验 | 任何 re-home / split 都要过它 |

### Supporting

| Tool / Suite | Purpose | When to Use |
|--------------|---------|-------------|
| `tests/meta/test_toolchain_truth.py` | 命令/测试地图/脚本边界真相 | 文件名或命令锚点变更时必跑 |
| `tests/meta/test_public_surface_guards.py` | public surface no-drift | coordinator / diagnostics / update split 完成后 |
| `ruff==0.15.4` | lint touched files | 最终 phase gate 前 |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| 保留巨石文件只加 `class` | 继续切到 topical modules | 单文件 class 化能稍降噪，但 failure node 仍过粗 |
| 新 pytest 插件 / 自定义 reporter | 既有 `pytest` ids + assertion messages | 新插件增加维护面，却不解决 truth sync |
| 保留旧路径做 wrapper | 直接移动/吸收并更新真相锚点 | wrapper 会留下第二收集入口与影子 story |

**Installation:** 无新增依赖；沿用现有 dev 环境即可。

## Architecture Patterns

### Recommended Project Structure

```text
tests/
├── meta/
│   ├── test_governance_closeout_guards.py      # 保留为已知 closeout anchor
│   ├── test_governance_closeout_route.py       # 当前 route / phase truth
│   └── test_governance_closeout_assets.py      # promoted assets / archive snapshots
├── core/
│   ├── coordinator/
│   │   ├── services/...
│   │   ├── runtime/...
│   │   ├── test_public_surface.py
│   │   ├── test_entity_lifecycle.py
│   │   └── test_update_flow.py
│   ├── test_diagnostics_redaction.py
│   ├── test_diagnostics_config_entry.py
│   ├── test_diagnostics_device.py
│   └── test_init_runtime_setup_entry.py
├── core/ota/
│   ├── test_firmware_manifest.py
│   ├── test_ota_candidate.py
│   ├── test_ota_row_selector.py
│   └── test_ota_rows_cache.py
└── platforms/
    ├── test_update.py
    ├── test_firmware_update_entity_edges.py
    └── test_update_task_callback.py
```

### Pattern 1: 沿现有专题树 inward topicize

**What:** 先用已经存在的 `tests/core/coordinator/**` 与 `tests/core/ota/**`，不要再在 repo 顶部创建新的 stray suites。  
**When to use:** coordinator / update 相关 split 全程。  
**Why:** 这两个子树已经被历史 phase 建成正式 topical home，继续沿用能最小化认知跳变。

### Pattern 2: 保留已知 governance anchor，再增 sibling suites

**What:** `tests/meta/test_governance_closeout_guards.py` 不必一次性“改名消失”；更稳妥的是保留它作为 closeout anchor，把当前 route truth 与 archive/promoted asset families 拆到 siblings。  
**When to use:** governance megaguard split。  
**Why:** 该路径已被 `FILE_MATRIX`、`VERIFICATION_MATRIX`、`CONTRIBUTING.md`、`tests/meta/test_toolchain_truth.py` 等多处引用，完全改名会扩大 churn 半径。

### Pattern 3: 让失败节点直接说人话

**What:** `pytest.param(..., id=...)`、helper 名与断言消息必须直接暴露 `phase / doc / token / runtime facet / platform concern`。  
**When to use:** `49-04` 全量 sweep，也可提前在每个 split 中同步引入。

```python
@pytest.mark.parametrize(
    ("phase", "doc", "needle"),
    [
        pytest.param("48", "48-SUMMARY.md", "phase: 48", id="phase48-summary-frontmatter"),
        pytest.param("48", "48-VERIFICATION.md", "218 passed", id="phase48-verification-pass-count"),
    ],
)
def test_phase_48_evidence_tokens(phase: str, doc: str, needle: str) -> None:
    ...
```

### Anti-Patterns to Avoid

- **Wrapper 保旧路由**：旧文件只 import 新测试，会留下影子入口与双收集故事。
- **按行数生切**：只为降行数拆文件，但 topic 仍混杂。
- **setup/init 误入 runtime subtree**：`async_setup_entry` wiring 应留在 init home，不要伪装成 coordinator runtime case。
- **复制第二套 truth**：任何 split 都不能绕开 `PROMOTED_PHASE_ASSETS.md`、`FILE_MATRIX.md` 与现有 meta guards。

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| failure-localization | 自定义 pytest reporter / 新插件 | `pytest` ids、显式 helper 名、断言消息 | 现有 runner 已足够；新插件只会增负担 |
| OTA parser / arbitration 测试 home | 新建另一套 helper-only megafile | 既有 `tests/core/ota/{test_firmware_manifest.py,test_ota_candidate.py,test_ota_row_selector.py,test_ota_rows_cache.py}` | 已有专题面更自然，且 Phase 49 不应重造结构 |
| governance evidence registry | 新 YAML / JSON 索引 | `.planning/reviews/PROMOTED_PHASE_ASSETS.md` + closeout guards | 单一真源已存在 |
| file-home classification | 手写临时脚本或人工约定 | `scripts/check_file_matrix.py` + `.planning/reviews/FILE_MATRIX.md` | 移动测试文件时必须 machine-checkable |

**Key insight:** `Phase 49` 是“把现有断言送回更自然的 home”，不是“再发明一层测试基础设施”。

## Recommended 4-Plan / Multi-Wave Split

| Plan | Scope | Recommended output | Wave |
|------|-------|--------------------|------|
| `49-01` | governance closeout megaguards | 保留 `tests/meta/test_governance_closeout_guards.py` 作为 anchor；把 route truth / assets truth 分出 sibling suites；共享 loader/helper 内聚 | Wave 1 |
| `49-02` | coordinator + diagnostics topicization | `tests/core/test_coordinator.py` 回流到 `tests/core/coordinator/**`；`tests/core/test_diagnostics.py` 拆成 redaction / config-entry / device diagnostics | Wave 1 |
| `49-03` | update-platform megatest + stray re-home | parser / arbitration / install-policy cases 进入 `tests/core/ota/**`；平台 entity/setup 留 `tests/platforms/**`；吸收两份 stray top-level tests | Wave 2 |
| `49-04` | assertion ids + failure summaries + truth sync | 统一 `id=` / helper 名 / assertion message；同步 `FILE_MATRIX`、`check_file_matrix`、`VERIFICATION_MATRIX`、文档命令锚点 | Wave 3 |

**Wave plan**
- **Wave 1:** `49-01` 与 `49-02` 并行；二者文件树基本分离，最适合同时推进。
- **Wave 2:** `49-03` 独立收口 OTA / platform / stray tests；这一步对 file-home 与 docs 命令影响最大，单独做更稳。
- **Wave 3:** `49-04` 最后执行；只有当最终文件名与归宿稳定后，`id`、命令清单与 truth anchors 才值得一次性同步。

## Common Pitfalls

### Pitfall 1: 改善了目录，没改善失败语义
**What goes wrong:** 文件拆了，但 pytest node 仍是抽象 case 名。  
**How to avoid:** 每个新参数集都用 concern-first `id`；治理侧优先暴露 `(phase, doc, token)`。

### Pitfall 2: 误把 stray test 并回不自然的 home
**What goes wrong:** `tests/test_coordinator_runtime.py` 若被塞进 `tests/core/coordinator/runtime/**`，会把 init/setup wiring 讲成 runtime component concern。  
**How to avoid:** setup-entry tests 继续归 `tests/core/test_init_runtime*.py`。

### Pitfall 3: 只更新 `FILE_MATRIX`，漏掉文档命令锚点
**What goes wrong:** `docs/developer_architecture.md`、`CONTRIBUTING.md`、`VERIFICATION_MATRIX` 仍引用旧路径。  
**How to avoid:** file move checklist 明确包含 docs / baseline / script / meta guards。

### Pitfall 4: `test_update.py` 继续吞掉 OTA helper truth
**What goes wrong:** manifest / selector / candidate / cache 逻辑继续堆在 platform file，和现有 `tests/core/ota/**` 双线并存。  
**How to avoid:** helper truth 优先回到 `tests/core/ota/**`，平台文件只保留 entity/setup/integration seam。

## Code Examples

Verified repo pattern:

```python
def test_state_service_exposes_device_accessors() -> None:
    device = MagicMock()
    state_runtime = MagicMock()
    state_runtime.get_all_devices.return_value = {"dev1": device}
    state_runtime.get_device_by_serial.return_value = device
    state_runtime.get_device_by_id.return_value = device
```

Source: `tests/core/coordinator/services/test_state_service.py`

Recommended localization pattern:

```python
assert "phase: 48" in summary_text, "phase48-summary-frontmatter"
assert telemetry["last_runtime_failure_stage"] == "runtime"
```

Use short, concern-first assertion messages; do not hide failures behind generic `case_01`.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| giant root-level test files | concern-topicized suites under `tests/core/coordinator/**`, `tests/core/ota/**`, `tests/platforms/**` | `Phase 37 / 39 / 48` | Phase 49 should finish the convergence rather than invent a new topology |
| one closeout megaguard holding all continuity truth | history/release/topology governance families + explicit promoted-asset allowlist | `Phase 37 / 39 / 46` | `test_governance_closeout_guards.py` now has clear concern families to split along |
| top-level coordinator smoke files | topical core suites + init runtime suites | `Phase 27 / 37 / 48` | remaining strays are now anomalies, not precedent |

**Deprecated/outdated:**
- 把 `tests/platforms/test_update.py` 当作 OTA helper 唯一真源。
- 继续保留 `tests/test_coordinator_public.py`、`tests/test_coordinator_runtime.py` 作为长期合法入口。

## Open Questions

1. **治理 closeout 是否完全改名，还是保留旧 anchor 文件？**
   - What we know: 旧路径已被 docs、baseline、toolchain truth、多份 guard 直接引用。
   - What's unclear: 完整 rename 是否值得额外 churn。
   - Recommendation: 保留 `tests/meta/test_governance_closeout_guards.py` 作为 anchor，再增 sibling suites。

2. **diagnostics 是否要新建 `tests/core/diagnostics/` 子树？**
   - What we know: 当前 cross-cutting diagnostics tests 仍主要位于 `tests/core/` 根层。
   - What's unclear: 新子树是否带来真实收益，还是只增加一次额外 topology 迁移。
   - Recommendation: `Phase 49` 先用 `tests/core/test_diagnostics_*.py` 同层拆分，不额外开新树。

## Validation Focus

- `uv run pytest -q tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_phase_history_runtime.py tests/meta/test_governance_phase_history_topology.py tests/meta/test_governance_release_contract.py tests/meta/test_public_surface_guards.py tests/meta/test_toolchain_truth.py`
- `uv run pytest -q tests/core/coordinator tests/core/test_diagnostics*.py tests/core/test_init_runtime_setup_entry.py`
- `uv run pytest -q tests/core/ota tests/platforms/test_update*.py tests/platforms/test_firmware_update_entity_edges.py`
- `uv run python scripts/check_file_matrix.py --check`
- 若 Phase 49 触及多份 docs/baseline 路径锚点，再补 `uv run pytest -q` 作为 phase gate

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest 9.0.0` + `pytest-asyncio 1.3.0` + `pytest-homeassistant-custom-component 0.13.317` |
| Config file | `pyproject.toml` |
| Quick run command | `uv run pytest -q tests/meta/test_governance_closeout_guards.py tests/core/test_coordinator.py tests/core/test_diagnostics.py tests/platforms/test_update.py` |
| Full suite command | `uv run pytest -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| `TST-09` | megaguards / megatests 按 concern topicize，归入自然 topical home | meta + unit/topology | `uv run pytest -q tests/meta tests/core/coordinator tests/core/test_diagnostics*.py tests/core/ota tests/platforms/test_update*.py` | ✅ |
| `QLT-17` | failures 直接报出 phase/doc/token/facet，且 file-home / docs truth 同步 | meta + lint/script | `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_public_surface_guards.py && uv run python scripts/check_file_matrix.py --check` | ✅ |

### Sampling Rate

- **Per task commit:** 跑被触及 topical suite；若移动文件，额外跑 `uv run python scripts/check_file_matrix.py --check`
- **Per wave merge:** 跑当前 wave 全量相关树
- **Phase gate:** meta/governance + coordinator/diagnostics + ota/update targeted suites 全绿；若 docs/baseline 改动较多，再跑 `uv run pytest -q`

### Wave 0 Gaps

None — 现有 `pytest` / HA harness / file-matrix governance 已足够；`Phase 49` 需要的是专题文件迁移与命名收口，不是新测试基础设施。

## Sources

### Primary (HIGH confidence)
- `AGENTS.md` — repo truth order、formal root、测试/文档同步规则
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — assurance plane 与 phase-asset/promoted-asset 边界
- `.planning/PROJECT.md` — `Phase 49` 是默认 next step
- `.planning/ROADMAP.md` — `Phase 49` goal、plans 与 success criteria
- `.planning/REQUIREMENTS.md` — `TST-09` / `QLT-17` requirement truth
- `.planning/STATE.md` — current next action 与 continuity truth
- `.planning/phases/49-mega-test-topicization-and-failure-localization-hardening/49-CONTEXT.md` — locked decisions、discretion、deferred scope
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/{46-AUDIT.md,46-SCORE-MATRIX.md,46-REMEDIATION-ROADMAP.md}` — audit verdict 与 routing rationale
- `.planning/phases/39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition/39-SUMMARY.md` — prior mega-test decomposition anchor
- `.planning/baseline/{VERIFICATION_MATRIX.md,DEPENDENCY_MATRIX.md,AUTHORITY_MATRIX.md}` — truth sync / split constraints
- `.planning/reviews/{FILE_MATRIX.md,README.md,PROMOTED_PHASE_ASSETS.md}` — file-home / promoted-asset truth
- `tests/meta/test_governance_closeout_guards.py`, `tests/core/test_coordinator.py`, `tests/core/test_diagnostics.py`, `tests/platforms/test_update.py`, `tests/test_coordinator_public.py`, `tests/test_coordinator_runtime.py` — hotspot inventory
- `tests/core/coordinator/**`, `tests/core/ota/**`, `tests/platforms/test_firmware_update_entity_edges.py`, `tests/platforms/test_update_task_callback.py` — existing natural topical homes
- `pyproject.toml` + local `uv run python` metadata query — current test stack versions

### Secondary (MEDIUM confidence)
- None

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: **HIGH** — 来自 `pyproject.toml` 与本地已安装版本查询
- Architecture: **HIGH** — 来自 roadmap/context/audit 与现有 test tree 实况
- Pitfalls: **HIGH** — 来自 `VERIFICATION_MATRIX`、`FILE_MATRIX`、`check_file_matrix.py`、docs/commands 现有锚点

**Research date:** 2026-03-21
**Valid until:** 2026-03-28
