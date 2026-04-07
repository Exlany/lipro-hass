# Phase 113: Hotspot burn-down and changed-surface assurance hardening - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning

<domain>
## Phase Boundary

本阶段只处理 `QLT-46`：把仍然处于 current route 上、且具备 **低 blast radius / 高维护收益** 的 production hotspots 继续 inward split，或用 focused no-regrowth guards + changed-surface assurance 把剩余 allowance 冻结成可审计真相。

本阶段优先目标：
- 把 `custom_components/lipro/core/anonymous_share/share_client_submit.py` 从 giant support carrier 继续拆成更细的 local collaborators；
- 把 `custom_components/lipro/core/command/result.py` 从 stable export + helper ballast carrier 继续 inward split，但保持它仍是 outward stable export home；
- 为 remaining large-but-sanctioned hotspots 建立显式 budget / locality / focused-test guard，而不是默认它们可以长期无上限膨胀；
- 把 focused hotspot assurance 纳入 maintainer 日常本地门禁，而不只存在于 `--full` 全量模式。

本阶段**不**处理：
- `Phase 112` 已完成的 route truth / formal-home discoverability 收口；
- public reachability、security fallback、delegate continuity、single-maintainer continuity（留给 `Phase 114` 或后续治理工作）；
- 触碰 predecessor-heavy 且 blast radius 更大的 `status_fallback_support.py` 主体结构，只允许对其设置 bounded allowance / no-growth guard，不在本阶段重开大拆；
- 新 feature、新 public surface、新 root，或任何 second-root / compat shell 回流。

</domain>

<decisions>
## Implementation Decisions

### Hotspot selection
- **D-01:** `share_client_submit.py` 与 `result.py` 是本阶段首选 production hotspots：它们体量较大、职责可自然分组、测试覆盖成熟、治理 blast radius 小于 `status_fallback_support.py` / `rest_decoder.py` 一类 predecessor-sensitive carriers。
- **D-02:** `status_fallback_support.py`、`rest_facade.py`、`manager.py`、`rest_decoder.py`、`firmware_update.py` 等 remaining hotspots 本阶段以 **bounded no-regrowth allowance** 方式冻结，不在同一 phase 内把 predecessor guards 全面打碎重写。

### Architecture invariants
- **D-03:** `custom_components/lipro/core/anonymous_share/share_client_submit.py` 继续是 submit flow 的 formal local home，但允许把 outcome builders / attempt resolution inward split 到 sibling support modules。
- **D-04:** `custom_components/lipro/core/command/result.py` 继续是 stable export / failure arbitration home；任何 inward split 只能下沉 internal helper，不能改变 outward import story。
- **D-05:** 新 helper modules 必须保持 strictly local importer story：只能被 owning hotspot shell / home 导入，不得升级为新 public surface 或第二 authority chain。

### Assurance / governance
- **D-06:** `Phase 113` 必须新增 focused no-regrowth guard，显式声明 remaining hotspots 的 line/function budgets 与 helper locality。
- **D-07:** `scripts/lint` 默认模式不再只停留在 static + docs-route + security smoke；当 touched surface 命中 `Phase 113` hotspots / guards / planning truth 时，必须自动执行 focused assurance run。
- **D-08:** phase closeout 必须把 `PROJECT/ROADMAP/REQUIREMENTS/STATE/MILESTONES` 与 governance current truth 前推到 `Phase 113 complete / Phase 114 discussion-ready`，不能留下“代码完成但 route truth 仍停在 planning-ready”的半收口状态。

### Repository-wide audit findings (recorded, not all in-scope)
- **D-09:** 当前仓库仍有更高层治理问题：`gsd-tools` 私有依赖写入测试、promoted assets 第二真源、planning route truth 多处硬编码、`.planning/codebase` freshness 漂移、planning link audit 未覆盖、贡献者入口过重、release continuity 单点。它们必须进入最终审查报告，但不全部强塞进 `QLT-46`。
- **D-10:** remaining hotspot allowance 不只是 phase-local test truth；它还属于 residual / delete-gate truth。凡是 `Phase 113` 冻结的 no-growth budgets，必须同步落到 `.planning/reviews/RESIDUAL_LEDGER.md` 与 `.planning/reviews/KILL_LIST.md`，不能只存在于单个 meta guard。

### the agent's Discretion
- 可决定 `share_client_submit.py` / `result.py` 的 inward split 颗粒度，只要 outward semantics 与 import homes 不漂移。
- 可决定 focused lint 使用 changed-file auto-detect 还是 narrow static trigger，只要默认模式能真实覆盖 touched hotspot surfaces。
- 可决定 remaining hotspot budgets 的具体阈值，只要阈值显式、machine-checkable、no-growth。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Active-route truth
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `tests/meta/governance_current_truth.py`

### Architecture / review truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`
- `CONTRIBUTING.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- `.planning/codebase/CONVENTIONS.md`
- `.planning/codebase/TESTING.md`
- `tests/meta/toolchain_truth_ci_contract.py`

### Production hotspots under direct consideration
- `custom_components/lipro/core/anonymous_share/share_client_submit.py`
- `custom_components/lipro/core/command/result.py`
- `custom_components/lipro/core/api/status_fallback_support.py`
- `custom_components/lipro/core/api/rest_facade.py`
- `custom_components/lipro/core/anonymous_share/manager.py`
- `custom_components/lipro/core/protocol/boundary/rest_decoder.py`
- `custom_components/lipro/entities/firmware_update.py`

### Guard / assurance predecessors
- `tests/meta/test_phase70_governance_hotspot_guards.py`
- `tests/meta/test_phase71_hotspot_route_guards.py`
- `tests/meta/test_phase95_hotspot_decomposition_guards.py`
- `tests/meta/test_phase99_runtime_hotspot_support_guards.py`
- `tests/meta/test_phase107_rest_status_hotspot_guards.py`

### Changed-surface verification candidates
- `tests/core/test_share_client_submit.py`
- `tests/core/test_command_result.py`
- `scripts/lint`
- `scripts/check_file_matrix.py`

</canonical_refs>

<specifics>
## Specific Ideas

- `113-01` 只拆 `share_client_submit.py`：把 outcome builder / attempt resolution 压回 sibling modules，让主文件只保留 preflight + refresh + top-level orchestration。
- `113-02` 只拆 `result.py`：把 unconfirmed/failure helper ballast inward split，保留 outward stable export story。
- `113-03` 只处理 hotspot assurance：把 remaining >400-line production carriers 的 exact budget / locality / focused assurance 写成 machine-checkable truth，并让 `scripts/lint` 默认模式在 touched hotspots 或 governance handoff truth 变更时自动跑对应 focused suites。
- `113-04` 专做 closeout：同步 `PROJECT/ROADMAP/REQUIREMENTS/STATE/MILESTONES` 与 governance current truth 到 `Phase 113 complete / Phase 114 discussion-ready`，并写出 `113-VERIFICATION.md`、`113-SUMMARY.md`、`113-AUDIT.md`。
- `113-03` 与 `113-04` 不得再合并成单个宽任务；guard/lint assurance 与 route closeout 必须分开验证、分开交付。

</specifics>

<deferred>
## Deferred Ideas

- `gsd-tools` 私有依赖从测试/closeout guards 中完全剥离。
- promoted assets allowlist 真源收敛。
- `.planning/codebase` freshness contract 与 planning link audit 扩展。
- contributor onramp 降压与 release continuity / delegate model 设计。
- `status_fallback_support.py` 的大规模结构重写（若仍需要，应作为单独高 blast radius phase）。

</deferred>
