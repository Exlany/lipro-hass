# Phase 79 Research

## Audit Verdict

Repository-wide review shows the codebase is structurally mature:

- `custom_components/lipro/**` already follows the north-star single-chain architecture with clear protocol/runtime/control/domain separation.
- Active residual families are empty in `.planning/reviews/RESIDUAL_LEDGER.md`.
- Open-source entrypoints, release/security/support docs, and CI/release contracts are unusually complete for a Home Assistant integration.

The highest remaining maintainability cost is no longer feature correctness, but governance/tooling density.

## Hotspot Findings

### 1. `scripts/check_file_matrix_registry.py` is the main maintainability hotspot

- It is the largest non-test Python file in the repository (`605` lines).
- `uv run ruff check custom_components/lipro scripts tests --select C901` currently reports the repo's only active `C901` hit here.
- Local complexity scan showed:
  - `_classify_test_path` → `cc=31`
  - `_classify_component_path` → `cc=25`
- The file mixes three responsibilities: override-truth families, path classification rules, and dispatch glue.

### 2. `tests/meta/test_governance_release_contract.py` is correct but too dense

- It is `638` lines and carries many concerns in one file: CI/release workflow gates, docs/support/security routing, continuity/custody truth, release identity, preview/rehearsal mode, and quality-scale/devcontainer sync.
- This lowers failure localization and makes future edits expensive.
- A split should preserve a stable release-contract anchor while moving most concern-specific assertions to narrower files.

### 3. Production hotspots exist, but they are lower ROI right now

- Local complexity scan also highlighted `custom_components/lipro/core/api/auth_recovery.py:244` and `custom_components/lipro/core/api/schedule_service.py:97`.
- These are real but non-blocking; they are materially healthier than the governance/tooling hotspots and do not justify reopening production seams in this phase.

## Why this phase should stay governance/tooling-only

- It keeps `v1.21`'s milestone name honest: this still belongs to governance / planning-route maintainability.
- It avoids creating unnecessary churn in production code after the repository has already cleared the more valuable structural refactors.
- It converts the last obvious “correct but hard to maintain” governance hotspots into thinner, more discoverable homes.

## Recommended plan split

1. **Route + contract activation for Phase 79**
   - Open the current route for one final maintainability pass.
   - Add `Phase 79` truth to active docs/contracts and define its exit contract.

2. **Registry hotspot decomposition**
   - Split `check_file_matrix_registry.py` into narrower companion modules.
   - Keep one thin import home and preserve the same outward contract.
   - Add focused tests for classifier behavior and override integrity.

3. **Release-contract topicization + closeout**
   - Split release-contract tests into concern-oriented suites while keeping a stable anchor.
   - Update file-matrix/verification/review assets and close the route back to milestone closeout-ready.
