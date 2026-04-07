# v1.1 Evidence Index

**Purpose:** 为 `v1.1 Protocol Fidelity & Operability` 提供机器友好的 closeout 入口，集中列出 boundary / enforcement / telemetry / replay / governance 的正式证据指针。
**Status:** Pull-only closeout index
**Updated:** 2026-03-13

## Pull Contract

- 本文件只索引正式真源与 phase evidence；它不是新的 authority source。
- `Phase 8` 与后续 AI / tooling 只能从这里继续 pull 已登记证据，不得重新扫描仓库拼装第二套事实。
- 真实时间戳允许出现；凭证等价物不得出现；伪匿名引用必须继续继承 `07.3` exporter 裁决。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Residual / delete gate |
|--------|----------------|-------------|---------------------|-------------|------------------------|
| Boundary decoder families | `.planning/phases/07.1-protocol-boundary-schema-decoder/07.1-01-BOUNDARY-INVENTORY.md`, `tests/fixtures/api_contracts/`, `tests/fixtures/protocol_boundary/` | `custom_components/lipro/core/protocol/boundary/`, `.planning/phases/07.1-protocol-boundary-schema-decoder/` | `uv run pytest tests/core/api/test_protocol_contract_matrix.py tests/core/mqtt/test_message_processor.py tests/core/mqtt/test_mqtt_payload.py tests/meta/test_governance_guards.py tests/meta/test_external_boundary_authority.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py -q` | `07.1` | `RESIDUAL_LEDGER.md` → `Protocol-boundary family coverage` |
| Architecture enforcement | `.planning/baseline/ARCHITECTURE_POLICY.md`, `.planning/baseline/PUBLIC_SURFACES.md`, `.planning/baseline/AUTHORITY_MATRIX.md` | `scripts/check_architecture_policy.py`, `tests/helpers/architecture_policy.py`, `.planning/phases/07.2-architecture-enforcement/` | `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q -x tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py` | `07.2` | no new file-level delete gate; future rule changes must first update baseline docs |
| Runtime telemetry exporter | `custom_components/lipro/core/telemetry/`, `custom_components/lipro/control/telemetry_surface.py`, `.planning/phases/07.3-runtime-telemetry-exporter/07.3-VALIDATION.md` | `.planning/phases/07.3-runtime-telemetry-exporter/`, `tests/core/telemetry/`, `tests/integration/test_telemetry_exporter_integration.py` | `uv run pytest -q -x tests/core/telemetry/test_models.py tests/core/telemetry/test_exporter.py tests/core/telemetry/test_sinks.py tests/core/coordinator/runtime/test_runtime_telemetry_methods.py tests/core/coordinator/services/test_telemetry_service.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/services/test_services_diagnostics.py tests/integration/test_telemetry_exporter_integration.py` | `07.3` | `KILL_LIST.md` 既有 delete gates 不变；后续 consumers 只能 pull exporter truth |
| Protocol replay harness | `tests/fixtures/protocol_replay/`, `tests/fixtures/api_contracts/`, `tests/fixtures/protocol_boundary/`, `07.3` exporter truth | `.planning/phases/07.4-protocol-replay-simulator-harness/`, `tests/harness/protocol/`, `tests/integration/test_protocol_replay_harness.py` | `uv run pytest -q -x tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/core/api/test_protocol_contract_matrix.py tests/integration/test_protocol_replay_harness.py tests/meta/test_protocol_replay_assets.py tests/meta/test_external_boundary_authority.py tests/meta/test_external_boundary_fixtures.py` | `07.4` | `RESIDUAL_LEDGER.md` → `Replay scenario coverage`（v1.1 仅保留 representative corpus） |
| Governance closeout | `.planning/baseline/AUTHORITY_MATRIX.md`, `.planning/baseline/PUBLIC_SURFACES.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/reviews/RESIDUAL_LEDGER.md`, `.planning/reviews/KILL_LIST.md` | `.planning/reviews/V1_1_EVIDENCE_INDEX.md`, `.planning/phases/07.5-integration-governance-verification-closeout/` | `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q -x tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_protocol_replay_assets.py` | `07.5` | no new file-level kill target; `Phase 8` 只允许 pull 此索引与上游真源 |
| AI debug evidence pack | `custom_components/lipro/core/telemetry/`, `tests/harness/protocol/`, `.planning/phases/07.1-protocol-boundary-schema-decoder/07.1-01-BOUNDARY-INVENTORY.md`, `.planning/reviews/V1_1_EVIDENCE_INDEX.md`, `.planning/baseline/AUTHORITY_MATRIX.md`, `.planning/baseline/PUBLIC_SURFACES.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/reviews/RESIDUAL_LEDGER.md` | `tests/harness/evidence_pack/`, `scripts/export_ai_debug_evidence_pack.py` | `uv run ruff check scripts/export_ai_debug_evidence_pack.py tests/harness/evidence_pack tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py && uv run pytest -q -x tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py` | `08` | `RESIDUAL_LEDGER.md` → `Phase 08 Residual Delta`（本轮无新增 residual family / kill target） |

## Phase Evidence Ledger

| Phase | Locked truth | Summary / validation / UAT | Pullable outputs |
|------|--------------|----------------------------|------------------|
| `07.1` | boundary authority / decoder family / replay-ready fixtures | `07.1-01-SUMMARY.md`, `07.1-02-SUMMARY.md`, `07.1-03-SUMMARY.md` | boundary inventory, decoder family, authority-ready fixtures |
| `07.2` | architecture policy / meta guards / CI fail-fast | `07.2-01-SUMMARY.md`, `07.2-02-SUMMARY.md` | architecture policy rules, guard helpers, governance checks |
| `07.3` | observer-only telemetry truth / redaction / pseudo-id compatibility | `07.3-01-SUMMARY.md`, `07.3-02-SUMMARY.md`, `07.3-VALIDATION.md`, `07.3-UAT.md` | exporter contracts/views, diagnostics/system-health consumer convergence |
| `07.4` | assurance-only deterministic replay / run summary | `07.4-01-SUMMARY.md`, `07.4-02-SUMMARY.md`, `07.4-03-SUMMARY.md`, `07.4-VALIDATION.md`, `07.4-UAT.md` | replay manifests, deterministic driver, replay report, black-box replay evidence |
| `07.5` | governance closeout / evidence index / residual arbitration | `07.5-01-SUMMARY.md`, `07.5-02-SUMMARY.md`, `07.5-SUMMARY.md`, `07.5-VALIDATION.md`, `07.5-VERIFICATION.md` | v1.1 evidence index, next-step contract for `08`, updated planning truth |
| `08` | AI debug evidence pack / pull-only AI/tooling export | `08-01-SUMMARY.md`, `08-02-SUMMARY.md`, `08-VALIDATION.md`, `08-VERIFICATION.md` | `ai_debug_evidence_pack.json`, `ai_debug_evidence_pack.index.md`, authority/redaction guards |

## Phase 8 Pull Boundary

- Allowed inputs: `V1_1_EVIDENCE_INDEX.md`, baseline docs, `07.3` exporter evidence, `07.4` replay evidence, active residual / delete gates。
- Forbidden inputs: ad-hoc repo scan、runtime internals、临时日志拼接、未登记 fixture truth。
- 如果 `08` 需要新增 replay family 或 evidence field，必须先回写 baseline/review docs，再扩 exporter / pack schema。
