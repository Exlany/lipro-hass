# Summary 113-03

## What changed
- 新增 `tests/meta/test_phase113_hotspot_assurance_guards.py`，冻结 Phase 113 hotspot line-budget registry、helper import locality，以及 default `scripts/lint` 的 changed-surface focused assurance 合同。
- 升级 `scripts/lint` 默认模式：当 changed surfaces 命中 submit/result hotspot、Phase 113 docs/toolchain truth、或 governance handoff truth 时，会自动补跑对应 focused pytest；`--full` 仍保留完整 governance/coverage 矩阵。
- 同步回写 `CONTRIBUTING.md`、`.planning/codebase/TESTING.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/reviews/FILE_MATRIX.md`、`.planning/reviews/RESIDUAL_LEDGER.md`、`.planning/reviews/KILL_LIST.md` 与 `tests/meta/toolchain_truth_ci_contract.py`，让 docs / machine truth / residual-delete truth 保持同一叙事。
- 为 `share_client_submit_attempts.py`、`share_client_submit_outcomes.py`、`result_support.py` 新增 `FILE_MATRIX` 登记，并把 `FILE_MATRIX` Python 总数更新到 `749`。

## Why it changed
- `QLT-46` 不只要求热点代码瘦身，还要求剩余 allowance 被显式冻结，并让维护者默认入口能在 touched surfaces 变更时自动看到 focused regressions。
- 如果不把 hotspot budgets、tooling/docs truth 与 residual/delete-gate 账本同步收口，本 phase 仍会留下“实现完成、治理滞后”的半闭环。

## Verification
- `uv run pytest -q tests/meta/test_phase113_hotspot_assurance_guards.py tests/meta/toolchain_truth_ci_contract.py tests/meta/test_governance_release_docs.py tests/meta/toolchain_truth_docs_fast_path.py`
- `28 passed in 3.68s`
- `uv run python scripts/check_file_matrix.py --check`
- `bash -n scripts/lint`
- `uv run ruff check tests/meta/test_phase113_hotspot_assurance_guards.py tests/meta/toolchain_truth_ci_contract.py tests/meta/governance_current_truth.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py`
- `All checks passed!`

## Outcome
- remaining hotspot growth 现在具备 machine-checkable budget / locality / residual truth，而不是 conversation-only 例外。
- maintainer 通过默认 `./scripts/lint` 就能在 Phase 113 touched surfaces 上得到 focused assurance，不必再靠记忆补跑手工 pytest。
