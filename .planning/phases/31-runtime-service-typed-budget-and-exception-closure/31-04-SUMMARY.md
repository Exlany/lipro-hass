# 31-04 Summary

## Outcome

- `tests/meta/test_phase31_runtime_budget_guards.py` 已把 runtime/service/platform touched zones 的 `sanctioned_any`、`backlog_any`、broad-catch allowlist 与 `type: ignore` no-growth contract 编码成 machine truth。
- `.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md` 与 `.planning/v1.3-HANDOFF.md` 现已把 `Phase 25 -> 31` continuation route 的 closeout truth 明确写成 single-source planning story。
- `tests/meta/test_governance_guards.py` 与 `tests/meta/test_governance_closeout_guards.py` 也已从 `30-03 partial` 推进到 `30/31 complete` 收官态，防止后续规划真相倒退。

## Key Files

- `tests/meta/test_phase31_runtime_budget_guards.py`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_governance_closeout_guards.py`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/v1.3-HANDOFF.md`
- `.planning/phases/31-runtime-service-typed-budget-and-exception-closure/31-VALIDATION.md`
- `.planning/phases/31-runtime-service-typed-budget-and-exception-closure/31-VERIFICATION.md`

## Validation

- `uv run mypy custom_components/lipro/core/coordinator custom_components/lipro/services custom_components/lipro/entities custom_components/lipro/select.py custom_components/lipro/sensor.py && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_toolchain_truth.py tests/meta/test_phase31_runtime_budget_guards.py`

## Notes

- 预算化不是借口；任何 future 扩写都必须同步 guard、verification 与 planning truth。