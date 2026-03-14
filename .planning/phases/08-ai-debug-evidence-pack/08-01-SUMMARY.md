---
phase: 08-ai-debug-evidence-pack
plan: "01"
status: completed
completed: 2026-03-13
requirements:
  - AID-01
  - AID-02
---

# Summary 08-01

## Outcome

- 新增 `tests/harness/evidence_pack/` formal home：`schema.py`、`sources.py` 与 `redaction.py` 已把 AI debug evidence pack 的 schema、formal-source registry、report-local pseudo-id 与 pack-level redaction 收口到单一 assurance/tooling 家园。
- `sources.py` 已明确 evidence pack 只允许 pull `07.3` telemetry exporter truth、`07.4` replay harness/report truth、`07.5` evidence index / governance matrices，以及 boundary inventory / authority fixtures；不允许从未登记路径临时拼第二套事实。
- `redaction.py` 已落地 Phase 8 脱敏裁决：允许真实时间戳；`entry_ref` / `device_ref` 报告内稳定、跨报告不可关联；`secret` / token / `password_hash` / access-key 等凭证等价物永不进入 pack。
- `AUTHORITY_MATRIX.md`、`PUBLIC_SURFACES.md`、`VERIFICATION_MATRIX.md`、`V1_1_EVIDENCE_INDEX.md`、`RESIDUAL_LEDGER.md` 与 `KILL_LIST.md` 已同步登记 evidence-pack 的 assurance-only / pull-only 身份，避免 phase 8 变成新的 runtime/control root。

## Verification

- `uv run pytest -q -x tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py`

## Governance Notes

- 本计划不绑定 `msgspec` / `pydantic v2`；schema 继续保持 backend-swappable。
- evidence pack 只消费既有 telemetry / replay / governance 真相链，不新建第二套 authority / redaction 政策。
