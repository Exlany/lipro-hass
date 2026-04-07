---
phase: 32
slug: truth-convergence-gate-honesty-and-quality-10-closeout
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-17
---

# Phase 32 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest meta/governance suites + architecture/file-matrix scripts + translation check + `ruff` + `mypy` |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run ruff check . && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` |
| **Phase gate command** | `uv run ruff check . && uv run mypy && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run python scripts/check_translations.py && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` |
| **Estimated runtime** | ~90-240 seconds |

## Wave Structure

- **Wave 1:** `32-01` + `32-02` —— active planning truth and repo-wide gate honesty
- **Wave 2:** `32-03` —— release identity / maintainer continuity / contributor template convergence
- **Wave 3:** `32-04` —— derived-map freshness / authority disclaimer / bilingual public-doc sync
- **Wave 4:** `32-05` —— hotspot slimming / mega-test topicization / typed-exception-residue follow-through

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 32-01-01 | 01 | 1 | GOV-24 | focused meta | `uv run pytest -q tests/meta/test_governance_closeout_guards.py -k "phase_32 or follow_through"` | planned |
| 32-01-02 | 01 | 1 | GOV-24 | focused meta | `uv run pytest -q tests/meta/test_governance_closeout_guards.py` | planned |
| 32-02-01 | 02 | 1 | QLT-05 | focused meta | `uv run pytest -q tests/meta/test_toolchain_truth.py -k "toolchain or runbook or contributing"` | planned |
| 32-02-02 | 02 | 1 | QLT-05 | focused static + meta | `uv run ruff check . && uv run pytest -q tests/meta/test_toolchain_truth.py` | planned |
| 32-03-01 | 03 | 2 | GOV-25 | focused meta | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_toolchain_truth.py -k "release or runbook or signing or code_scanning"` | planned |
| 32-03-02 | 03 | 2 | GOV-25 | focused meta | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py -k "support or security or template or owner"` | planned |
| 32-04-01 | 04 | 3 | GOV-26 | focused meta | `uv run pytest -q tests/meta/test_toolchain_truth.py -k "codebase or derived or testing"` | planned |
| 32-04-02 | 04 | 3 | GOV-26 | focused script + meta | `uv run python scripts/check_translations.py && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py -k "docs or public or architecture"` | planned |
| 32-05-01 | 05 | 4 | HOT-07, TST-04 | focused tests | `uv run pytest -q tests/core/api/test_api.py tests/core/test_init.py tests/meta/test_governance_guards.py -k "api or init or governance"` | planned |
| 32-05-02 | 05 | 4 | TYP-08, ERR-06, RES-06 | focused static + meta | `uv run ruff check . && uv run pytest -q tests/meta/test_governance_guards.py && uv run mypy custom_components/lipro/core/api custom_components/lipro/core/protocol custom_components/lipro/core/coordinator` | planned |

## Manual-Only Verifications

- 确认 `v1.3-HANDOFF.md` 与 `v1.3-MILESTONE-AUDIT.md` 被显式保留为历史 closeout baseline，而不是被静默抹除或继续误作 active truth。
- 确认 release identity / code scanning / signing / attestation 的概念边界在 workflow、runbook、README、README_zh、CONTRIBUTING、SUPPORT、SECURITY、PR template 中一致。
- 确认 `.planning/codebase/*.md` 仍是 derived collaboration maps，而不是偷偷回升为 governance authority。
- 确认 hotspot slimming 继续沿正式 seams 推进，而不是引入第二 orchestration root 或新的过度抽象层。
- 确认 protocol-constrained crypto wording 继续诚实，不把 `MD5` 登录路径伪装成当前仓库可独立消灭的密码学债。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `truth -> gate -> release/docs -> derived maps -> hotspots`.
- [x] `uv run ruff check .` remains a mandatory phase gate.
- [x] Repo-wide `mypy` honesty is treated as an explicit exit criterion, not an implied green story.
- [x] `nyquist_compliant: true` set in frontmatter.
- [x] Execution evidence recorded in `32-VERIFICATION.md`.
