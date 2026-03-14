---
phase: 11-control-router-formalization-wiring-residual-demotion
plan: "08"
status: completed
completed: 2026-03-14
requirements:
  - GOV-08
---

# Summary 11-08

## Outcome

- `.github/workflows/ci.yml` 已支持 `workflow_call`，`.github/workflows/release.yml` 先复用 CI 再校验 tag / project version 一致性，发布旁路已被阻断。
- `.github/ISSUE_TEMPLATE/*`、`.github/pull_request_template.md`、`CONTRIBUTING.md`、`SECURITY.md` 与 `docs/README.md` / `AGENTS.md` 已统一到单一开源治理口径。
- `tests/meta/test_governance_guards.py` 与 `tests/meta/test_version_sync.py` 已补结构化守卫，锁定 phase 资产身份、version sync 与安全披露入口。

## Verification

- 见 `11-VERIFICATION.md` 的 Phase 11 closeout suite。
- 关键切片：`tests/meta/test_governance_guards.py`、`tests/meta/test_version_sync.py`。

## Governance Notes

- release 不再绕过 CI / governance / version checks；对外协作入口、测试契约与安全披露路径已完成统一。
