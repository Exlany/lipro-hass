---
phase: 08-ai-debug-evidence-pack
plan: "02"
status: completed
completed: 2026-03-13
requirements:
  - AID-01
  - AID-02
---

# Summary 08-02

## Outcome

- 新增 `tests/harness/evidence_pack/collector.py`：collector 只做 pull / merge / serialize，组合 `07.3` exporter views、`07.4` replay summaries、boundary inventory / authority pointers 与 `07.5` governance evidence，生成稳定的 `metadata / telemetry / replay / boundary / governance / index` 六段结构。
- 新增 `scripts/export_ai_debug_evidence_pack.py` 作为唯一导出入口：统一输出 `ai_debug_evidence_pack.json` 与 `ai_debug_evidence_pack.index.md`，不获取 coordinator / protocol private internals。
- 新增 `tests/integration/test_ai_debug_evidence_pack.py` 与 `tests/meta/test_evidence_pack_authority.py`：验证 section shape、repo-relative authority path、真实时间戳保留、报告内稳定且跨报告不可关联的伪匿名引用，以及 formal-source-only / governance registration / sensitive-key blocking。
- `scripts/check_file_matrix.py` 与 `FILE_MATRIX.md` 已把 `tests/harness/evidence_pack/*`、`tests/integration/test_ai_debug_evidence_pack.py`、`tests/meta/test_evidence_pack_authority.py`、`scripts/export_ai_debug_evidence_pack.py` 正式登记为 `Phase 8` assurance assets。

## Verification

- `uv run ruff check scripts/export_ai_debug_evidence_pack.py tests/harness/evidence_pack tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py`
- `uv run pytest -q -x tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py`

## Governance Notes

- `08` 只交付 assurance/tooling export，不扩大 replay corpus，不改写 exporter schema，也不新增 file-level kill target。
- `V1_1_EVIDENCE_INDEX.md` 已登记 phase 8 产物，为后续 AI / tooling / closeout review 提供可 pull 的稳定入口。
