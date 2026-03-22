# Phase 59 PRD — Verification Localization & Governance Guard Topicization

## Goal

把 public-surface / governance-history / follow-up-route megaguards 与 `tests/core/test_device_refresh.py` topicize 成按稳定 truth family / concern boundary 划分的更窄套件，同时保持 guard semantics、coverage honesty 与 current-story docs 一致。

## In Scope

- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_governance_phase_history.py`
- `tests/meta/test_governance_followup_route.py`
- `tests/core/test_device_refresh.py`
- 与这些 suites 直接关联的 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`
- `.planning/baseline/VERIFICATION_MATRIX.md` 与必要的 review truth 同步

## Requirements

- `TST-11`
- `QLT-19`
- `GOV-43`

## Success Criteria

1. giant verification buckets 被拆成更窄、更可单独运行的 topical suites，失败定位半径明显下降；
2. split 过程中不新增 second truth source、helper-owned governance story 或 broad fixture folklore；
3. current-story docs 与 verification truth 准确记录新的 suite topology 与 focused commands。

## Non-Goals

- 不直接分解 `scripts/check_file_matrix.py`
- 不直接改 production architecture / public surface
- 不为了 split 而引入新的 repo-wide helper root
