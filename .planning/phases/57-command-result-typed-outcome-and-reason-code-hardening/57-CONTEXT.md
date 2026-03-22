# Phase 57: Command-result typed outcome and reason-code hardening - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning
**Source:** `v1.10` milestone seed + `Phase 41/50/56` closeout evidence + targeted command-result/runtime/diagnostics reread

<domain>
## Phase Boundary

本 phase 只处理 `ERR-12 / TYP-14 / GOV-41`：把 command-result family 从散落的 raw strings 收敛为一套更明确的 typed outcome / reason-code contract，同时保持以下 truth 不漂移：

1. `custom_components/lipro/core/command/result_policy.py` 继续拥有 command-result payload classification / polling truth；
2. `custom_components/lipro/core/command/result.py` 继续拥有 stable export / failure arbitration truth；
3. runtime sender 与 diagnostics query service 只消费统一 vocabulary，不长出第二套 command outcome story；
4. outward behavior 不发生 public drift：diagnostics `query_command_result` 仍返回 `state` / `attempts` / `result`，runtime sender 仍返回 verified flag 与 classification / timeout semantics。

本 phase 不处理 retry-budget stratification、不统一 command/runtime/MQTT retry policy，也不把 command-result family 改造成新的 telemetry root 或 operation framework。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- `confirmed / failed / pending / unknown / unconfirmed` 必须从 scattered string comparisons 提升为 shared typed command-result state vocabulary。
- `command_result_failed / command_result_unconfirmed / push_failed / api_error` 必须从散落字符串提升为 shared failure-reason vocabulary；missing `msgSn` 继续视为 `command_result_unconfirmed` 的 specialized code，而不是新故事线。
- runtime sender 的 `verification_result` / `verification_classification` 语义必须继续稳定，但实现上应复用同一 typed vocabulary。
- diagnostics `QueryCommandResultResponse` 的 `state` 类型必须对齐 shared contract，而不是继续裸 `str`。
- 该 typed contract 只能落在 command-result family 自身；不得为此新增 package-level compat shell 或第二 formal home。

### Claude's Discretion
- 可以使用 `Literal` aliases、`TypedDict`、named constants、helper predicates 的任意组合，只要 outward behavior 稳定、contract 更清晰。
- governance notes 可聚焦于 public/dependency/verification truth，不必为本 phase 扩张无关 docs。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Route / North-star Truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/reviews/V1_10_MILESTONE_SEED.md`

### Prior Phase Evidence
- `.planning/phases/41-full-spectrum-architecture-code-quality-and-open-source-audit/41-REMEDIATION-ROADMAP.md`
- `.planning/phases/45-hotspot-decomposition-and-typed-failure-semantics/45-SUMMARY.md`
- `.planning/phases/50-rest-typed-surface-reduction-and-command-result-ownership-convergence/50-SUMMARY.md`
- `.planning/phases/50-rest-typed-surface-reduction-and-command-result-ownership-convergence/50-VERIFICATION.md`
- `.planning/phases/56-shared-backoff-neutralization-and-cross-plane-retry-hygiene/56-SUMMARY.md`
- `.planning/phases/56-shared-backoff-neutralization-and-cross-plane-retry-hygiene/56-VERIFICATION.md`

### Target Files
- `custom_components/lipro/core/command/result_policy.py`
- `custom_components/lipro/core/command/result.py`
- `custom_components/lipro/core/coordinator/runtime/command/sender.py`
- `custom_components/lipro/services/diagnostics/types.py`
- `custom_components/lipro/services/diagnostics/handlers.py`
- `tests/core/test_command_result.py`
- `tests/core/coordinator/runtime/test_command_runtime.py`
- `tests/core/test_init_service_handlers_debug_queries.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_dependency_guards.py`
- `tests/meta/test_governance_phase_history.py`

</canonical_refs>

<specifics>
## Specific Ideas

- 复用仓库既有 `reason_code` 语言，但不强迫 command-result family 直接变成 `OperationOutcome` dataclass。
- typed contract 的价值在于消除 scattered literals 与 ownership drift，而不是增加新 wrapper。
- focused guards 应验证 `result_policy.py` / `result.py` / runtime sender / diagnostics types 讲的是同一套 vocabulary。

</specifics>

<deferred>
## Deferred Ideas

- retry-budget stratification across command/runtime/MQTT
- broader telemetry/exporter alignment beyond command-result family
- repo-wide string-literal budget tightening outside touched files

</deferred>

---

*Phase: 57-command-result-typed-outcome-and-reason-code-hardening*
*Context gathered: 2026-03-22 from v1.10 seed + Phase 41/50/56 evidence + targeted command-result reread*
