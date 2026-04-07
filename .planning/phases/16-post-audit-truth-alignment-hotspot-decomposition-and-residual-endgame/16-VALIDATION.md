---
phase: 16
slug: post-audit-truth-alignment-hotspot-decomposition-and-residual-endgame
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-15
---

# Phase 16 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` + `ruff` + `mypy` + repo governance scripts |
| **Config file** | `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml` |
| **Quick run command** | `uv run ruff check . && uv run mypy && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` |
| **Debt audit command set** | `rg -n 'except Exception|type: ignore' custom_components/lipro && rg -n '@pytest\\.mark\\.(github|integration|slow)' tests || true && rg -n '\\bAny\\b' custom_components/lipro/control custom_components/lipro/core/api custom_components/lipro/core/protocol custom_components/lipro/core/coordinator custom_components/lipro/entities custom_components/lipro/services` |
| **Full suite command** | `uv run pytest tests/ -v --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95 --cov-report=json --cov-report=xml --cov-report=term-missing` |
| **Estimated runtime** | ~120 seconds |

---

## Sampling Rate

- **After every plan-local commit:** Run the targeted automated command listed for the active plan below.
- **After every wave:** Run the quick run command plus the debt audit command set.
- **Before `$gsd-verify-work`:** Run the full suite command plus `uv run pytest tests/snapshots/ -v`.
- **Before phase closeout sign-off:** Reconcile debt audit output with `.planning/reviews/RESIDUAL_LEDGER.md` / `.planning/reviews/KILL_LIST.md`; no high-risk unowned leftovers are allowed.
- **Max feedback latency:** 120 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 16-01-00 | 16-01 | 1 | GOV-14 | governance/meta/script guards | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check` | ✅ | ✅ green |
| 16-02-00 | 16-02 | 1 | QLT-02 / DOC-02 | config/tooling/docs guard | `uv run ruff check . && uv run mypy && uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py tests/meta/test_governance_guards.py && shellcheck scripts/develop` | ✅ | ✅ green |
| 16-03-00 | 16-03 | 2 | CTRL-06 / ERR-01 / TYP-04 | focused control/service regression + typing | `uv run pytest -q tests/core/test_control_plane.py tests/core/test_init.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/services/test_execution.py tests/services/test_services_registry.py tests/services/test_service_resilience.py tests/services/test_services_share.py tests/services/test_services_diagnostics.py tests/services/test_device_lookup.py tests/services/test_maintenance.py tests/flows/test_config_flow.py && uv run mypy` | ✅ | ✅ green |
| 16-04-00 | 16-04 | 2 | HOT-04 / TYP-04 / RES-02 / ERR-01 | protocol/runtime + typing | `uv run pytest -q tests/core/api tests/core/mqtt tests/core/coordinator tests/core/coordinator/runtime/test_mqtt_runtime.py tests/integration/test_mqtt_coordinator_integration.py tests/snapshots/test_api_snapshots.py && uv run mypy && uv run python scripts/check_architecture_policy.py --check` | ✅ | ✅ green |
| 16-05-00 | 16-05 | 3 | DOM-03 / OTA-01 | domain/entity/OTA focused regression | `uv run pytest -q tests/core/device tests/core/ota tests/entities tests/platforms/test_entity_behavior.py tests/platforms/test_update.py tests/platforms/test_firmware_update_entity_edges.py tests/platforms/test_entity_base.py` | ✅ | ✅ green |
| 16-06-00 | 16-06 | 3 | TST-01 / DOC-02 / GOV-14 | test-layer + DX docs + closeout re-audit | `uv run pytest -q tests/platforms tests/flows/test_config_flow.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py && uv run python scripts/check_file_matrix.py --check && uv run python scripts/check_architecture_policy.py --check` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] Existing infrastructure already covers governance/meta checks.
- [x] Existing focused suites already cover control/service, protocol/runtime, device/OTA, and platform paths.
- [x] No new test framework or watch-mode tooling is required.
- [x] `uv run ruff check .`, `uv run mypy`, `uv run python scripts/check_architecture_policy.py --check`, and `uv run python scripts/check_file_matrix.py --check` are part of the wave-end gate.
- [x] Debt audit can be executed with existing `rg` + governance assets; no new framework bootstrap is required before planning.

---

## Closeout Debt Gate

在 `16-06` 与 phase closeout 之前，必须额外完成一次 second-pass debt audit：

1. 复核 `except Exception`、`type: ignore`、dead markers、high-`Any` hotspots、dynamic entry points 是否仍落在 active formal paths 上。
2. 把仍存在的 residual / compat / fallback 项与 `.planning/reviews/RESIDUAL_LEDGER.md`、`.planning/reviews/KILL_LIST.md` 对齐。
3. 若有保留项，必须证明其为低风险、局部、owner+delete-gate 清晰且不再误导新维护者；否则视为 closeout blocked。

---

## Stop-the-Line Rules

- `dependency/public-surface/governance/file-matrix` 失败：立即阻断当前 wave，不得带病推进。
- `⚠️ flaky` 测试：最多重试 **2** 次；若仍不稳定，视为当前 wave blocked。
- wave-end gate 连续失败：回退到上一个 wave-end green 点，再决定重试策略；不得在失败状态上继续叠加改动。
- debt audit 发现未登记高风险热点：视为 closeout blocked，必须先补计划归属或显式降格说明。

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Active governance docs tell one coherent Phase 16 story | GOV-14 | Human readability matters beyond regex/AST pass | Read `AGENTS.md`, `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, `.planning/reviews/RESIDUAL_LEDGER.md`, and `.planning/reviews/KILL_LIST.md` together and confirm there is no contradictory residual or phase-status wording |
| Toolchain truth is understandable to contributors | QLT-02 / DOC-02 | Users need one clear mental model, not just green CI | Review `pyproject.toml`, `.pre-commit-config.yaml`, `.devcontainer.json`, `CONTRIBUTING.md`, and any new runbook/troubleshooting docs together |
| DX guidance matches real local maintenance flow | DOC-02 | Placement and clarity are user-facing quality, not just structural data | Walk through `scripts/develop`, troubleshooting docs, and maintainer runbook from a fresh-reader perspective |
| No high-risk hotspot remains outside the plan inventory | HOT-04 / RES-02 | Repo-wide closeout needs human arbitration, not only pattern counts | Compare the second-pass hotspot inventory in `16-RESEARCH.md` with the final touched files and residual ledger; every remaining hotspot must be either cleaned or explicitly justified |
| No silent defer survives phase closeout | GOV-14 / ERR-01 / TYP-04 | A green test suite alone does not prove architectural honesty | Review any remaining broad-catch / `type: ignore` / residual exceptions and confirm each has owner, delete gate, and low-risk rationale |

---

## Validation Sign-Off

- [x] All requirement groups have an automated verify path or explicit manual gate.
- [x] Sampling continuity exists across all three waves.
- [x] Wave 0 uses existing infrastructure; no missing framework setup remains.
- [x] No watch-mode flags are present.
- [x] `nyquist_compliant: true` is set in frontmatter.
- [x] Phase closeout explicitly includes a debt audit / no-silent-defer gate.
- [x] Plan-local execution evidence has been collected and synced to summaries / governance artifacts.

**Approval:** passed

---

## Final Closeout Evidence

- Final rerun on `2026-03-15` completed with one coherent gate: `uv run ruff check .`, `uv run mypy`, `uv run python scripts/check_architecture_policy.py --check`, `uv run python scripts/check_file_matrix.py --check`, `uv run pytest -q`.
- Result summary: `ruff` ✅, `mypy` ✅ (`Success: no issues found in 440 source files`), governance scripts ✅, full `pytest` ✅ (`2194 passed in 38.59s`, no warnings).
- Final second-pass repo audit: `Any=711`, `except Exception=36`, `type: ignore=12`, dead pytest markers (`github|integration|slow`) `=0`.
- Remaining residual inventory stays identical to `.planning/reviews/RESIDUAL_LEDGER.md` / `.planning/reviews/KILL_LIST.md`; no new unowned hotspot or silent defer surfaced during closeout.
- `SnapshotBuilder` mesh-group enrichment now tolerates degraded `AsyncMock` contract doubles without unawaited-coroutine warnings, so the final full-suite rerun is warning-free.
