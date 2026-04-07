# Phase 120 Plan 120-03 Summary

## Outcome

- `scripts/check_file_matrix.py` 现改为单一 dynamic-import strategy：用同一套 `importlib.import_module(...)` 逻辑加载 checker 子模块，不再保留 `TYPE_CHECKING` / `__package__` 双轨导入枝杈。
- `scripts/lint` 的 changed-surface assurance 去掉 `phase113_*` 命名与输出口径，改成可复用的 generic changed-surface family。
- `tests/meta/toolchain_truth_checker_paths.py` 与 `tests/meta/test_phase89_tooling_decoupling_guards.py` 从字符串匹配升级为 AST / behavior truth 断言，减少 phase-literal folklore。
- `tests/conftest.py` 的本地依赖提示统一改成 `uv add --dev pytest-homeassistant-custom-component`。
- `docs/developer_architecture.md` 仅保留 current developer guidance；历史 appendix 已下沉到 `docs/architecture_archive.md`。
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` 与 `.github/pull_request_template.md` 统一改成 stable current-selector family + latest archived pointer 口径，不再把 `.planning/v1.33...` 当 current-route truth。
- `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` 已统一激活 `v1.34 active milestone route / Phase 120 planned / starting from latest archived baseline = v1.33`，默认下一步改为 `$gsd-execute-phase 120`。
- continuity 叙事继续保持 honest freeze posture；本轮没有伪造 hidden delegate、repo-external continuity closure 或 repo-external fallback 已解决。

## Validation

- `uv run pytest tests/meta/toolchain_truth_checker_paths.py tests/meta/test_phase89_tooling_decoupling_guards.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_docs.py -q`
- `uv run python scripts/check_file_matrix.py --check`
