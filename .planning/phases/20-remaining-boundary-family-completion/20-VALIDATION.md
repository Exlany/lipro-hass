---
phase: 20
slug: remaining-boundary-family-completion
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-16
---

# Phase 20 — Validation Strategy

> Per-phase validation contract for remaining boundary family completion.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + ruff + mypy |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_schedule_codec.py tests/core/api/test_schedule_endpoint.py tests/core/api/test_api_schedule_endpoints.py tests/core/api/test_api_schedule_candidate_queries.py tests/core/mqtt/test_topic_builder.py tests/core/mqtt/test_mqtt_payload.py tests/core/mqtt/test_message_processor.py tests/core/mqtt/test_transport_refactored.py` |
| **Wave gate commands** | `uv run python scripts/check_architecture_policy.py --check` + `uv run python scripts/check_file_matrix.py --check` + `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_protocol_replay_assets.py tests/meta/test_version_sync.py tests/meta/test_evidence_pack_authority.py` |
| **Full suite command** | `uv run pytest -q` |
| **Estimated runtime** | ~180-240 seconds |

---

## Sampling Rate

- **After every task commit:** run the task-level automated command listed below.
- **After wave 1:** re-run REST contract + schedule-focused tests.
- **After wave 2:** re-run MQTT topic/message-envelope + replay-focused tests.
- **After wave 3 / before verification:** run wave gate commands, `uv run ruff check .`, `uv run mypy`, and the full suite command; only then may phase-complete truth be written back to `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`.
- **Max feedback latency:** 240 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 20-01-01 | 20-01 | 1 | SIM-03 | REST list-envelope static gate | `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_protocol_replay_rest.py -k "device_list or list"` | ✅ | ⬜ pending |
| 20-01-02 | 20-01 | 1 | SIM-03 | schedule-json boundary regression | `uv run pytest -q tests/core/api/test_schedule_codec.py tests/core/api/test_schedule_endpoint.py tests/core/api/test_api_schedule_endpoints.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_candidate_queries.py tests/services/test_services_schedule.py tests/core/api/test_api.py -k "schedule"` | ✅ | ⬜ pending |
| 20-01-03 | 20-01 | 1 | SIM-03 | REST replay + asset visibility | `uv run pytest -q tests/core/api/test_protocol_replay_rest.py tests/integration/test_protocol_replay_harness.py tests/meta/test_protocol_replay_assets.py` | ✅ | ⬜ pending |
| 20-02-01 | 20-02 | 2 | SIM-03 | MQTT topic boundary regression | `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/mqtt/test_mqtt.py tests/core/mqtt/test_topic_builder.py` | ✅ | ⬜ pending |
| 20-02-02 | 20-02 | 2 | SIM-03 | MQTT message-envelope regression | `uv run pytest -q tests/core/mqtt/test_mqtt_payload.py tests/core/mqtt/test_message_processor.py tests/core/mqtt/test_transport_refactored.py` | ✅ | ⬜ pending |
| 20-02-03 | 20-02 | 2 | SIM-03 | MQTT replay harness visibility + registry descriptor | `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/meta/test_protocol_replay_assets.py` | ✅ | ⬜ pending |
| 20-03-01 | 20-03 | 3 | SIM-05 | fixture/inventory sync gate | `uv run pytest -q tests/meta/test_protocol_replay_assets.py tests/integration/test_protocol_replay_harness.py` | ✅ | ⬜ pending |
| 20-03-02 | 20-03 | 3 | SIM-05 | baseline/review/governance sync | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` | ✅ | ⬜ pending |
| 20-03-03 | 20-03 | 3 | SIM-03 / SIM-05 | full phase gate | `uv run python scripts/check_architecture_policy.py --check && uv run pytest -q tests/integration/test_protocol_replay_harness.py tests/meta/test_protocol_replay_assets.py tests/meta/test_evidence_pack_authority.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py && uv run ruff check . && uv run mypy && uv run pytest -q` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] Existing protocol boundary registry, replay harness, fixture matrix, meta guard and governance infrastructure already cover Phase 20.
- [x] No dedicated Wave 0 bootstrap is required; Phase 20 can execute directly against the current protocol-boundary / replay stack.
- [x] Authority truth continues to live in `tests/fixtures/api_contracts/`, `tests/fixtures/protocol_boundary/`, `tests/fixtures/protocol_replay/` and `.planning/baseline/AUTHORITY_MATRIX.md`.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `rest.list-envelope.v1` / `rest.schedule-json.v1` are described as boundary families, not service-layer convenience wrappers | SIM-03 | wording can silently re-legitimize helper-level truth | Read `20-CONTEXT.md`, `20-RESEARCH.md`, updated boundary docs and verify formal authority stays in protocol boundary |
| `mqtt.topic.v1` / `mqtt.message-envelope.v1` do not turn message processor, transport utils, or `parse_mqtt_payload()` shim into second authority roots | SIM-03 | topic/envelope formalization can drift into transport ownership ambiguity | Read updated docs/tests together and confirm message processor and `payload.py` only consume formal decoder truth |
| replay / fixture docs remove partial/de-scope wording without inventing a second authority chain | SIM-05 | asset matrices can drift via documentation shortcuts | Review protocol-boundary fixture README, replay README, manifests, and baseline authority wording as one bundle |
| `RESIDUAL_LEDGER.md` 中关于 remaining families 的 partial / de-scope 叙述被显式关闭或缩窄为真实剩余项 | SIM-05 | governance README 与 residual truth 容易只改其一 | Read `.planning/reviews/RESIDUAL_LEDGER.md` together with fixture/replay docs and confirm the same families no longer remain in stale carry-forward language |

---

## Validation Sign-Off

- [x] All planned tasks have automated verification commands or explicit manual gates.
- [x] Existing infrastructure is sufficient; no separate Wave 0 plan is required.
- [x] Task ordering reflects roadmap dependency order: REST → MQTT → inventory/governance sync.
- [x] Sampling continuity exists across all 3 waves.
- [x] No watch-mode flags are present.
- [x] `nyquist_compliant: true` is set in frontmatter.
- [ ] Execution evidence has not been collected yet.
- [ ] Wave-end gates have not run yet.

**Approval:** pending execution
