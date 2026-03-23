---
phase: 66-release-target-fidelity-adapter-root-cleanup-and-focused-protocol-coverage-hardening
plan: "01"
status: completed
completed_at: "2026-03-23T00:00:00Z"
verification:
  - uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py
---

# Phase 66 Plan 01 Summary

## Objective

Align release-target validation with tagged refs and remove stale release/install current-story drift across README, baseline, reviews, and governance guards.

## Completed Work

- `.github/workflows/ci.yml` now accepts an optional reusable `ref` input and all checkout steps honor the same ref truth.
- `.github/workflows/release.yml` now reuses CI gates against `refs/tags/${RELEASE_TAG}` so validation and publish paths stop telling different stories.
- `README.md` and `README_zh.md` now use freshness-safe `<release-tag>` examples instead of encoding one stale literal tag as the canonical install path.
- `docs/README.md`, `.planning/baseline/PUBLIC_SURFACES.md`, `.planning/baseline/AUTHORITY_MATRIX.md`, and `.planning/reviews/README.md` now agree that `v1.14 / Phase 66` is the active route and that archive pointers remain pull-only historical evidence.
- `tests/meta/test_governance_release_contract.py` now guards the new reusable-ref contract and freshness-safe release examples.

## Files Modified

- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `README.md`
- `README_zh.md`
- `docs/README.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/AUTHORITY_MATRIX.md`
- `.planning/reviews/README.md`
- `tests/meta/test_governance_release_contract.py`

## Verification

- `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` → `45 passed in 3.56s`

## Scope Notes

- This plan focused on release-target / current-story truth only and did not yet touch HA adapter roots or protocol seam tests.
