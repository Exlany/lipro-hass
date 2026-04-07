---
phase: 77-governance-guard-topicization-bootstrap-smoke-coverage-and-literal-drift-reduction
plan: "01"
subsystem: governance-bootstrap-smoke
tags: [governance, bootstrap, smoke, tests, topicization]
requirements-completed: [TST-23]
completed: 2026-03-26
---

# Phase 77 Plan 01 Summary

**bootstrap route-activation smoke 已从 `closeout / release / version` 巨型套件中剥离出来，并建立了专属的 focused smoke home。**

## Accomplishments
- 新增 `tests/meta/test_governance_bootstrap_smoke.py`，集中守卫 active-route、default-next、latest archived pointer 与 public-doc-hidden-bootstrap story。
- `tests/meta/governance_contract_helpers.py` 扩展为正式 route/doc helper home，承接 public-doc-hidden-bootstrap 与 latest-archive route truth 断言。
- `tests/meta/test_governance_release_contract.py` 与 `tests/meta/test_version_sync.py` 已去掉 focused bootstrap smoke 的主职责，回到各自 release/docs 与 version/metadata concern。
- `tests/meta/test_governance_closeout_guards.py` 不再承载跨 concern 的 bootstrap pointer smoke，failure localization 明显收敛。

## Proof
- `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_release_contract.py` → `23 passed`
