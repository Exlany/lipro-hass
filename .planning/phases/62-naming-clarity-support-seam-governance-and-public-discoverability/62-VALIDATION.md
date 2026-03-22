---
phase: 62
slug: naming-clarity-support-seam-governance-and-public-discoverability
status: planned
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-22
---

# Phase 62 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `uv run pytest -q ...` focused device-extras/governance/docs guards + `uv run python scripts/check_file_matrix.py --check` |
| **Config file** | `pyproject.toml` |
| **Smoke command** | `uv run pytest -q tests/core/device/test_extras_payloads.py tests/core/device/test_extras_features.py tests/platforms/test_light_model_and_commands.py tests/platforms/test_switch_behavior.py tests/platforms/test_select_models.py tests/meta/public_surface_phase_notes.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_phase62_naming_discoverability_guards.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_version_sync.py` |
| **Phase gate command** | `uv run pytest -q tests/core/device/test_extras_payloads.py tests/core/device/test_extras_features.py tests/platforms/test_light_model_and_commands.py tests/platforms/test_switch_behavior.py tests/platforms/test_select_models.py tests/meta/public_surface_phase_notes.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_phase62_naming_discoverability_guards.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py && uv run python scripts/check_file_matrix.py --check` |
| **Estimated runtime** | `~10-90s` |

## Wave Structure

- **Wave 1:** `62-01` keep-vs-rename inventory + low-fanout `DeviceExtras` rename，与 `62-02` public docs fast-path convergence 可并行执行；生产写集与 docs 写集分离。
- **Wave 2:** `62-03` governance freeze 依赖 `62-01` 与 `62-02` 的最终裁决后统一回写 baseline/review truth。
- **Wave 3:** `62-04` focused guards + current-story closeout 依赖 `62-03`，用于冻结最终 topology 与 discoverability route。

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 62-01-01 | 01 | 1 | RES-14 | low-fanout `DeviceExtras` support rename preserves outward behavior | `uv run pytest -q tests/core/device/test_extras_payloads.py tests/core/device/test_extras_features.py tests/platforms/test_light_model_and_commands.py tests/platforms/test_switch_behavior.py tests/platforms/test_select_models.py` | ⬜ pending |
| 62-01-02 | 01 | 1 | RES-14 | honest support/surface seams remain explicitly non-public in active truth | `uv run pytest -q tests/meta/public_surface_phase_notes.py tests/meta/test_dependency_guards.py` | ⬜ pending |
| 62-02-01 | 02 | 1 | DOC-07 | root README / docs index / contributor fast path keep one public-first-hop story | `uv run pytest -q tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_version_sync.py` | ⬜ pending |
| 62-02-02 | 02 | 1 | DOC-07 | maintainer-only routing stays out of the public first hop | `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/toolchain_truth_docs_fast_path.py` | ⬜ pending |
| 62-03-01 | 03 | 2 | GOV-45 | baseline and review ledgers freeze the final keep-vs-rename decisions | `uv run pytest -q tests/meta/public_surface_phase_notes.py tests/meta/test_dependency_guards.py` | ⬜ pending |
| 62-03-02 | 03 | 2 | GOV-45 | machine-readable governance and file matrix remain in sync | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_version_sync.py tests/meta/toolchain_truth_docs_fast_path.py` | ⬜ pending |
| 62-04-01 | 04 | 3 | GOV-45 | anti-regression guards block stale terminology and duplicate discoverability routes | `uv run pytest -q tests/meta/public_surface_phase_notes.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_phase62_naming_discoverability_guards.py tests/meta/test_governance_guards.py` | ⬜ pending |
| 62-04-02 | 04 | 3 | GOV-45 | current-story docs and promoted evidence acknowledge Phase 62 closeout truth | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` | ⬜ pending |

## Manual-Only Verifications

- 确认 `extra_support.py -> extras_support.py` 只改善 family naming，不改变 `DeviceExtras` outward behavior。
- 确认 root README / README_zh 只保留 public first hop，maintainer-only runbook 没有回流到公开入口。
- 确认 docs wording 与 baseline/review/current-story docs 讲的是同一条 naming/discoverability 故事，而不是三套并行叙事。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave design keeps code/docs/governance write sets staged and reviewable.
- [x] `nyquist_compliant: true` set in frontmatter.
- [ ] Execution evidence recorded.
