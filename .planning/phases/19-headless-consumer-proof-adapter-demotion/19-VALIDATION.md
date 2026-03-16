---
phase: 19
slug: headless-consumer-proof-adapter-demotion
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-16
---

# Phase 19 — Validation Strategy

> Per-phase validation contract for headless consumer proof and adapter demotion.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + ruff + mypy |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q tests/flows/test_config_flow.py tests/core/test_init.py tests/core/test_token_persistence.py tests/core/capability/test_registry.py tests/core/device/test_device.py tests/platforms/test_entity_behavior.py` |
| **Wave gate commands** | `uv run python scripts/check_architecture_policy.py --check` + `uv run python scripts/check_file_matrix.py --check` + `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` |
| **Full suite command** | `uv run pytest -q` |
| **Estimated runtime** | ~120-180 seconds |

---

## Sampling Rate

- **After every task commit:** Run the task-level automated command listed below.
- **After wave 1:** Re-run the quick auth/bootstrap regression loop plus the new headless boot focused test.
- **After wave 2:** Run the headless proof integration loop plus replay/evidence suites.
- **After wave 3: Re-run the adapter-shell regression loop.
- **After wave 4 / before `$gsd-verify-work`:**** Run the wave gate commands, `uv run ruff check .`, `uv run mypy`, and the full suite command.
- **Max feedback latency:** 180 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 19-01-01 | 19-01 | 1 | CORE-02 | boot-home static gate | `uv run ruff check custom_components/lipro/headless && uv run mypy custom_components/lipro/headless` | ❌ create in task | ⬜ pending |
| 19-01-02 | 19-01 | 1 | CORE-02 | adapter regression | `uv run pytest -q tests/flows/test_config_flow.py tests/core/test_init.py tests/core/test_token_persistence.py` | ✅ | ⬜ pending |
| 19-01-03 | 19-01 | 1 | CORE-02 | helper purity guard | `uv run ruff check custom_components/lipro/flow/credentials.py custom_components/lipro/flow/login.py custom_components/lipro/headless` | ✅ | ⬜ pending |
| 19-01-04 | 19-01 | 1 | CORE-02 | focused boot regression | `uv run pytest -q tests/core/test_headless_boot.py tests/flows/test_config_flow.py tests/core/test_init.py tests/core/test_token_persistence.py` | ❌ create in task | ⬜ pending |
| 19-02-01 | 19-02 | 2 | CORE-02 | proof harness static gate | `uv run ruff check tests/harness/headless_consumer.py custom_components/lipro/headless/boot.py` | ❌ create in task | ⬜ pending |
| 19-02-02 | 19-02 | 2 | CORE-02 | headless integration smoke | `uv run pytest -q tests/integration/test_headless_consumer_proof.py tests/core/api/test_protocol_contract_matrix.py tests/core/capability/test_registry.py tests/snapshots/test_device_snapshots.py` | ❌ create in task | ⬜ pending |
| 19-02-03 | 19-02 | 2 | CORE-02 | replay + evidence chain | `uv run pytest -q tests/integration/test_headless_consumer_proof.py tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py` | ↺ after `19-02-02` | ⬜ pending |
| 19-02-04 | 19-02 | 2 | CORE-02 | evidence authority gate | `uv run pytest -q tests/meta/test_evidence_pack_authority.py tests/integration/test_ai_debug_evidence_pack.py` | ✅ | ⬜ pending |
| 19-03-01 | 19-03 | 3 | CORE-02 | platform shell regression | `uv run pytest -q tests/platforms/test_entity_behavior.py` | ✅ | ⬜ pending |
| 19-03-02 | 19-03 | 3 | CORE-02 | runtime-locator adapter regression | `uv run pytest -q tests/integration/test_headless_consumer_proof.py tests/platforms/test_entity_behavior.py` | ✅ | ⬜ pending |
| 19-03-03 | 19-03 | 3 | CORE-02 | adapter-shell integration regression | `uv run pytest -q tests/platforms/test_entity_behavior.py tests/integration/test_headless_consumer_proof.py` | ✅ | ⬜ pending |
| 19-04-01 | 19-04 | 4 | CORE-02 | baseline + phase-complete sync gate | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` | ✅ | ⬜ pending |
| 19-04-02 | 19-04 | 4 | CORE-02 | residual / no-change governance | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_evidence_pack_authority.py` | ✅ | ⬜ pending |
| 19-04-03 | 19-04 | 4 | CORE-02 | second-root / backflow policy guard | `uv run python scripts/check_architecture_policy.py --check && uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] Existing pytest / ruff / mypy / governance infrastructure already covers Phase 19。
- [x] `tests/core/test_headless_boot.py`、`tests/harness/headless_consumer.py` 与 `tests/integration/test_headless_consumer_proof.py` 是 task-level deliverables，不构成独立 Wave 0 blocker。
- [x] 若 Phase 19 引入新的 evidence sources 或 proof outputs，`tests/harness/evidence_pack/sources.py` 与 `tests/meta/test_evidence_pack_authority.py` 在对应 task 中同轮补齐即可，无需独立 Wave 0。

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Headless proof wording remains “proof-only / non-public” across docs and plan assets | CORE-02 | 是否暗示第二 root 需要人工仲裁，而非仅靠关键字匹配 | Read `19-CONTEXT.md`, `19-RESEARCH.md`, `PUBLIC_SURFACES.md`, and `ARCHITECTURE_POLICY.md` together and confirm they never describe headless boot as a second formal root |
| If a contributor-facing proof command is added, docs explain it as a local verification tool rather than a supported product surface | CORE-02 | Command semantics and onboarding wording affect architecture expectations | Review `CONTRIBUTING.md` and any new `scripts/**` help text before merge |

---

## Validation Sign-Off

- [x] All tasks have an automated verify contract or explicit manual gate.
- [x] Existing infrastructure is sufficient; no dedicated Wave 0 plan is required.
- [x] Task ordering now reflects file-creation timing for new proof assets.
- [x] Sampling continuity exists across all 4 waves.
- [x] No watch-mode flags are present.
- [x] `nyquist_compliant: true` is set in frontmatter.
- [ ] Execution evidence has not been collected yet.
- [ ] Wave-end gates have not run yet.

**Approval:** pending execution
