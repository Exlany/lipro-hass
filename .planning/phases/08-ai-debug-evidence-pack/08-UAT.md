---
status: testing
phase: 08-ai-debug-evidence-pack
source:
  - 08-01-SUMMARY.md
  - 08-02-SUMMARY.md
  - 08-VERIFICATION.md
started: 2026-03-13T17:10:00Z
updated: 2026-03-13T17:10:00Z
---

## Current Test

number: 1
name: Evidence Pack 导出入口是否单一且可直接使用
expected: |
  运行 `uv run python scripts/export_ai_debug_evidence_pack.py` 后，
  你应该能得到一份 `ai_debug_evidence_pack.json` 与配套 markdown index；
  并且从导出入口可以清楚判断：它只是 pull 正式真源，不会再临时拼出第二套事实。
awaiting: user response

## Tests

### 1. Evidence Pack 导出入口是否单一且可直接使用
expected: 运行导出脚本后，能看到 JSON pack 与 markdown index 两类产物，且入口语义清楚表明它是单一导出面。
result: pending

### 2. 导出结构是否稳定且便于 AI 消费
expected: 打开导出的 JSON 后，应能稳定找到 `metadata / telemetry / replay / boundary / governance / index` 六个 section，并能从 index 追溯 authority/source。
result: pending

### 3. 脱敏策略是否符合 Phase 8 承诺
expected: 报告中允许真实时间戳；`entry_ref` / `device_ref` 在单份报告内稳定、跨报告不可关联；token、password_hash、access-key 等凭证等价物不会出现。
result: pending

### 4. 治理与证据入口是否前后一致
expected: 打开 `.planning/reviews/V1_1_EVIDENCE_INDEX.md`、`AUTHORITY_MATRIX.md`、`PUBLIC_SURFACES.md` 时，应能从治理文档直接找到 evidence pack 的正式来源、边界与验证命令，而不是靠口头约定。
result: pending

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0

## Gaps

none yet
