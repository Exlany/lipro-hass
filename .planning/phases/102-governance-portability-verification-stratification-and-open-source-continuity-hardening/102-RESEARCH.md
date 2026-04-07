# Phase 102 Research

## Findings

1. `tests/meta/test_governance_route_handoff_smoke.py` 对本机 `node` / `~/.codex/get-shit-done/bin/gsd-tools.cjs` 的硬依赖不够可移植；fast-path 证明应 capability-aware，而不是 unconditional hard fail。
2. `tests/meta/governance_current_truth.py` 已是 machine-readable route contract 真源，但 phase list / plan counts / focused guard footprints / testing inventory snapshot 仍可继续收口。
3. `.planning/baseline/VERIFICATION_MATRIX.md` 顶部 current archived-only truth 与 `Phase 98 -> 101` historical closeout note 混排，需要分层。
4. `.planning/codebase/README.md` freshness 漂移，且 public docs / maintainer appendix wording 需要与 latest archived evidence pointer 重新对齐。
5. `v1.28` 适合采用单 phase archived-only closeout；无需保留 active milestone 终态。

## Plan Shape

- `102-01`：治理真相常量中心化 + smoke portability
- `102-02`：verification/docs/codebase-map stratification + wording refresh
- `102-03`：closeout assets / archive snapshots / promoted bundle / audit proof
