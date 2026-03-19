# v1.4 Evidence Index

**Purpose:** 为 `v1.4 Sustainment, Trust Gates & Final Hotspot Burn-down` 提供机器友好的 shipped / archived closeout 入口，集中列出 continuity、release trust、protocol/runtime hotspot slimming、quality-signal convergence 与 milestone archive promotion 的正式证据指针。
**Status:** Pull-only shipped archive index
**Updated:** 2026-03-19

## Pull Contract

- 本文件只索引正式真源、phase verification/summaries、milestone audit 与 archive snapshots；它不是新的 authority source。
- maintainer release flow、下一里程碑启动与后续审计只能从这里继续 pull 已登记证据，不得重新扫描仓库拼装第二套事实。
- `.planning/v1.4-MILESTONE-AUDIT.md` 是 `v1.4` 的 verdict home；`.planning/milestones/v1.4-ROADMAP.md` 与 `.planning/milestones/v1.4-REQUIREMENTS.md` 只保留历史快照，不反向定义活跃治理真相。
- `39-SUMMARY.md` 与 `39-VERIFICATION.md` 是 promoted closeout evidence；`39-VALIDATION.md` 维持 execution-trace 身份，不额外升级为长期治理 allowlist。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Continuity / release trust | `README*.md`, `SUPPORT.md`, `SECURITY.md`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`, `.github/workflows/{release,codeql}.yml`, `34-VERIFICATION.md` | `.planning/phases/34-continuity-and-hard-release-gates/`, `docs/`, `.github/workflows/` | `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py` | `34` | custody / freeze / restoration contract，`SHA256SUMS` / `SBOM` / `provenance` / `signing` / `code scanning` 形成单一 blocking story |
| Protocol hotspot slimming | `custom_components/lipro/core/api/*`, `custom_components/lipro/core/protocol/*`, `35-VERIFICATION.md` | `.planning/phases/35-protocol-hotspot-final-slimming/` | `uv run pytest -q tests/core/api/test_api_command_surface.py tests/core/api/test_protocol_contract_matrix.py tests/meta/test_public_surface_guards.py` | `35` | `34-01~34-03-SUMMARY.md` / `35-01~35-03-SUMMARY.md` 共同锁定 slimmer protocol truth |
| Runtime root / exception hardening | `custom_components/lipro/core/coordinator/*`, `36-VERIFICATION.md` | `.planning/phases/36-runtime-root-and-exception-burn-down/` | `uv run pytest -q tests/core/test_coordinator.py tests/integration/test_mqtt_coordinator_integration.py tests/meta/test_public_surface_guards.py` | `36` | `CoordinatorPollingService` 收口 orchestration，broad catches 继续 burn-down 到 typed arbitration |
| Test topology / derived-truth convergence | `.planning/codebase/*`, `CONTRIBUTING.md`, `37-VERIFICATION.md` | `.planning/phases/37-test-topology-and-derived-truth-convergence/`, `.planning/codebase/` | `uv run pytest -q tests/core/test_init*.py tests/meta/test_governance_phase_history*.py && uv run python scripts/check_file_matrix.py --check` | `37` | topicized suites 与 derived maps 维持同一 topology story |
| External-boundary honesty / quality-signal hardening | `custom_components/lipro/firmware_support_manifest.json`, `.planning/REQUIREMENTS.md`, `38-VERIFICATION.md` | `.planning/phases/38-external-boundary-residual-retirement-and-quality-signal-hardening/` | `uv run pytest -q tests/meta/test_external_boundary_authority.py tests/meta/test_external_boundary_fixtures.py tests/meta/test_firmware_support_manifest_repo_asset.py tests/core/ota/test_firmware_manifest.py` | `38` | bundled local trust-root + remote advisory payload；`firmware manifest metadata` 仍是显式 defer |
| Governance convergence / archive promotion | `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`, `.planning/v1.4-MILESTONE-AUDIT.md`, `.planning/milestones/v1.4-*.md`, `39-VERIFICATION.md` | `.planning/`, `.planning/phases/39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition/` | `uv run ruff check . && uv run mypy && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance*.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` | `39` | shipped / archived promotion completed; `V1_4_EVIDENCE_INDEX.md` is the latest pull-only closeout pointer |

## Release / Closeout Pull Boundary

- Maintainer release issues must start from `docs/MAINTAINER_RELEASE_RUNBOOK.md` and this index, not from ad-hoc file hunting.
- `archive-ready / shipped` 判断以 `.planning/v1.4-MILESTONE-AUDIT.md` 为 verdict home；本索引只负责把证据指针收在一起。
- `v1.4` archive snapshots 是历史记录，不取代 `.planning/ROADMAP.md` / `.planning/REQUIREMENTS.md` / `.planning/STATE.md` 的活跃治理角色。
