"""Shared archived-route and latest-archive truth for governance tests."""

from __future__ import annotations

CURRENT_MILESTONE = "v1.20"
CURRENT_MILESTONE_NAME = (
    "Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement"
)
CURRENT_MILESTONE_HEADER = f"## Latest Archived Milestone ({CURRENT_MILESTONE})"
CURRENT_MILESTONE_ROADMAP_HEADER = (
    f"## {CURRENT_MILESTONE}: {CURRENT_MILESTONE_NAME}"
)
CURRENT_MILESTONE_STATUS = "archived / evidence-ready (2026-03-25)"
CURRENT_MILESTONE_DEFAULT_NEXT = "$gsd-new-milestone"
CURRENT_MILESTONE_LABEL = f"{CURRENT_MILESTONE} {CURRENT_MILESTONE_NAME}"
CURRENT_MILESTONE_STATE_LABEL = "No active milestone route"
CURRENT_PHASE = "75"
CURRENT_PHASE_TITLE = (
    "Access-mode truth closure, evidence promotion formalization, and thin-adapter typing hardening"
)
CURRENT_PHASE_HEADING = f"### Phase {CURRENT_PHASE}: {CURRENT_PHASE_TITLE}"
CURRENT_PHASE_DIR = (
    "75-access-mode-truth-closure-evidence-promotion-formalization-and-thin-adapter-typing-hardening"
)
CURRENT_ROUTE = "no active milestone route / latest archived baseline = v1.20"
CURRENT_ROUTE_MODE = CURRENT_ROUTE
CURRENT_ROUTE_PROSE_FORBIDDEN = (
    "v1.20 active route / Phase 75 complete / latest archived baseline = v1.19",
)
CURRENT_RUNTIME_ROOT_TEST = "tests/core/coordinator/test_runtime_root.py"
LATEST_ARCHIVED_MILESTONE = CURRENT_MILESTONE
LATEST_ARCHIVED_MILESTONE_NAME = CURRENT_MILESTONE_NAME
LATEST_ARCHIVED_PROJECT_HEADER = CURRENT_MILESTONE_HEADER
LATEST_ARCHIVED_EVIDENCE_FILENAME = "V1_20_EVIDENCE_INDEX.md"
LATEST_ARCHIVED_EVIDENCE_PATH = ".planning/reviews/V1_20_EVIDENCE_INDEX.md"
LATEST_ARCHIVED_EVIDENCE_LABEL = "latest archived evidence index"
LEGACY_ARCHIVED_CLOSEOUT_POINTER_LABEL = "latest archived closeout pointer"
LATEST_ARCHIVED_AUDIT_FILENAME = "v1.20-MILESTONE-AUDIT.md"
LATEST_ARCHIVED_AUDIT_PATH = ".planning/v1.20-MILESTONE-AUDIT.md"
PREVIOUS_ARCHIVED_MILESTONE = "v1.19"
PREVIOUS_ARCHIVED_MILESTONE_NAME = (
    "Audit-Driven Final Hotspot Decomposition & Governance Truth Projection"
)
PREVIOUS_ARCHIVED_PROJECT_HEADER = (
    f"## Previous Archived Milestone ({PREVIOUS_ARCHIVED_MILESTONE})"
)
PREVIOUS_ARCHIVED_EVIDENCE_PATH = ".planning/reviews/V1_19_EVIDENCE_INDEX.md"
