# 23-02 Summary

## Outcome

- README / README_zh / CONTRIBUTING / SUPPORT / troubleshooting / bug template / PR template / runbook 现在对同一条 v1.2 support/security/troubleshooting/release story 讲同一套口径。
- `failure_summary` / `failure_entries` 提示已进入 bug-report、support 与 troubleshooting 路径；公开入口不再只要求 diagnostics/developer report，而是明确鼓励附上结构化失败摘要。
- 旧的 “Phase 10 targeted regression” 术语已被 phase-neutral wording 取代；双语 README 的 architecture/refactor 特性描述也已重新对齐。

## Key Files

- `README.md`
- `README_zh.md`
- `CONTRIBUTING.md`
- `SUPPORT.md`
- `docs/TROUBLESHOOTING.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/bug.yml`
- `.github/ISSUE_TEMPLATE/config.yml`

## Validation

- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py`
- `uv run ruff check .`

## Notes

- `SECURITY.md` 没有新增 truth drift，因此本 plan 维持 **no-change**；它继续承担私密披露路径，不承担 troubleshooting / release evidence 入口职责。
