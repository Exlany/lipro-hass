---
phase: 85-terminal-audit-refresh-and-residual-routing
plan: "02"
type: summary
status: completed
date: 2026-03-27
requirements:
  - AUD-04
  - GOV-62
verification:
  - uv run python scripts/check_file_matrix.py --check
  - uv run pytest -q tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_milestone_archives.py tests/meta/test_governance_release_docs.py
files:
  - .planning/reviews/V1_23_TERMINAL_AUDIT.md
  - .planning/reviews/RESIDUAL_LEDGER.md
  - .planning/reviews/KILL_LIST.md
  - .planning/reviews/FILE_MATRIX.md
---

# Phase 85 Plan 02 Summary

本计划把 `v1.23 / Phase 85` 的 repo-wide terminal audit verdict 从会话结论冻结为 review-ledger-backed truth：`close now`、`route next`、`explicitly keep` 现都能在长期治理文件中直接找到。

## 完成内容

- 重写 `.planning/reviews/V1_23_TERMINAL_AUDIT.md`，按 governance/docs、production、assurance、historical evidence 四类输出 file-level verdict、owner、exit condition 与 evidence。
- 强化 `.planning/reviews/RESIDUAL_LEDGER.md` 的 `Phase 85 Audit-Routed Carry-Forward`，明确 close-now truth sync 不回流成 active residual，archived evidence 继续保持 explicitly-keep 身份。
- 更新 `.planning/reviews/KILL_LIST.md`，把 `share_client.py` 的两个 symbol-level delete gates 固定为 `Phase 86` 路由，并明确 `runtime_infra.py` 与 giant assurance suites 不是 file-level kill target。
- 收紧 `.planning/reviews/FILE_MATRIX.md` 的 residual/delete-gate 叙述，并同步 Python inventory 计数到 `668`。

## 验证结果

- `uv run python scripts/check_file_matrix.py --check` ✅ 通过
- `uv run pytest -q tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_milestone_archives.py tests/meta/test_governance_release_docs.py` ✅ 38 passed

## 偏差与修正

- 发现 `FILE_MATRIX.md` 头部 Python 总数仍为 `667`，与当前 inventory `668` 不一致；已在本计划内直接修正，随后重跑校验通过。
- 未新增任何 production code path 改动；本计划只冻结审计 verdict 与 routing truth。

## Git 说明

- 按契约者要求，**未执行任何 `git commit`**。
