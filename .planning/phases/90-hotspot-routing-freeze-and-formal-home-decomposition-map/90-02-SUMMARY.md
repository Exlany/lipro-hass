---
phase: 90-hotspot-routing-freeze-and-formal-home-decomposition-map
plan: "02"
status: completed
completed: 2026-03-28
---

# Summary 90-02

**Baseline docs, review ledgers, and derived collaboration maps now tell one ownership story: the five hotspots stay formal homes, `client.py` is only a stable import shell, and delete-gate wording is explicit instead of folkloric.**

## Outcome

- `.planning/baseline/{PUBLIC_SURFACES,DEPENDENCY_MATRIX,VERIFICATION_MATRIX}.md` now freeze the Phase 90 hotspot map and register the required runnable proof.
- `.planning/reviews/{FILE_MATRIX,RESIDUAL_LEDGER,KILL_LIST}.md` now explicitly reject file-level delete folklore for the five hotspots and protect the four outward shells from orchestration regrowth.
- `.planning/codebase/{ARCHITECTURE,STRUCTURE,CONCERNS,CONVENTIONS,TESTING}.md` and `docs/developer_architecture.md` now mirror the frozen map as derived navigation, not as a second authority chain.

## Verification

- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py`

## Task Commits

- None — per user instruction, this workspace keeps the phase uncommitted.

## Deviations from Plan

- `PUBLIC_SURFACES.md` and `DEPENDENCY_MATRIX.md` were promoted into the plan's touched set because Phase 90's frozen map needs both public-surface and dependency language to stay machine-checkable.

## Next Readiness

- `90-03` can now add focused guards against route drift, delete-target drift, and shell-regrowth drift using the finalized wording.
