# Phase 56: Shared backoff neutralization and cross-plane retry hygiene - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning
**Source:** `v1.9` milestone seed + `Phase 52/54/55` closeout evidence + targeted backoff/routing reread

<domain>
## Phase Boundary

本 phase 只处理 `RES-13 / ARC-09 / GOV-40`：把 generic exponential backoff primitive 从 `request_policy.py` 的跨平面 utility 泄漏状态迁到 neutral shared home，同时保持以下 truth 不漂移：

1. `RequestPolicy` 继续只拥有 API-specific `429` / busy / pacing truth；
2. command-result polling、runtime command verification 与 MQTT setup backoff 只共享 primitive，不共享 policy owner；
3. `core/utils/backoff.py` 只是 neutral helper home，而不是新的 cross-plane strategy root；
4. baseline / review / promoted evidence / meta guards 必须同步关闭 residual，而不是只在代码层面“悄悄修掉”。

本 phase 不处理 command-result typed outcome endgame，也不统一 command/runtime/MQTT 的 retry semantics；这些若要继续推进，只能在后续 phase 中以显式 requirement 处理。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- `compute_exponential_retry_wait_time()` 必须迁到 neutral shared helper home，且非 API caller 不得继续从 `request_policy.py` import 它。
- `RequestPolicy` 继续保留 `compute_rate_limit_wait_time()`、`handle_rate_limit()`、busy retry 与 CHANGE_STATE pacing formal truth；不得被降格成“只是 wrapper”。
- `request_policy_support.py` 仍可作为 API-local support seam，但 generic backoff primitive 真源不能继续留在这里。
- `result_policy.py`、runtime `RetryStrategy` 与 `MqttSetupBackoff` 只允许共享 neutral primitive；各自的 attempt budget、min/max、jitter、delay clipping 与 retry semantics 继续留在 plane-local homes。
- governance truth 必须明确写出 residual 已关闭，且 `56-SUMMARY.md` / `56-VERIFICATION.md` 要进入 promoted assets。

### Claude's Discretion
- neutral helper home 应落在 `core/utils/backoff.py` 还是更窄的 utility file；只要名称/位置诚实且不会演化成万能 retry manager 即可。
- focused tests 可通过 unit assertions + meta guards 实现，只要能 machine-check non-API import direction 与 residual closeout truth 即可。

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
- `.planning/reviews/V1_9_MILESTONE_SEED.md`

### Prior Phase Evidence
- `.planning/phases/52-protocol-root-second-round-slimming-and-request-policy-isolation/52-SUMMARY.md`
- `.planning/phases/52-protocol-root-second-round-slimming-and-request-policy-isolation/52-VERIFICATION.md`
- `.planning/phases/54-helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families/54-SUMMARY.md`
- `.planning/phases/54-helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families/54-VERIFICATION.md`
- `.planning/phases/55-mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification/55-SUMMARY.md`
- `.planning/phases/55-mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification/55-VERIFICATION.md`

### Target Files
- `custom_components/lipro/core/utils/backoff.py`
- `custom_components/lipro/core/api/request_policy.py`
- `custom_components/lipro/core/api/request_policy_support.py`
- `custom_components/lipro/core/command/result_policy.py`
- `custom_components/lipro/core/coordinator/runtime/command/retry.py`
- `custom_components/lipro/core/mqtt/setup_backoff.py`
- `tests/core/api/test_api_request_policy.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_dependency_guards.py`

</canonical_refs>

<specifics>
## Specific Ideas

- 用 `core/utils/backoff.py` 对齐现有 `core/utils/retry_after.py`：一个是 neutral Retry-After parse，一个是 neutral exponential backoff primitive。
- `request_policy.py` 内部若仍需 exponential wait，只应通过 private import 使用，而不是重新导出 public helper。
- residual closeout 需要同时改 `PUBLIC_SURFACES`、`DEPENDENCY_MATRIX`、`VERIFICATION_MATRIX`、`RESIDUAL_LEDGER` 与 `KILL_LIST`。

</specifics>

<deferred>
## Deferred Ideas

- command-result typed outcome / reason-code endgame
- retry budget stratification across command/runtime/MQTT
- further production `Any` contraction unrelated to the active residual family

</deferred>

---

*Phase: 56-shared-backoff-neutralization-and-cross-plane-retry-hygiene*
*Context gathered: 2026-03-22 from v1.9 seed + Phase 52/54/55 evidence + targeted backoff reread*
