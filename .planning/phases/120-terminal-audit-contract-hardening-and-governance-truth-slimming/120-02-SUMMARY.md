---
phase: 120-terminal-audit-contract-hardening-and-governance-truth-slimming
plan: "02"
subsystem: auth
tags: [home-assistant, config-flow, translations, pytest, error-taxonomy]
requires: []
provides:
  - explicit login flow keys for malformed response, API failure, and unexpected internal failure
  - explicit invalid_entry semantics for reauth and reconfigure persisted-entry defects
  - focused regressions and bilingual translations that freeze the flow taxonomy
affects: [config-flow, translations, flow-testing]
tech-stack:
  added: []
  patterns:
    - explicit translated flow error taxonomy
    - persisted-entry validation maps to invalid_entry instead of unknown
key-files:
  created:
    - .planning/phases/120-terminal-audit-contract-hardening-and-governance-truth-slimming/120-02-SUMMARY.md
  modified:
    - custom_components/lipro/flow/login.py
    - custom_components/lipro/flow/submission.py
    - custom_components/lipro/translations/en.json
    - custom_components/lipro/translations/zh-Hans.json
    - tests/flows/test_config_flow_user.py
    - tests/flows/test_config_flow_reauth.py
    - tests/flows/test_config_flow_reconfigure.py
    - tests/flows/test_flow_submission.py
key-decisions:
  - "Preserved invalid_auth and cannot_connect while introducing api_error, invalid_response, unexpected_error, and invalid_entry as stable flow keys."
  - "Reserved unknown for truly unclassified failures so malformed responses and persisted-entry corruption no longer collapse into one bucket."
patterns-established:
  - "Flow helpers normalize upstream and stored-entry failures into explicit translated UI-facing keys."
  - "Focused regressions must assert the same taxonomy vocabulary used by translation catalogs."
requirements-completed: [QLT-47, TST-42]
duration: 3m
completed: 2026-04-01
---

# Phase 120 Plan 120-02: flow taxonomy hardening summary

**Config flows now surface explicit translated categories for malformed login responses, API failures, unexpected internal failures, and invalid persisted-entry state**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-01T05:21:26Z
- **Completed:** 2026-04-01T05:24:13Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments
- Preserved existing `invalid_auth` and `cannot_connect` semantics while adding explicit login failure keys for malformed upstream responses, generic API failures, and unexpected internal failures.
- Reclassified reauth and reconfigure persisted-entry defects to `invalid_entry`, including missing or invalid stored `phone_id` and malformed stored phone data.
- Synchronized English and Simplified Chinese translations with focused regressions across user, reauth, reconfigure, and submission helper flows.

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: failing flow taxonomy regressions** - `78ceba3` (`test`)
2. **Task 1 GREEN: refine login flow error taxonomy** - `e911bf7` (`fix`)
3. **Task 2 GREEN: classify persisted entry flow failures** - `4e5b3e5` (`fix`)

## Files Created/Modified
- `custom_components/lipro/flow/login.py` - Maps hashed-login failures to `invalid_auth`, `cannot_connect`, `api_error`, `invalid_response`, and `unexpected_error`.
- `custom_components/lipro/flow/submission.py` - Maps reauth/reconfigure stored-entry defects to `invalid_entry` while preserving field-level validation errors.
- `custom_components/lipro/translations/en.json` - Adds English strings for the new flow error vocabulary.
- `custom_components/lipro/translations/zh-Hans.json` - Adds Simplified Chinese strings for the new flow error vocabulary.
- `tests/flows/test_config_flow_user.py` - Freezes login taxonomy expectations for malformed/API/unexpected failures.
- `tests/flows/test_config_flow_reauth.py` - Freezes reauth invalid-entry behavior for missing `phone_id`.
- `tests/flows/test_config_flow_reconfigure.py` - Freezes reconfigure invalid-entry behavior for missing `phone_id`.
- `tests/flows/test_flow_submission.py` - Covers helper-level invalid-entry cases, including malformed stored phone data.
- `.planning/phases/120-terminal-audit-contract-hardening-and-governance-truth-slimming/120-02-SUMMARY.md` - Records execution scope, decisions, and verification.

## Decisions Made
- Used `api_error`, `invalid_response`, `unexpected_error`, and `invalid_entry` as the new stable taxonomy because each class now maps to a distinct remediation/debugging path.
- Kept existing field-level `invalid_phone`, `invalid_password`, and `reauth_user_mismatch` behavior unchanged to avoid semantic drift in existing UX paths.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added persisted-entry regression for malformed stored phone**
- **Found during:** Task 120-02-02
- **Issue:** Existing focused coverage froze missing or invalid `phone_id`, but did not explicitly protect the malformed stored-phone path in reauth validation.
- **Fix:** Added one helper-level regression asserting malformed stored phone data maps to `invalid_entry`.
- **Files modified:** `tests/flows/test_flow_submission.py`
- **Verification:** `uv run pytest tests/flows/test_config_flow_reauth.py tests/flows/test_config_flow_reconfigure.py tests/flows/test_flow_submission.py -q`
- **Committed in:** `78ceba3`

---

**Total deviations:** 1 auto-fixed (1 missing critical)
**Impact on plan:** Tightened the plan intent without widening scope; the extra regression closes an uncovered persisted-entry defect path.

## Issues Encountered
- None - planned RED/GREEN sequence completed without blocking issues.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Flow taxonomy, translations, and focused regressions are aligned and ready for downstream audits or broader verification.
- `unknown` remains available for future truly unclassified failures, but the audited flow paths no longer rely on it as a catch-all.

## Self-Check: PASSED
- Found summary file at `.planning/phases/120-terminal-audit-contract-hardening-and-governance-truth-slimming/120-02-SUMMARY.md`
- Verified task commits `78ceba3`, `e911bf7`, and `4e5b3e5` exist in git history

---
*Phase: 120-terminal-audit-contract-hardening-and-governance-truth-slimming*
*Completed: 2026-04-01*
