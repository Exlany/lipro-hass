# Phase 58 Remediation Roadmap

## Route Principles

- 只沿单一正式主链收口，不重开“第二根”叙事。
- 先打 failure localization / audit freshness / tooling maintainability，再做 aesthetic cleanup。
- 对“正确但偏厚”的 formal home，采用 `keep + split inward + forbid growth`，而不是先宣判为 residual。
- 不把 open-source honesty 与 real-world resilience 混为一谈：能文档化就文档化，不能凭空承诺。

## Priority Bands

### P0 — Highest leverage next
1. **verification localization / megaguard topicization**
2. **refresh-proof governance/tooling maintainability**（先看 `scripts/check_file_matrix.py` 与大型 governance tests）

### P1 — High-value structural refinement
1. **large-but-correct formal-home slimming**（anonymous share / diagnostics API / selected platform homes）
2. **naming and support-only seam clarity**

### P2 — Follow-through / polish
1. **public discoverability and contributor-path simplification**
2. **selective platform/test topicization for still-long suites**

## Recommended Phase Seeds

### Phase 59 — Verification localization and governance guard topicization
**Why now:** current highest maintenance cost sits in large meta guards and broad tests, not in root architecture correctness.
**Target families:** `tests/meta/test_public_surface_guards.py`, `tests/meta/test_governance_phase_history.py`, `tests/core/test_device_refresh.py`, related truth docs.
**Suggested checks:** `uv run pytest -q tests/meta/test_public_surface_guards.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_followup_route.py tests/meta/test_dependency_guards.py`

### Phase 60 — Tooling hotspot decomposition and file-governance maintainability
**Why now:** `scripts/check_file_matrix.py` is highly valuable but now big enough to deserve inward decomposition and clearer ownership notes.
**Target families:** `scripts/check_file_matrix.py`, `tests/meta/test_toolchain_truth.py`, `.planning/reviews/FILE_MATRIX.md`, `.planning/baseline/VERIFICATION_MATRIX.md`.
**Suggested checks:** `uv run python scripts/check_file_matrix.py --check` plus touched meta suites.

### Phase 61 — Formal-home slimming for large but correct modules
**Why now:** several production homes are architecturally right yet still denser than ideal.
**Target families:** `custom_components/lipro/core/anonymous_share/manager.py`, `custom_components/lipro/core/anonymous_share/share_client.py`, `custom_components/lipro/core/api/diagnostics_api_service.py`, `custom_components/lipro/core/ota/candidate.py`, `custom_components/lipro/select.py`.
**Suggested checks:** targeted family regressions + `uv run ruff check` on touched zones.

### Phase 62 — Naming clarity and public discoverability follow-through
**Why now:** next-order friction comes from support/helper/service naming density and high-density contributor/public docs.
**Target families:** `*_support.py`, `*_surface.py`, selected docs/config entry assets, retired script discoverability.
**Suggested checks:** docs/meta/toolchain truth suites + targeted grep guards if needed.

## Sequencing Advice

1. 先做 `Phase 59`，把大守卫/大测试的 failure radius 降下来。
2. 再做 `Phase 60`，避免 tooling truth 自己成为新 hotspot。
3. 然后处理 `Phase 61`，把 production thick homes 继续 inward slimming。
4. 最后做 `Phase 62`，清理命名与开放入口噪音。

## Anti-Routes

- 不要把“active residual families currently none”误解成“仓库已经不需要任何 follow-up”。
- 不要在未刷新验证定位之前就开启大规模代码搬迁。
- 不要把 `v1.10` 未归档状态误写成已 archive；这只是 closeout sequencing，不是缺陷本身。

## Route Verdict

`Phase 58` 之后，仓库的正确下一步不是重新做一轮 broad audit，而是按上面的 `Phase 59 -> 62` 逐个处理 maintainability precision 问题。
