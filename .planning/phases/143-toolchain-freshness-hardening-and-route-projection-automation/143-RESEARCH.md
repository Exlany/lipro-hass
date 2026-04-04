# Phase 143 Research

## Thesis

`Phase 142` 已把 governance load shedding / derived-truth audit 收束为单一 current-route story，但 nested worktree / repo-root detection、route projection hardcode、link freshness 与 docs-entry drift 仍有 machine-checkable proof 不足的问题。

## Decision

- selector family、registry、baseline docs 与 focused guards 继续是唯一 route authority。
- local `gsd-tools` fast-path 在 nested worktree 下必须通过 explicit isolated `--cwd` root 证明；direct-cwd drift 只能算 tooling fallback。
- `Phase 143` 只做 toolchain / freshness / route-projection hardening，不提前混入 runtime/command/auth hotspot refactor。

## Candidate Work

- local fast-path `gsd-tools` invocation contract 与 repo-root proof
- `.planning/codebase` freshness / link audit / docs-entry drift proof chain
- maintainer-facing route projection hardcode audit 与 guard automation

## Guardrails

- 不让 tools、docs 或 `.planning/codebase` 升格为新的 authority layer。
- 不复活 `v1.43` archived baseline 作为 live route。
- 不在本 phase 提前改动 `runtime_types.py`、dispatch / result、auth/session 或 firmware/share hotspot 实现。
