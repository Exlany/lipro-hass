---
phase: 08
slug: ai-debug-evidence-pack
status: passed
verified_on: 2026-03-13
requirements:
  - AID-01
  - AID-02
---

# Phase 08 Verification

## Goal

验证 `Phase 8` 是否真正把 `07.3 telemetry exporter`、`07.4 replay harness/report`、`07.5 governance closeout` 收敛成一份可给 AI 调试/分析的统一 evidence pack：pull-only、authority-traceable、统一脱敏、默认 JSON + markdown index。

## Must-Have Score

- Verified: `2 / 2`
- Human-only items: `0`
- Gaps found: `0`

## Requirement Verdict

| Requirement | Verdict | Evidence |
|-------------|---------|----------|
| `AID-01` | ✅ passed | `tests/harness/evidence_pack/`、`scripts/export_ai_debug_evidence_pack.py`、`tests/integration/test_ai_debug_evidence_pack.py`、`tests/meta/test_evidence_pack_authority.py`、更新后的 `AUTHORITY_MATRIX / PUBLIC_SURFACES / VERIFICATION_MATRIX / FILE_MATRIX / V1_1_EVIDENCE_INDEX.md` 已形成 single-entry、formal-source-only、authority-traceable 的 pack 导出链。 |
| `AID-02` | ✅ passed | `tests/harness/evidence_pack/redaction.py` 与 integration/meta tests 已证明：真实时间戳保留；`entry_ref` / `device_ref` 报告内稳定、跨报告不可关联；`secret` / token / `password_hash` / access-key 等凭证等价物不会进入 pack。 |

## Automated Proof

- `uv run pytest -q -x tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py`
- `uv run ruff check scripts/export_ai_debug_evidence_pack.py tests/harness/evidence_pack tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py`
- `uv run pytest -q -x tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py`

## Verified Outcomes

- evidence pack 只有一个正式导出入口：`scripts/export_ai_debug_evidence_pack.py`。
- pack 只 pull 正式真源，并通过 `index.section_authority_trace` 与 section-level `source_paths` 暴露 authority/source trace。
- pack 统一输出 `metadata / telemetry / replay / boundary / governance / index` 六个 section，并附带可读的 markdown index。
- repo-relative authority path、governance verify commands、residual pointers 与 evidence index 已进入统一治理链，可直接交给 AI / tooling /维护者消费。

## Human Verification

- none

## Gaps

- none

## Verdict

`Phase 8` 达成目标，可以进入 `verify-work 7.5` 与 `verify-work 8` 的对话式验收。
