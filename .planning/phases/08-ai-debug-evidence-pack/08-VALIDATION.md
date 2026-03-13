---
phase: 08
slug: ai-debug-evidence-pack
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-13
updated: 2026-03-13
---

# Phase 08 — Validation Strategy

> Per-phase validation contract for AI Debug Evidence Pack.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` + `ruff` |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q -x tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py` |
| **Full suite command** | `uv run ruff check scripts/export_ai_debug_evidence_pack.py tests/harness/evidence_pack tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py && uv run pytest -q -x tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py` |
| **Estimated runtime** | ~8 seconds |

---

## Sampling Rate

- **After every task commit:** Run `Quick run command`
- **After every plan wave:** Run `Full suite command`
- **Before phase closeout:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| `08-01-01` | `08-01` | 1 | `AID-01`, `AID-02` | schema / structure | `uv run pytest -q -x tests/integration/test_ai_debug_evidence_pack.py` | ❌ W0 | ⬜ pending |
| `08-01-02` | `08-01` | 1 | `AID-02` | redaction / pseudo-id policy | `uv run pytest -q -x tests/meta/test_evidence_pack_authority.py` | ❌ W0 | ⬜ pending |
| `08-01-03` | `08-01` | 1 | `AID-01` | governance / authority source | `uv run pytest -q -x tests/meta/test_evidence_pack_authority.py tests/meta/test_governance_guards.py` | ❌ W0 | ⬜ pending |
| `08-02-01` | `08-02` | 2 | `AID-01` | exporter / collector integration | `uv run pytest -q -x tests/integration/test_ai_debug_evidence_pack.py` | ❌ W0 | ⬜ pending |
| `08-02-02` | `08-02` | 2 | `AID-01`, `AID-02` | end-to-end pack generation | `uv run pytest -q -x tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py` | ❌ W0 | ⬜ pending |
| `08-02-03` | `08-02` | 2 | `AID-01`, `AID-02` | governance / closeout handoff | `uv run pytest -q -x tests/meta/test_evidence_pack_authority.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `scripts/export_ai_debug_evidence_pack.py` — 唯一导出入口
- [ ] `tests/harness/evidence_pack/` — schema / sources / collector / redaction home
- [ ] `tests/fixtures/evidence_pack/README.md` — evidence pack fixture/index rules
- [ ] `tests/integration/test_ai_debug_evidence_pack.py` — end-to-end pack assertions
- [ ] `tests/meta/test_evidence_pack_authority.py` — authority / redaction / source guards

---

## Manual-Only Verifications

若有任何 evidence section 仍需人工确认其 authority/source 映射，必须在此登记，并在 phase closeout 时清零。

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all missing evidence-pack artifacts
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
