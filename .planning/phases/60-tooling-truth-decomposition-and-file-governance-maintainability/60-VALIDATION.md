---
phase: 60
slug: tooling-truth-decomposition-and-file-governance-maintainability
status: planned
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-22
---

# Phase 60 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `uv run pytest -q ...` focused meta/tooling verification + `uv run python scripts/check_file_matrix.py --check` |
| **Config file** | `pyproject.toml` |
| **Smoke command** | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py` |
| **Phase gate command** | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py tests/meta/test_evidence_pack_authority.py tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py tests/meta/test_phase50_rest_typed_budget_guards.py tests/meta/test_governance_closeout_guards.py` |
| **Estimated runtime** | `~10-120s` |

## Wave Structure

- **Wave 1:** `60-01` decompose `scripts/check_file_matrix.py` into internal truth families while keeping outward contract stable
- **Wave 2:** `60-02` topicize `tests/meta/test_toolchain_truth.py` by concern boundary / truth family
- **Wave 3:** `60-03` freeze new tooling topology into governance docs, file matrix, verification matrix, testing map, and touched guards

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 60-01-01 | 01 | 1 | HOT-14 | checker decomposition preserves CLI / import contract | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_evidence_pack_authority.py tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py tests/meta/test_phase50_rest_typed_budget_guards.py tests/meta/test_governance_closeout_guards.py` | ⬜ pending |
| 60-01-02 | 01 | 1 | HOT-14 | importer-facing compatibility remains stable for all checker consumers | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_evidence_pack_authority.py tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py tests/meta/test_phase50_rest_typed_budget_guards.py tests/meta/test_governance_closeout_guards.py` | ⬜ pending |
| 60-02-01 | 02 | 2 | TST-12 | toolchain truth topicization preserves daily guard semantics | `uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py tests/meta/test_governance_release_contract.py` | ⬜ pending |
| 60-02-02 | 02 | 2 | TST-12 | release/docs/governance semantics remain aligned after topicization | `uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py tests/meta/test_governance_release_contract.py` | ⬜ pending |
| 60-03-01 | 03 | 3 | GOV-44 | docs / matrix / current-story freeze stays coherent after tooling split | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py tests/meta/test_governance_closeout_guards.py` | ⬜ pending |
| 60-03-02 | 03 | 3 | GOV-44 | current-story docs and closeout ledgers keep one authority chain after Phase 60 | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py tests/meta/test_governance_closeout_guards.py` | ⬜ pending |

## Manual-Only Verifications

- 确认 `scripts/check_file_matrix.py` 的 outward contract 仍由单一 root 暴露，而不是让 importers 追着 internal module path 改名。
- 确认 `tests/meta/test_toolchain_truth.py` 的 topicization 真正降低 failure radius，而不是只把 giant suite 平移成多个 prose-heavy 噪音文件。
- 确认 `FILE_MATRIX / VERIFICATION_MATRIX / TESTING / current-story docs` 仍是 authority truth，本 phase 没有复制出第二套 governance prose。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `checker decomposition -> toolchain topicization -> truth freeze`.
- [x] `nyquist_compliant: true` set in frontmatter.
- [ ] Execution evidence recorded.
