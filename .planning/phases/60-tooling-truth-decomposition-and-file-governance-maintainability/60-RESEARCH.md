# Phase 60: Tooling Truth Decomposition & File-Governance Maintainability - Research

**Researched:** 2026-03-22
**Domain:** repo governance tooling / meta-guard topicization
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- `scripts/check_file_matrix.py` 当前约 `1331` 行，是 repo-maintenance tooling hotspot 的第一优先级。
- `tests/meta/test_toolchain_truth.py` 当前约 `607` 行，混合 toolchain / release / docs / governance / codebase-map 多条故事线，是验证热点的第二优先级。
- `scripts.check_file_matrix` 的既有 public import contract 必须稳定保留，至少包括：`repo_root`、`classify_path`、`iter_python_files`、`parse_file_matrix_paths`、`extract_reported_total`、`run_checks` 与 CLI 行为。
- phase 的首要收益是 **ownership clarity / failure localization / truth-chain honesty**，不是机械平均行数。
- `.planning/reviews/FILE_MATRIX.md` 与 `.planning/baseline/VERIFICATION_MATRIX.md` 继续是 authority truth；tooling split 不得把这些规则复制到第二份 helper 文档里。

### Claude's Discretion

- 可把 `scripts/check_file_matrix.py` 变成 thin root + internal families，只要 outward contract 稳定。
- 可把 `tests/meta/test_toolchain_truth.py` 拆成 topical modules，只要 daily runnable roots 与 guard intent 仍清晰。
- 可同步修正文档中的 toolchain / verification command anchors，只要不越界到 `Phase 61 / 62` 的 production / naming 主体。

### Deferred Ideas (OUT OF SCOPE)

_`60-CONTEXT.md` 未单列 Deferred Ideas；本研究按 PRD/CONTEXT 的 out-of-scope 边界执行。_
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| HOT-14 | `scripts/check_file_matrix.py` 与相关 file-governance tooling truth 必须沿 existing truth families inward decomposition，保留稳定 CLI / import contract，不再让单个巨石脚本承担全部 inventory / classifier / validator / render story。 | 推荐保留 `scripts/check_file_matrix.py` 作为 thin compatibility root，只向内拆成 inventory / classification / markdown / validators families。 |
| TST-12 | `tests/meta/test_toolchain_truth.py` 与相关 toolchain / governance megaguards 必须 topicize 成更小、更诚实的 focused suites 或 thin runnable roots，降低 daily failure radius。 | 推荐保留 `tests/meta/test_toolchain_truth.py` 作为 thin runnable root，内部按 Python/DX、release identity、docs index、CI contract、governance maps topicize。 |
| GOV-44 | `.planning/reviews/FILE_MATRIX.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/codebase/TESTING.md` 与 current-story docs 必须在 tooling decomposition 后继续讲同一条 ownership / no-growth 故事。 | 研究明确 authority chain 仍锁定在 `FILE_MATRIX.md`、`VERIFICATION_MATRIX.md`、`TESTING.md` 与 current-story docs；新 internal modules 只承载实现，不承载新治理真源。 |
</phase_requirements>

## Summary

`Phase 60` 最自然的做法不是“把大文件平均切小”，而是把 **现有真相家族** 从过厚 root 中 inward 收口：`scripts/check_file_matrix.py` 继续保留 module path、CLI flags、import-facing helpers；`tests/meta/test_toolchain_truth.py` 继续保留 daily runnable root，再把断言按 authority home / failure mode 分到非 `test_` 话题模块。这样能复用仓库已在 `tests/meta/test_public_surface_guards.py` 与 `tests/meta/test_governance_phase_history.py` 证明可行的 thin-shell 模式。

对 `scripts/check_file_matrix.py`，最自然的 inward decomposition 边界是：`inventory`、`governance classification`、`markdown IO`、`validators`、`thin CLI root`。其中最大热点是 `OVERRIDES` + prefix classifiers；它们属于同一条 file-governance truth family，应该向内收口，但不能把 authority prose 从 `FILE_MATRIX.md` / `VERIFICATION_MATRIX.md` 复制进新的 helper docs。

对 `tests/meta/test_toolchain_truth.py`，最自然的 topicization 边界是：`Python / local DX`、`release identity`、`docs index / terminology`、`CI / lint / benchmark contract`、`governance continuity / derived maps`。最稳妥的 public contract 保留点不是子模块名，而是保留 `tests/meta/test_toolchain_truth.py` 这条 root path，使 pre-push、CI、`CONTRIBUTING.md`、`TESTING.md` 与 current-story docs 不必在同一 phase 被迫大面积改写。

**Primary recommendation:** 保留 `scripts/check_file_matrix.py` 与 `tests/meta/test_toolchain_truth.py` 作为稳定薄根；只把内部 truth family inward 收口，并把 topology 变化冻结回 `FILE_MATRIX.md`、`VERIFICATION_MATRIX.md`、`TESTING.md` 与 current-story docs。

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib (`argparse` / `dataclasses` / `pathlib` / `re` / `tomllib`) | Python `3.14` / repo requires `>=3.14.2` | CLI、row model、path parsing、markdown/token checks | 当前 checker 与 meta guards 已全部依赖这套零新增依赖组合 |
| `pytest` | `>=7.0.0` | meta/tooling focused suites 与 thin runnable roots | 当前 `pyproject.toml`、CI、CONTRIBUTING 全部以它为标准测试入口 |
| `ruff` | `0.15.4` | touched files lint gate | 当前 repo 明确 pin；适合验证 topicization/decomposition 后的 touched files |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `yaml.safe_load` | repo dev environment（现有依赖链提供） | 读取 workflow / pre-commit / issue config truth | 仅在 meta guards 中解析 YAML 真源时使用 |
| `uv` | repo workflow standard | 统一运行 Python、pytest、ruff | 所有本地/CI 命令都要求 `uv run ...` |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| 保留单文件巨石 | 多个 internal modules + thin root | 更容易本地化失败；代价是需要设计清晰 re-export 边界 |
| 直接把 `test_toolchain_truth.py` 改成多条 CI 命令 | 保留 thin runnable root | thin root 更符合现有 `tests/meta/` topicization 模式，也最少改 command anchors |
| 新增 governance helper 文档承载 split 后规则 | 继续以 `FILE_MATRIX.md` / `VERIFICATION_MATRIX.md` / `TESTING.md` 为真源 | 避免第二条 authority chain |

**Installation:**
```bash
uv sync --frozen --extra dev
```

**Version verification:** `Python 3.14`、`pytest>=7.0.0`、`ruff==0.15.4` 已于 2026-03-22 从 `pyproject.toml` / `uv.lock` / current CI contract 核对；本 phase 无需引入新依赖。

## Architecture Patterns

### Recommended Project Structure
```text
scripts/
├── check_file_matrix.py           # thin CLI + compatibility re-exports
└── file_matrix/
    ├── inventory.py              # repo_root, iter_python_files, shared paths
    ├── classification.py         # classify_path, prefix rules, row helpers
    ├── overrides.py              # explicit FileGovernanceRow overrides
    ├── markdown.py               # render/parse FILE_MATRIX markdown
    └── validators.py             # validate_* + run_checks composition

tests/meta/
├── test_toolchain_truth.py       # thin runnable root kept for hooks/CI/docs
├── toolchain_truth_python_dx.py
├── toolchain_truth_release_identity.py
├── toolchain_truth_docs_index.py
├── toolchain_truth_ci_contract.py
└── toolchain_truth_governance_maps.py
```

### Pattern 1: Thin Compatibility Root
**What:** `scripts/check_file_matrix.py` 保留外部 module path、CLI 与 import contract，只负责 re-export 与 `main()` 编排。
**When to use:** 当 root 已被多处 meta guards / docs / hooks / CI 直接依赖时。
**Example:**
```python
# Recommended pattern; inferred from the repo's existing thin-root guard style
from .file_matrix.inventory import iter_python_files, repo_root
from .file_matrix.classification import classify_path
from .file_matrix.markdown import extract_reported_total, parse_file_matrix_paths
from .file_matrix.validators import run_checks
```

### Pattern 2: Thin Runnable Root + Non-`test_` Topic Modules
**What:** `tests/meta/test_toolchain_truth.py` 继续作为 pytest root，真实断言搬到命名清晰的 topic modules。
**When to use:** 当 daily commands、pre-push、CI 与 docs 已把某个 root file 当成稳定入口时。
**Example:**
```python
# Source pattern: tests/meta/test_public_surface_guards.py
from .public_surface_architecture_policy import *
from .public_surface_phase_notes import *
from .public_surface_runtime_contracts import *
```


### Pattern 3: Topic Boundary by Truth Home, Not by Line Count
**What:** `toolchain_truth` 按 authority home / failure mode 分 topic，而不是平均拆段。
**When to use:** 当同一文件混合 Python pins、workflow steps、docs wording、derived maps、continuity registry 等多条故事线时。
**Example:**
```text
Python / DX: pyproject.toml, .pre-commit-config.yaml, .devcontainer.json
Release identity: .github/workflows/release.yml, codeql.yml, README.md, README_zh.md
Docs index: docs/README.md, ADR, PUBLIC_SURFACES.md, DEPENDENCY_MATRIX.md
CI contract: ci.yml, scripts/lint, pytest marker truth, scripts/develop smoke
Governance maps: TESTING.md, GOVERNANCE_REGISTRY.json, VERIFICATION_MATRIX.md
```

### Anti-Patterns to Avoid
- **按行数平均切文件：** 会把 `OVERRIDES`、classifiers、validators 的真实 ownership 打散。
- **让 importer 追 internal path：** 任何外部 suite 改成 `from scripts.file_matrix...` 都是在泄漏内部实现。
- **把 authority 规则复制到 helper prose：** split 后的新 module docstring 不是新真源。
- **一次性改掉所有命令锚点：** `test_toolchain_truth.py` root path 当前已在 pre-push、CI、CONTRIBUTING、TESTING 中成锚。
- **过度 topicization：** 模块数多于 truth family 数，会把 failure localization 反向变成搜索噪音。

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| file-governance authority | 第二份 rules markdown / JSON 真源 | `FILE_MATRIX.md` + `VERIFICATION_MATRIX.md` + existing checker | authority chain 已存在，复制只会分叉 |
| toolchain suite topicization | 自定义 pytest plugin / dynamic loader | thin root + non-`test_` topic modules | 仓库已有成功先例，成本更低、语义更清晰 |
| repo root discovery | 第二个 root locator helper | 现有 `repo_root()` | 多个 root 发现策略会制造隐形漂移 |
| workflow/doc parsing | 新的 config abstraction layer | 现有 `tomllib` / `yaml.safe_load` / JSON loader helpers | phase 目标是减噪，不是再造抽象 |

**Key insight:** 这个 phase 的痛点是 truth family 混讲，不是“缺少更多框架”；最优解是重排 ownership，而不是增加系统复杂度。

## Common Pitfalls

### Pitfall 1: Public Contract Drift
**What goes wrong:** `scripts.check_file_matrix` outward names、CLI flags、返回语义或 root path 漂移。
**Why it happens:** 只盯内部结构，忽略外部 importer 与命令锚点。
**How to avoid:** 保留 module path、函数名、CLI `--write/--check/--report` 与 `run_checks()` 聚合语义。
**Warning signs:** `tests/meta/test_governance_guards.py`、budget guards、closeout guards 同时爆炸。

### Pitfall 2: Authority Chain Split-Brain
**What goes wrong:** 新 internal 模块或 phase prose 开始携带 owner / acceptance / no-growth 规则。
**Why it happens:** 把“实现分层”误当成“真源迁移”。
**How to avoid:** 只在 `FILE_MATRIX.md`、`VERIFICATION_MATRIX.md`、`TESTING.md` 与 current-story docs 写治理结论。
**Warning signs:** 需要同时改 helper prose 与正式矩阵才能说清同一规则。

### Pitfall 3: Wrong Topic Boundary for `test_toolchain_truth.py`
**What goes wrong:** 以文档类型或行数拆分，导致单个 topic 仍混合多条故事线。
**Why it happens:** 没按 authority home / failure mode 切。
**How to avoid:** 让每个 topic 对应一类失败：Python/DX、release identity、docs index、CI contract、governance maps。
**Warning signs:** 改一个 workflow step name 触发 3 个以上 topic files 同时失败。

### Pitfall 4: Cross-Suite Story Duplication
**What goes wrong:** `test_toolchain_truth.py` 与 `test_governance_release_contract.py`、`test_version_sync.py` 重复断言同一事实。
**Why it happens:** 没有先定义“谁拥有哪条真相”。
**How to avoid:** 只把 toolchain/local-DX/derived-map truth 留在 `toolchain_truth` family；版本号与 contributor/release custody 继续尊重既有 suite owner。
**Warning signs:** 同一 workflow/docs token 在多个 meta suites 中被完全重复检查。

## Code Examples

Verified patterns from current repo sources:

### Stable Import-Facing Contract
```python
# Source: tests/meta/test_governance_guards.py
from scripts.check_file_matrix import (
    extract_reported_total,
    iter_python_files,
    parse_file_matrix_paths,
    repo_root,
    run_checks,
)
```

### Existing Thin-Shell Runnable Root
```python
# Source: tests/meta/test_governance_phase_history.py
from .governance_phase_history_archive_execution import *
from .governance_phase_history_current_milestones import *
from .governance_phase_history_mid_closeouts import *
```

### Recommended Toolchain Thin Root
```python
# Recommended by analogy to the existing Phase 59 thin-shell pattern
from .toolchain_truth_python_dx import *
from .toolchain_truth_release_identity import *
from .toolchain_truth_docs_index import *
from .toolchain_truth_ci_contract import *
from .toolchain_truth_governance_maps import *
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| giant meta roots own all assertions directly | thin shell roots import named topic modules | `Phase 59` / 2026-03-22 | 更小 failure radius，命名更诚实 |
| governance truth partly lives in phase prose | current-story docs + baseline/review matrices own truth; phase docs are execution traces by default | current repo contract | split tooling 不会制造第二条故事线 |
| monolithic checker script holds every concern | thin compatibility root + internal truth families | recommended for `Phase 60` | 保持 outward contract，同时让 diffs 与 failures 更可定位 |

**Deprecated/outdated:**
- giant bucket `tests/meta/test_toolchain_truth.py` owning unrelated truth families
- `scripts/check_file_matrix.py` 继续单文件承载 all inventory / classifier / validator / render concerns
- 把新 internal module path 暴露给 hooks、CI、docs 或外部 guards

## Open Questions

1. **`tests/meta/test_toolchain_truth.py` 是否要继续保留单 root path？**
   - What we know: pre-push、CI、`CONTRIBUTING.md`、`TESTING.md` 都直接锚定它。
   - What's unclear: 是否值得在本 phase 同时重写所有命令锚点。
   - Recommendation: 保留 thin root path，先 inward topicize；若后续仍嫌粒度太粗，再单独开 phase 处理命令层 split。

2. **release/governance 相关断言要不要迁到 `test_governance_release_contract.py`？**
   - What we know: 当前已存在部分 overlap，但 `toolchain_truth` 仍拥有 Python/DX/testing-map/checker-boundary 视角。
   - What's unclear: 哪些 release/doc assertions 已经“更像 custody contract”而不是 toolchain truth。
   - Recommendation: 本 phase 只做明显 ownership 正确的 topicization；避免一次性大规模跨-suite 挪动，先保 failure localization 与 daily root 稳定。

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest` + direct checker CLI |
| Config file | `pyproject.toml` |
| Quick run command | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py` |
| Full suite command | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py tests/meta/test_evidence_pack_authority.py tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py tests/meta/test_phase50_rest_typed_budget_guards.py tests/meta/test_governance_closeout_guards.py` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HOT-14 | thin `scripts.check_file_matrix` keeps CLI/import contract while internal families split inward | meta/integration | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_evidence_pack_authority.py tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py tests/meta/test_phase50_rest_typed_budget_guards.py tests/meta/test_governance_closeout_guards.py` | ✅ |
| TST-12 | `test_toolchain_truth` topicization preserves daily guard semantics and narrower failure radius | meta | `uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py` | ✅ |
| GOV-44 | docs/matrix/current-story freeze remains one story after split | meta/governance | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py tests/meta/test_governance_closeout_guards.py` | ✅ |

### Sampling Rate
- **Per task commit:** `uv run python scripts/check_file_matrix.py --check` plus the touched focused meta root
- **Per wave merge:** quick run command above
- **Phase gate:** full suite command above must stay green before `/gsd:verify-work`

### Wave 0 Gaps
None — 现有 `pytest` / meta-guard / checker 基础设施已足够；本 phase 需要的是边界重排，不是新测试框架。

## Sources

### Primary (HIGH confidence)
- `.planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/60-PRD.md` - phase goal, scope, success criteria
- `.planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/60-CONTEXT.md` - locked decisions, canonical refs, execution shape
- `.planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/60-VALIDATION.md` - required wave order and gate commands
- `.planning/v1.12-MILESTONE-AUDIT.md` - why `Phase 60` is routed next, not a blocker to `v1.12`
- `.planning/reviews/V1_12_EVIDENCE_INDEX.md` - existing thin-root / localized verification closeout pattern
- `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-REMEDIATION-ROADMAP.md` - forward route and anti-routes
- `scripts/check_file_matrix.py` - current hotspot composition and outward contract
- `tests/meta/test_toolchain_truth.py` - current topic buckets and failure radius
- `tests/meta/test_governance_guards.py` - importer contract and governance checker expectations
- `tests/meta/test_public_surface_guards.py`, `tests/meta/test_governance_phase_history.py` - established thin-shell topicization pattern
- `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `CONTRIBUTING.md`, `.planning/codebase/TESTING.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/reviews/FILE_MATRIX.md` - live command anchors and authority chain

### Secondary (MEDIUM confidence)
- None — this research is driven by current repo truth, not external ecosystem choice.

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - repo pins and command contracts are explicit in `pyproject.toml`, CI, and contributor docs.
- Architecture: HIGH - recommendation follows the current importer graph plus already-landed thin-shell patterns from `Phase 59`.
- Pitfalls: HIGH - risks come directly from existing hooks, workflows, docs anchors, and authority docs.

**Research date:** 2026-03-22
**Valid until:** 2026-03-29
