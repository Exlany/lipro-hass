# Phase 140 Research

## Findings

- `.planning/baseline/VERIFICATION_MATRIX.md` 与 `V1_41_REMEDIATION_CHARTER.md` 的部分命令仍引用旧测试路径，说明 archive/current governance freshness 未形成自动守卫。
- `CHANGELOG.md` 的 Unreleased 段落仍泄露 `.planning` / phase-internal 术语，与 docs/README 规定的 public summary 身份不完全一致。
- `SUPPORT.md` 已保留 private-access / future public mirror 条件语义，但 maintainer runbook 对 stable support target 的措辞偏乐观，需要补足 access-mode 条件。
- 现有 release/governance tests 对 runbook appendix 污染与 route pointers 守得较好，但对 changelog public-summary scope 与 conditional support wording 覆盖不足。

## Proposed Direction

1. 刷新 baseline/archived docs 中所有已迁移的测试路径，优先修复不可执行 proof。
2. 收紧 changelog Unreleased contract，只保留 public-facing stories。
3. 统一 README/SUPPORT/runbook 对 private-access 与 release asset reachability 的条件表述。
4. 用 focused meta tests 冻结上述 contract，避免下一轮再回流。
5. 把 audit 中记录的 control/runtime/domain hotspot 仅整理为后续 codebase-freshness backlog，不在本 phase 顺手扩 scope：service-router layering、runtime_types breadth、device façade side-car residual、entry-root lazy import tax。
