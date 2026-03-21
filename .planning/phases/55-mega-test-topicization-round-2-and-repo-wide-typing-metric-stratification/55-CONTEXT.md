# Phase 55: Mega-test topicization round 2 and repo-wide typing-metric stratification - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning
**Source:** `v1.8` roadmap route + `Phase 49/50/52` closeout evidence + targeted mega-test/typing reread

<domain>
## Phase Boundary

本 phase 处理 `TST-10` 与 `TYP-13`：继续把 API / MQTT / platform mega-tests 按 concern topicize，同时把 repo-wide typing truth 从 touched-zone no-growth 提升为 production-vs-test-literal 分层指标。

本 phase 必须保持以下真相不漂移：

1. mega-test topicization 的目标是 failure localization、更清晰的 concern grouping 与 no-regrowth named-file truth，而不是重新制造 giant meta-guard；
2. `tests/core/api/test_api_command_surface.py`、`tests/core/mqtt/test_transport_runtime.py` 与 platform mega tests 的行为 coverage 必须保持稳定，允许薄壳或 helper continuity，但不允许丢失验证主题；
3. typing metrics 必须诚实区分 production debt、test debt 与 meta-guard literal debt，production no-growth 仍是硬约束；
4. repo-wide typing stratification 不能把 test/meta 的必要字面量误叙述成 production debt，也不能借此放松 production typing discipline；
5. baseline / review / guard docs 必须与新的 test topology 和 typing buckets 同步。

本 phase 不处理 runtime/entry-root 与 helper hotspot code refactor；它只处理 test topology 与 typing metrics/governance truth。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- `tests/core/api/test_api_command_surface.py`、`tests/core/mqtt/test_transport_runtime.py` 与 platform mega suites 允许拆成多文件，但原有 concern coverage、shared fixtures 与 import stories 必须保持稳定；必要时可保留 thin shell / helper anchor。
- topicization 应优先按 concern family 划分，而不是按任意行数切片；每个新文件必须讲清一个明确主题。
- typing stratification 必须至少区分 `production_any`、`production_type_ignore`、`tests_any_non_meta`、`meta_guard_any_literals`、`tests_type_ignore` 等 bucket，且 production no-growth guard 仍是 hard fail。
- repo-wide metrics / guards 不能退回 giant regex-only magic number story；应尽量保持 named-file or named-bucket clarity。
- 若新文件 topology 影响 `FILE_MATRIX`、testing docs 或 governance guards，必须同轮同步。

### Claude's Discretion
- API/MQTT/platform 拆分顺序按 failure-localization 价值与耦合风险排序；
- mega tests 可保留 shared support helpers，只要不把 second test story 藏进无名 util；
- typing metrics 可通过现有 meta guard 扩展或新增 focused meta file 实现，只要 bucket story清晰即可。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / current truth
- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/codebase/TESTING.md`

### Prior phase anchors
- `.planning/phases/49-mega-test-topicization-and-failure-localization-hardening/49-SUMMARY.md`
- `.planning/phases/49-mega-test-topicization-and-failure-localization-hardening/49-VERIFICATION.md`
- `.planning/phases/50-rest-typed-surface-reduction-and-command-result-ownership-convergence/50-SUMMARY.md`
- `.planning/phases/52-protocol-root-second-round-slimming-and-request-policy-isolation/52-SUMMARY.md`

### Mega-test hotspots
- `tests/core/api/test_api_command_surface.py`
- `tests/core/mqtt/test_transport_runtime.py`
- `tests/platforms/test_light.py`
- `tests/platforms/test_fan.py`
- `tests/platforms/test_select.py`
- `tests/platforms/test_switch.py`
- `tests/meta/test_phase31_runtime_budget_guards.py`

### Focused verify anchors
- `tests/core/api/test_api_request_policy.py`
- `tests/core/api/test_api_transport_executor.py`
- `tests/core/mqtt/test_message_processor.py`
- `tests/core/mqtt/test_connection_manager.py`
- `tests/platforms/test_platform_entities_behavior.py`
- `tests/platforms/test_entity_base.py`
- `tests/meta/test_phase45_hotspot_budget_guards.py`
- `tests/meta/test_phase50_rest_typed_budget_guards.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_dependency_guards.py`

</canonical_refs>

<specifics>
## Specific Ideas

- API mega 适合至少拆成 command payloads、auth/response normalization、429/retry/public wrapper、misc branch coverage 四簇。
- MQTT mega 适合按 transport lifecycle、message ingress/decode、subscription sync、connection loop 四簇。
- platform megas 可按 `light/fan` 与 `select/switch` 两波拆分，并在单文件内再按 model/conversion、entity commands、setup/behavior 主题切开。
- typing metrics 应把 production debt 与 test/meta literal debt 分开；`tests/meta/test_phase31_runtime_budget_guards.py` 可升级为 stratified truth，而不是只盯一小组 touched files。

</specifics>

<deferred>
## Deferred Ideas

- no production code refactor here.
- no new global meta-guard giant file.
- no weakening of production typing discipline via “tests are noisy anyway” rhetoric.

</deferred>

---

*Phase: 55-mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification*
*Context gathered: 2026-03-21 from v1.8 route + Phase 49/50/52 evidence + mega-test/typing reread*
