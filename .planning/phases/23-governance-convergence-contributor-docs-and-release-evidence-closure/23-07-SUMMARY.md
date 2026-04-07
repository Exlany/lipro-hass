# 23-07 Summary

## Outcome

- 刷新 `.planning/codebase/TESTING.md` 的仓库统计与边界说明，并用 meta guard 锁定测试文件数量与 scripts/tests helper-only / pull-only 例外。
- 明确裁决 `scripts/check_architecture_policy.py` 与 `scripts/export_ai_debug_evidence_pack.py` 对 `tests.*` 的依赖身份：前者仅可 pull `tests.helpers/*`，后者仅可 pull `tests.harness/evidence_pack/*`。
- 将本轮审计发现映射到 `23-04..23-08` 与显式 follow-up / defer ledger，避免 wording guards、巨型测试、release hardening、firmware metadata 等问题继续静默漂移。

## Key Files

- `.planning/codebase/TESTING.md`
- `.planning/phases/23-governance-convergence-contributor-docs-and-release-evidence-closure/23-AUDIT-CHECKLIST.md`
- `tests/meta/test_toolchain_truth.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_evidence_pack_authority.py`
- `tests/meta/test_governance_guards.py`

## Validation

- `uv run pytest tests/meta/test_toolchain_truth.py tests/meta/test_evidence_pack_authority.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py -q` → passed
- `uv run python scripts/check_architecture_policy.py --check` → passed

## Notes

- `TESTING.md` 继续是 derived collaboration map，不是新的 authority source。
- scripts/tests 耦合只允许 helper-only / pull-only 例外；新增例外必须同步治理文档与守卫。
