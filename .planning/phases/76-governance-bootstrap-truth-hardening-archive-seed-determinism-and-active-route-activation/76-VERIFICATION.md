---
phase: 76-governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation
verified: 2026-03-26T09:45:26Z
status: passed
score: 9/9 must-haves verified
---

# Phase 76: Governance bootstrap truth hardening, archive-seed determinism, and active-route activation Verification Report

**Phase Goal:** 把 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 之间的 current-route / latest-archive truth 收口成 deterministic bootstrap contract，确保 active route 激活不再依赖 hidden heading order 或历史 prose 漏洞。
**Verified:** 2026-03-26T09:45:26Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | current bootstrap consumers resolve one explicit active milestone and latest archived baseline | ✓ VERIFIED | `.planning/PROJECT.md:10`, `.planning/ROADMAP.md:28`, `.planning/REQUIREMENTS.md:32`, `.planning/STATE.md:38`, `.planning/MILESTONES.md:5`, `tests/meta/governance_current_truth.py:24`, `tests/meta/governance_current_truth.py:93` |
| 2 | `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` no longer rely on heading order or prose placement for current route | ✓ VERIFIED | `.planning/MILESTONES.md:3`, `.planning/PROJECT.md:50`, `tests/meta/governance_current_truth.py:96` |
| 3 | bootstrap smoke resolves one deterministic `v1.21` / `v1.20` story | ✓ VERIFIED | `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init new-milestone` → `current_milestone=v1.21`, `latest_completed_milestone=v1.20`; `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init plan-phase 76` → `phase_found=true`, `phase_req_ids=GOV-57, ARC-20` |
| 4 | historical milestone bodies remain readable/auditable but are demoted behind the explicit current-route contract | ✓ VERIFIED | `.planning/ROADMAP.md:26`, `.planning/ROADMAP.md:439`, `.planning/MILESTONES.md:48`, `.planning/MILESTONES.md:371`, `.planning/REQUIREMENTS.md:70`, `.planning/REQUIREMENTS.md:103` |
| 5 | parser-visible selectors for current/latest milestone live in dedicated route-contract sections, not historical narrative blocks | ✓ VERIFIED | `.planning/MILESTONES.md:3`, `.planning/MILESTONES.md:5`, `tests/meta/governance_followup_route_current_milestones.py:193`, `tests/meta/governance_followup_route_current_milestones.py:207`, `tests/meta/test_governance_milestone_archives.py:596` |
| 6 | archive-focused guards fail if old prose regains selector precedence or current-state wording returns | ✓ VERIFIED | `tests/meta/governance_followup_route_current_milestones.py:200`, `tests/meta/governance_followup_route_current_milestones.py:207`, `tests/meta/test_phase75_governance_closeout_guards.py:74`, `tests/meta/test_phase75_governance_closeout_guards.py:80`, `tests/meta/test_governance_milestone_archives.py:602` |
| 7 | active-route docs and state describe the same post-Phase-76 truth: `v1.21` active, `v1.20` latest archived baseline | ✓ VERIFIED | `.planning/PROJECT.md:5`, `.planning/ROADMAP.md:54`, `.planning/STATE.md:32`, `.planning/STATE.md:64`, `uv run python - <<'PY' ...` → `all_equal True` |
| 8 | latest archived evidence pointer remains fixed at `.planning/reviews/V1_20_EVIDENCE_INDEX.md` | ✓ VERIFIED | `.planning/PROJECT.md:29`, `.planning/PROJECT.md:38`, `.planning/REQUIREMENTS.md:51`, `.planning/STATE.md:57`, `.planning/MILESTONES.md:24`, `.planning/baseline/VERIFICATION_MATRIX.md:394` |
| 9 | verification / file-matrix / release guards detect drift in route status, default next command, and archive pointer | ✓ VERIFIED | `.planning/baseline/VERIFICATION_MATRIX.md:391`, `.planning/reviews/FILE_MATRIX.md:551`, `.planning/reviews/FILE_MATRIX.md:554`, `.planning/reviews/FILE_MATRIX.md:567`, `.planning/reviews/FILE_MATRIX.md:575`, `.planning/reviews/FILE_MATRIX.md:597`, `tests/meta/test_governance_closeout_guards.py:248`, `tests/meta/test_governance_release_contract.py:391`, `tests/meta/test_version_sync.py:325` |

**Score:** 9/9 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `.planning/PROJECT.md:5` | expose current route, active baseline, default next command, archive pointer | ✓ VERIFIED | Current route is `v1.21 active route / Phase 76 execution-ready / latest archived baseline = v1.20`; contract block at `.planning/PROJECT.md:10` matches shared helper |
| `.planning/ROADMAP.md:28` | expose the same machine-readable route contract and Phase 76 current milestone | ✓ VERIFIED | Contract block precedes milestone prose; Phase 76 remains `Execution-ready` at `.planning/ROADMAP.md:66` |
| `.planning/REQUIREMENTS.md:5` | expose current mutable story and Phase 76 requirement basket | ✓ VERIFIED | GOV-57 / ARC-20 are declared at `.planning/REQUIREMENTS.md:9`; shared contract matches at `.planning/REQUIREMENTS.md:32` |
| `.planning/STATE.md:30` | expose active milestone, default next command, and shared route contract | ✓ VERIFIED | State names `v1.21`, `Phase 76 execution-ready`, `$gsd-execute-phase 76`, and pointer `.planning/reviews/V1_20_EVIDENCE_INDEX.md` |
| `.planning/MILESTONES.md:3` | keep chronology human-readable while route selection is machine-readable | ✓ VERIFIED | Contract block is first selector; `v1.20` / `v1.19` route truth is explicitly marked historical at `.planning/MILESTONES.md:48`, `.planning/MILESTONES.md:371` |
| `.planning/baseline/VERIFICATION_MATRIX.md:391` | define the Phase 76 activation contract and runnable proof | ✓ VERIFIED | Baseline now anchors current mutable story, archive pointer, and default next command |
| `.planning/reviews/FILE_MATRIX.md:551` | register the guard families that own current-route drift detection | ✓ VERIFIED | `governance_current_truth`, follow-up route, closeout, release, and version guards are all described and retained |
| `tests/meta/governance_current_truth.py:24` | define one canonical route contract and assert doc equality | ✓ VERIFIED | `PLANNING_ROUTE_CONTRACT` matches all five planning docs via `assert_machine_readable_route_contracts()` |
| `tests/meta/governance_followup_route_current_milestones.py:193` | enforce current/latest archive truth and historical demotion | ✓ VERIFIED | Asserts shared contract, historical truth retention, and forbids old selector wording |
| `tests/meta/test_governance_milestone_archives.py:596` | prevent old selector prose from reappearing in archive docs | ✓ VERIFIED | Rejects `current governance state` / `live governance state` regressions and preserves historical labels |
| `tests/meta/test_phase75_governance_closeout_guards.py:52` | keep v1.20 closeout truth archive-only after Phase 76 activation | ✓ VERIFIED | Confirms historical truth remains archived context while active route/default next command stay current |
| `tests/meta/test_governance_closeout_guards.py:248` | align verification matrix and file-matrix with current-route contract | ✓ VERIFIED | Requires Phase 76 verification contract, archive pointer, next command, and file-matrix rows |
| `tests/meta/test_governance_release_contract.py:391` | keep release/docs truth aligned with current route and archive pointer | ✓ VERIFIED | Checks default next command in planning docs and latest archive pointer in verification/milestones |
| `tests/meta/test_version_sync.py:325` | freeze default next command and latest archived pointer drift | ✓ VERIFIED | Enforces `$gsd-execute-phase 76` and `.planning/reviews/V1_20_EVIDENCE_INDEX.md` |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `.planning/PROJECT.md:10` | `tests/meta/governance_current_truth.py:93` | shared `governance-route` YAML contract | ✓ VERIFIED | Five planning docs parse to one identical contract; `uv run python` check returned `all_equal True` |
| `.planning/ROADMAP.md:70` | `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init plan-phase 76` | roadmap phase metadata | ✓ VERIFIED | CLI returned `phase_found=true`, `phase_req_ids=GOV-57, ARC-20`, `phase_dir=.planning/phases/76-...` |
| `.planning/MILESTONES.md:3` | `tests/meta/governance_followup_route_current_milestones.py:207` | historical prose demoted behind contract block | ✓ VERIFIED | Tests require historical truths to remain present while rejecting old parser-visible selector phrases |
| `.planning/STATE.md:38` | `.planning/baseline/VERIFICATION_MATRIX.md:391` | active-route state fields projected into verification contract | ✓ VERIFIED | Both surfaces declare `Phase 76 execution-ready`, pointer `.planning/reviews/V1_20_EVIDENCE_INDEX.md`, and default next command |
| `.planning/baseline/VERIFICATION_MATRIX.md:394` | `tests/meta/test_governance_release_contract.py:391` | latest archived pointer + release/current-truth guards | ✓ VERIFIED | Release and version tests read the same pointer and fail on drift |
| `.planning/reviews/FILE_MATRIX.md:551` | `tests/meta/test_governance_closeout_guards.py:272` | file-matrix governance rows -> closeout guard assertions | ✓ VERIFIED | Closeout guard requires the registered guard families and residual stories to stay honest |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `tests/meta/governance_current_truth.py:24` | `PLANNING_ROUTE_CONTRACT` | parsed YAML blocks in `.planning/PROJECT.md:10`, `.planning/ROADMAP.md:28`, `.planning/REQUIREMENTS.md:32`, `.planning/STATE.md:38`, `.planning/MILESTONES.md:5` | Yes — `assert_machine_readable_route_contracts()` compares parsed doc payloads, not hardcoded smoke output | ✓ FLOWING |
| `tests/meta/governance_followup_route_current_milestones.py:193` | `contracts[...]` + historical truth literals | current docs plus historical archive sections in `.planning/ROADMAP.md:26`, `.planning/MILESTONES.md:48`, `.planning/REQUIREMENTS.md:70` | Yes — guards require both current contract equality and historical archive-only labels | ✓ FLOWING |
| `tests/meta/test_governance_closeout_guards.py:256` | verification/file-matrix/current-route assertions | `.planning/baseline/VERIFICATION_MATRIX.md:391`, `.planning/reviews/FILE_MATRIX.md:551` | Yes — tests consume actual baseline/review docs and fail on missing rows or drift | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| shared route contract is deterministic across five planning docs | `uv run python - <<'PY' ... load_planning_route_contracts() ... PY` | `all_equal True`; all docs resolved `v1.21` / `Phase 76 execution-ready` / `v1.20` / `$gsd-execute-phase 76` / `.planning/reviews/V1_20_EVIDENCE_INDEX.md` | ✓ PASS |
| bootstrap new-milestone smoke resolves active and latest archived baselines | `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init new-milestone` | `current_milestone="v1.21"`, `latest_completed_milestone="v1.20"` | ✓ PASS |
| bootstrap plan-phase smoke resolves Phase 76 contract | `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init plan-phase 76` | `phase_found=true`, `phase_req_ids="GOV-57, ARC-20"`, `phase_dir=.planning/phases/76-...` | ✓ PASS |
| focused governance gates stay green | `uv run pytest -q tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_phase75_governance_closeout_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` | `66 passed in 1.13s` | ✓ PASS |
| file-matrix governance inventory stays consistent | `uv run python scripts/check_file_matrix.py --check` | exit `0` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| `GOV-57` | `76-01`, `76-03` | current-route / next-step truth must be deterministic and shared across planning docs and tests | ✓ SATISFIED | `.planning/PROJECT.md:5`, `.planning/ROADMAP.md:54`, `.planning/REQUIREMENTS.md:58`, `.planning/STATE.md:64`, `.planning/MILESTONES.md:31`, `tests/meta/governance_current_truth.py:93`, `.planning/baseline/VERIFICATION_MATRIX.md:391` |
| `ARC-20` | `76-02`, `76-03` | historical milestone bodies remain audit/archive context and cannot reclaim current-route selector precedence | ✓ SATISFIED | `.planning/MILESTONES.md:3`, `.planning/MILESTONES.md:48`, `.planning/MILESTONES.md:371`, `.planning/ROADMAP.md:26`, `.planning/REQUIREMENTS.md:70`, `tests/meta/governance_followup_route_current_milestones.py:200`, `tests/meta/test_phase75_governance_closeout_guards.py:74` |

注：`.planning/REQUIREMENTS.md:19` 与 `.planning/REQUIREMENTS.md:20` 仍把 `GOV-57` / `ARC-20` 标记为 milestone-level `Planned`，这是 `v1.21` 尚未整体 closeout 的路由状态；不影响本次对 Phase 76 phase-level must_haves 的通过判定。

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| — | — | No TODO / FIXME / empty-stub / placeholder implementation blocking Phase 76 assets | ℹ️ Info | No blocker anti-patterns found in touched planning docs, baseline/review docs, or focused meta guards |

### Human Verification Required

None.

### Gaps Summary

No blocking gaps found.

- current route 已为 `v1.21 active route / Phase 76 execution-ready / latest archived baseline = v1.20`
- historical route truth 已降级为 archive-only context，仅作为 `v1.20` / `v1.19` 的历史 closeout or archive-transition 叙事保留
- default next command 已前推为 `$gsd-execute-phase 76`
- latest archived evidence pointer 继续固定为 `.planning/reviews/V1_20_EVIDENCE_INDEX.md`

---

_Verified: 2026-03-26T09:45:26Z_
_Verifier: Claude (gsd-verifier)_
