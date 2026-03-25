# Phase 72 Research

## Inputs

- `.planning/reviews/V1_19_TERMINAL_AUDIT.md`
- `.planning/v1.19-MILESTONE-AUDIT.md`
- `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VERIFICATION.md`

## Findings That Directly Drive Implementation

### Bootstrap / Lifecycle

- `Coordinator` bootstrap / builder debt 仍适合沿现有 runtime home inward split，而不是引入新的 builder root。
- `EntryLifecycleController` / `EntryLifecycleSupport` 的 orchestration truth 需要继续收拢，避免 duplicated probing / assembly folklore。

### Runtime Access

- `runtime_access` family 仍有 test-aware probing / support helper residue；下一轮应保留 outward home、不保留 probing folklore。
- active route 需要直接冻结到 `v1.20 / Phase 72 planning-ready`，避免回到 no-active-route 字面同步成本。

## Rejected Alternatives

- **直接跳到 service-family / auth cleanup**：这些项已登记到 `Phase 73 -> 74`，若与 bootstrap/lifecycle 同轮混合，会放大回归面。
- **恢复 no-active-route story**：会让 `v1.20` 变成 conversation-only milestone，违背 current mutable truth。
