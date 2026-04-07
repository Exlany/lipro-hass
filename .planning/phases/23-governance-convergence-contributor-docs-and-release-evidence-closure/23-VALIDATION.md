---
phase: 23
slug: governance-convergence-contributor-docs-and-release-evidence-closure
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-16
---

# Phase 23 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + ruff + mypy |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q` |
| **Phase gate command** | `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` |
| **Estimated runtime** | ~180-420 seconds |

## Wave Structure

- **Wave 1-3:** `23-01..03` —— historical completed governance/doc/release-evidence closure assets
- **Wave 4:** `23-04` —— user-visible contract fixes + low-risk boundary hazard removal
- **Wave 5:** `23-05`, `23-06` —— mainline convergence + hotspot decomposition / coupling demotion
- **Wave 6:** `23-07` —— tests/scripts/governance derived-asset repair + audit checklist
- **Wave 7:** `23-08` —— docs/security/release/open-source posture closure

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 23-04-01 | 04 | 4 | GOV-16/GOV-17 | focused | `uv run pytest tests/platforms/test_fan.py -q` | ⬜ pending |
| 23-04-02 | 04 | 4 | GOV-16 | focused | `uv run pytest tests/core/test_system_health.py tests/core/test_diagnostics.py -q` | ⬜ pending |
| 23-04-03 | 04 | 4 | GOV-17 | focused | `uv run pytest tests/meta/test_governance_guards.py -q` | ⬜ pending |
| 23-05-01 | 05 | 5 | GOV-16 | focused | `uv run pytest tests/test_coordinator_public.py tests/services/test_execution.py -q` | ⬜ pending |
| 23-05-02 | 05 | 5 | GOV-16 | focused | `uv run pytest tests/core/test_device_refresh.py tests/meta/test_dependency_guards.py -q` | ⬜ pending |
| 23-05-03 | 05 | 5 | GOV-16 | focused | `uv run pytest tests/core/test_coordinator.py -q` | ⬜ pending |
| 23-06-01 | 06 | 5 | GOV-16 | focused | `uv run pytest tests/services/test_services_registry.py tests/services/test_services_diagnostics.py -q` | ⬜ pending |
| 23-06-02 | 06 | 5 | GOV-16 | focused | `uv run pytest tests/core/test_developer_report.py -q` | ⬜ pending |
| 23-07-01 | 07 | 6 | GOV-16/GOV-17 | focused | `uv run pytest tests/meta/test_toolchain_truth.py -q` | ⬜ pending |
| 23-07-02 | 07 | 6 | GOV-16/GOV-17 | focused | `uv run pytest tests/meta/test_evidence_pack_authority.py tests/meta/test_public_surface_guards.py -q` | ⬜ pending |
| 23-07-03 | 07 | 6 | GOV-16/GOV-17 | focused | `uv run pytest tests/meta/test_governance_guards.py -q` | ⬜ pending |
| 23-08-01 | 08 | 7 | GOV-16/GOV-17 | focused | `uv run pytest tests/meta/test_governance_guards.py tests/meta/test_version_sync.py -q` | ⬜ pending |
| 23-08-02 | 08 | 7 | GOV-17 | focused | `uv run pytest tests/meta/test_evidence_pack_authority.py -q` | ⬜ pending |

## Wave Commands

### Wave 4 Gate

- `uv run pytest tests/platforms/test_fan.py tests/core/test_system_health.py tests/core/test_diagnostics.py -q`
- `uv run pytest tests/meta/test_governance_guards.py -q`
- `uv run ruff check .`

### Wave 5 Gate

- `uv run pytest tests/test_coordinator_public.py tests/services/test_execution.py tests/core/test_device_refresh.py tests/core/test_coordinator.py -q`
- `uv run pytest tests/services/test_services_registry.py tests/services/test_services_diagnostics.py tests/core/test_developer_report.py -q`
- `uv run pytest tests/meta/test_dependency_guards.py -q`
- `uv run ruff check .`

### Wave 6 Gate

- `uv run pytest tests/meta/test_toolchain_truth.py tests/meta/test_evidence_pack_authority.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py -q`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run ruff check .`

### Wave 7 Gate

- `uv run pytest tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_evidence_pack_authority.py -q`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check .`
- `uv run mypy`

## Manual-Only Verifications

- 确认 `23-01..03` 保持历史完成记录身份，未被重写。
- 确认新增计划没有把默认安装入口从 `latest` 反转成 pinned tag。
- 确认 `23-AUDIT-CHECKLIST.md` 覆盖了本轮审查的所有问题，没有 silent omission。
- 确认 production refactor、tests/governance repair、docs/release posture 之间的执行顺序符合 `contract -> mainline -> derived assets -> public narrative`。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Historical completed plans are preserved and additive plans start from `23-04`.
- [x] `nyquist_compliant: true` set in frontmatter.
- [ ] Execution evidence pending.

**Approval:** ready for execution after plan verification
