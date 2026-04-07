# 27-04 Summary

## Outcome

- `tests/core/test_init.py` 现在聚焦 setup/runtime lifecycle；service handler / device targeting / diagnostics / schedule / anonymous-share / developer-report 回归已抽到新的 `tests/core/test_init_service_handlers.py`。
- `tests/meta/test_governance_guards.py` 保留 repo-level governance 主闸；milestone closeout / archive / handoff truth 已拆到新的 `tests/meta/test_governance_closeout_guards.py`。
- `.planning/codebase/TESTING.md`、`.planning/reviews/FILE_MATRIX.md` 与 `tests/meta/test_toolchain_truth.py` 已同步新的测试清单、最小回归建议与文件总数，避免“测试拆了，但治理图谱没跟上”。
- `AGENTS.md`、`CONTRIBUTING.md`、`.github/workflows/ci.yml`、`.pre-commit-config.yaml`、`docs/MAINTAINER_RELEASE_RUNBOOK.md` 与 `scripts/check_file_matrix.py` 也已把 `test_governance_closeout_guards.py` / `test_init_service_handlers.py` 纳入常规门禁与 rewrite 分类，避免 closeout truth 只被手工记住。

## Key Files

- `tests/core/test_init.py`
- `tests/core/test_init_service_handlers.py`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_governance_closeout_guards.py`
- `.planning/codebase/TESTING.md`
- `.planning/reviews/FILE_MATRIX.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `.github/workflows/ci.yml`
- `.pre-commit-config.yaml`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `scripts/check_file_matrix.py`
- `tests/meta/test_toolchain_truth.py`

## Validation

- `uv run pytest -q tests/core/test_init.py tests/core/test_init_service_handlers.py` → `160 passed`
- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_toolchain_truth.py` → `44 passed`
- `uv run pytest -q tests/core/test_init.py tests/core/test_init_service_handlers.py tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` → `234 passed`

## Notes

- 本 tranche 刻意保留锚点文件 `tests/core/test_init.py` / `tests/meta/test_governance_guards.py`，只把主题性最强的测试拆出去，避免为了“拆分”引入第二套 hidden helper truth。
