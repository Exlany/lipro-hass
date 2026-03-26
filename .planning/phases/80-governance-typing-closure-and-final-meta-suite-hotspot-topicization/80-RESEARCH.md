# Phase 80 Research

## Audit signals

- `uv run mypy --follow-imports=silent .` currently fails on the governance/tooling seam rather than production code.
- `uv run ruff check custom_components scripts tests --select C901,PLR0911,PLR0912,PLR0915,PLR0913` shows no remaining `C901` hotspots, but it still highlights oversized single-test bodies in:
  - `tests/meta/governance_followup_route_current_milestones.py`
  - `tests/meta/test_governance_release_contract.py`
- The largest production modules remain below the urgency level that would justify reopening them before these governance/tooling residuals are closed.

## Chosen direction

### 1. Fix type honesty at the root
Use explicit exports and typed helper boundaries:
- re-export `FileGovernanceRow` from the registry root if downstream modules consume it there;
- convert raw JSON/object navigation in governance smoke tests to typed dictionaries/helpers.

### 2. Finish governance hotspot decomposition where it still matters
The remaining ROI is in test failure localization, not more file proliferation:
- split the giant follow-up route test into multiple smaller tests within the same concern home unless a new stable home becomes obviously cleaner;
- break the remaining oversized release workflow anchor into narrower workflow-focused tests while preserving one honest anchor file.

### 3. Freeze Phase 80 as the new live story
After execution, all active docs/tests/review assets must route to `Phase 80 complete`, and GSD fast-path must return to milestone closeout.

## Rejected alternatives

- **Reopen production hotspots first**: not selected because current scans show no failing quality gates there; doing so now would be lower ROI and risk wider churn.
- **Create many more topic files immediately**: rejected unless a stable concern boundary clearly exists; smaller focused tests inside current homes are often sufficient.
- **Use broad `Any`/ignore` to clear mypy**: rejected because it would hide the exact type-honesty problem this phase is meant to close.
