"""Archived route-history literals kept out of current-truth helper home."""

from __future__ import annotations

CURRENT_ROUTE_PROSE_FORBIDDEN = (
    "active / roadmap drafted; phase 119 pending planning (2026-04-01)",
    "$gsd-plan-phase 119",
    "Phase 119 planning pending",
    "v1.33 active milestone route / starting from latest archived baseline = v1.32",
    "$gsd-complete-milestone v1.33",
    "v1.31 active milestone route / starting from latest archived baseline = v1.30",
    "v1.32 active milestone route / starting from latest archived baseline = v1.31",
    "no active milestone route / latest archived baseline = v1.20",
    "no active milestone route / latest archived baseline = v1.21",
    "no active milestone route / latest archived baseline = v1.22",
    "no active milestone route / latest archived baseline = v1.23",
    "no active milestone route / latest archived baseline = v1.24",
    "no active milestone route / latest archived baseline = v1.25",
    "no active milestone route / latest archived baseline = v1.26",
    "no active milestone route / latest archived baseline = v1.27",
    "no active milestone route / latest archived baseline = v1.28",
    "no active milestone route / latest archived baseline = v1.29",
    "v1.24 / Phase 89 complete",
)

HISTORICAL_CLOSEOUT_ROUTE_TRUTH = (
    "historical closeout route truth = "
    "`no active milestone route / latest archived baseline = v1.33`"
)
HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH = (
    "historical archive-transition route truth = "
    "`no active milestone route / latest archived baseline = v1.32`"
)

__all__ = [
    "CURRENT_ROUTE_PROSE_FORBIDDEN",
    "HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH",
    "HISTORICAL_CLOSEOUT_ROUTE_TRUTH",
]
