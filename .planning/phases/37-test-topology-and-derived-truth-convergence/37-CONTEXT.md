# Phase 37 Context

**Phase:** `37 Test topology and derived-truth convergence`
**Milestone:** `v1.4 seed — Sustainment, Trust Gates & Final Hotspot Burn-down`
**Date:** `2026-03-18`
**Status:** `planned — context captured, ready for execution planning`
**Source:** `.planning/{ROADMAP,REQUIREMENTS,STATE,PROJECT}.md` + test topology audit + `.planning/codebase/*` freshness review + CI / contributing truth

## Why Phase 37 Exists

经过多轮整改后，仓库的真实短板已不再是“有没有测试”，而是：

1. 少数跨故事线巨石测试仍然吸附过多主题，失败定位成本高。
2. `.planning/codebase/*` 作为 derived maps，freshness/header truth 与真实测试热点、命令拓扑已开始出现漂移。
3. benchmark / topology / closeout evidence 已具备基础能力，但 guard 仍可更精确，避免高噪音 prose-coupled 断言。

`Phase 37` 的目标不是把所有长文件都切碎，而是完成第三波真正有价值的 topicization，并让 derived truth 再次与真实测试布局收敛。

## Goal

1. topicize 剩余真正跨故事线的巨石测试，提升局部执行与失败定位效率。
2. 收敛 `.planning/codebase/*`、测试策略、verification truth 与实际测试布局/命令拓扑。
3. 补 drift guards 与 closeout evidence，降低高噪音断言并稳住 benchmark posture。

## Decisions (Locked)

- `Phase 37` 严格依赖 `Phase 36` 完成后的 runtime 布局，不并行执行。
- 优先拆 `test_init_service_handlers.py`、`test_init_runtime_behavior.py`、`test_governance_phase_history.py` 这类真实跨故事线巨石；不是为拆而拆所有长文件。
- `.planning/codebase/*` 仍只是 derived collaboration maps；本 phase 只做 freshness / topology 对齐，不把它们抬升为 authority。
- benchmark 仍保持 advisory-with-budget posture，不擅自改写成 hard gate。
- drift guard 必须守真实命令/布局/引用，而不是继续堆 prose-coupled 文案断言。

## Non-Negotiable Constraints

- 不得因测试拆分改变 public behavior 或逃避 coverage/guard。
- 不得制造大量互相导入的“假 topicization”壳文件。
- 不得让 `.planning/codebase/*` 与 `CONTRIBUTING.md`、CI、baseline truth 继续分叉。
- 不得把 benchmark posture 从 advisory 改写成未获授权的 blocking contract。

## Canonical References

### Governance / Route Truth
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/PROJECT.md`
- `CONTRIBUTING.md`
- `.github/workflows/ci.yml`

### Test Topology Hotspots
- `tests/core/test_init_service_handlers.py`
- `tests/core/test_init_runtime_behavior.py`
- `tests/meta/test_governance_phase_history.py`
- `tests/core/test_init.py`
- `tests/core/api/test_api_command_surface.py`

### Derived Truth / Docs
- `.planning/codebase/README.md`
- `.planning/codebase/ARCHITECTURE.md`
- `.planning/codebase/STRUCTURE.md`
- `.planning/codebase/TESTING.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`

### Guard / Regression Truth
- `tests/meta/test_toolchain_truth.py`
- `tests/meta/test_governance_phase_history.py`
- `tests/meta/test_governance_closeout_guards.py`
- `tests/meta/test_public_surface_guards.py`

## Expected Scope

### In scope
- third-wave topicization of remaining cross-story mega tests
- codebase map freshness / topology / command truth refresh
- drift guards and benchmark/topology closeout evidence

### Out of scope
- protocol or runtime hotspot slimming
- release hardening
- global rewrite of all long tests
- changing benchmark from advisory to blocking

## Open Planning Questions

1. 哪些 split 能真正降低耦合，而不是制造互导壳？
2. codebase maps 的 freshness guard 应守 header，还是守热点/command truth，还是两者都守？
3. 哪些高噪音 governance assertions 可以改为更结构化的 truth checks？
4. benchmark posture 最需要补的是 budget semantics、artifact truth，还是 docs/CI wording 同步？

---

*Phase directory: `37-test-topology-and-derived-truth-convergence`*
*Context gathered: 2026-03-18 from test topology audit and derived-truth freshness review.*
