---
phase: 74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout
plan: "03"
subsystem: docs-governance
tags: [docs, public-surface, version-truth, retired-stubs, cleanup]
requires:
  - phase: 74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout
    provides: topicized suite and cleanup baseline
provides:
  - honest public docs fast path with no route leakage
  - consistent version/open-source truth across public docs and registry
  - retired script stubs that fail fast with explicit guidance
affects: [phase-74-04, docs-boundary, governance-registry]
tech-stack:
  added: []
  patterns: [public-fast-path hygiene, fail-fast retired stub]
key-files:
  created:
    - .planning/phases/74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout/74-03-SUMMARY.md
    - tests/meta/test_phase74_cleanup_closeout_guards.py
  modified:
    - docs/README.md
    - README.md
    - README_zh.md
    - CONTRIBUTING.md
    - SUPPORT.md
    - docs/TROUBLESHOOTING.md
    - docs/MAINTAINER_RELEASE_RUNBOOK.md
    - .gitignore
    - .planning/baseline/GOVERNANCE_REGISTRY.json
    - scripts/agent_worker.py
    - scripts/orchestrator.py
    - tests/meta/test_version_sync.py
    - tests/meta/toolchain_truth_docs_fast_path.py
    - tests/meta/test_governance_release_contract.py
key-decisions:
  - "Keep `docs/README.md` public-only; maintainer route/pointer truth stays in planning and runbook assets."
  - "Retired stubs must fail fast honestly, not pretend to remain supported paths."
requirements-completed: [GOV-56, QLT-30]
completed: 2026-03-25
---

# Phase 74 Plan 03 Summary

**公开文档、版本真相、phase tracking 与 retired stubs 已被校正到诚实的开源契约。**

## Accomplishments
- `docs/README.md` 收回 public docs map 身份，不再暴露 current route、archive pointer 或 maintainer next-command 内情。
- `README*`、`CONTRIBUTING.md`、`SUPPORT.md`、runbook 与 governance registry 现讲同一条 stable-support / docs first-hop / archive-boundary 故事。
- `scripts/agent_worker.py` 与 `scripts/orchestrator.py` 保持 unsupported fail-fast retired stub 语义，不再误导为可继续使用的正式入口。

## Proof
- `uv run pytest -q tests/meta/test_version_sync.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_governance_release_contract.py tests/meta/test_phase74_cleanup_closeout_guards.py` → `47 passed`.
