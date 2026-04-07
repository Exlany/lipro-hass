# Phase 74: Legacy auth residual retirement, test topicization, and milestone closeout - Research

**Researched:** 2026-03-25
**Confidence:** HIGH

## Summary

本 phase 的最佳策略不是继续发明新 helper 或新 façade，而是把“已经完成的真实收口”彻底同步到代码、守卫、文档与治理资产：

1. `AuthSessionSnapshot` 早已成为唯一正式 auth/session truth，但 `KILL_LIST.md` 仍把 `get_auth_data()` fallback 记成 active delete gate；这属于治理残留，不是生产残留。
2. `custom_components/lipro/services/registrations.py` 已不再承担生产 ownership；删除它的收益高于保留，因为当前只剩测试与文档在消费这个 compat shell。
3. `docs/README.md` 应退回 public docs map 身份；current-route、archive list、next GSD command 应下沉到 maintainer-facing governance truth，而不是留在公开 first hop。
4. `.gitignore` 的 `Phase 12` 特例已经与当前 phase-asset policy 脱节；与其继续维护例外，不如直接承认 `.planning/phases/**/*.md` 可被 Git 跟踪，而 authority 仍由 allowlist/reference 决定。
5. `tests/core/test_share_client.py` 与 `tests/core/coordinator/runtime/test_command_runtime.py` 最适合做“thin shell + topical modules + support helper”式 topicization；这样既能降低 failure radius，也不会改变现有 verification lane 的入口路径。
6. retired stubs 当前更适合“诚实化 + delete gate formalization”，而不是立刻删除；当前 public docs / registry / tests 仍把它们作为 unsupported fail-fast 入口发布。

## Recommended Execution Order

1. 先清掉真正的 compat shell：删除 `services/registrations.py`，同步 imports / guards / docs / policy。
2. 再 topicize 两个 remaining large suites，保留原测试入口文件作为 thin shell。
3. 再完成 docs / registry / `.gitignore` / retired stub honesty 收口。
4. 最后跑 full gates，写回 `PROJECT / ROADMAP / REQUIREMENTS / STATE` 与 `74-VALIDATION.md`，把 `v1.20` 推到 `Phase 74 complete / closeout-ready`。

## Key Risks

- 只删代码不删治理，会被 `check_architecture_policy.py`、`check_file_matrix.py` 与 meta guards 立刻抓住。
- topicization 若改变测试入口路径而不保留 thin shell，会放大 verification-matrix / history docs 的同步成本。
- docs honesty 若直接改 package version 或 release tag 叙事，会引入新的不确定性；本轮应只澄清 package semver 与 internal governance milestone 是两条语义线。
