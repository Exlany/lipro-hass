# Phase 86: Production residual eradication and boundary re-tightening - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning

<domain>
## Phase Boundary

`Phase 86` 只消费 `Phase 85` 已冻结的 production-path route-next truth，对 `custom_components/lipro/core/anonymous_share/share_client.py` 与 `custom_components/lipro/runtime_infra.py` 做残留清零与边界收紧：

- 删除已经被审计确认为 silent compat / stale alias / bool-only bridge 的生产残留；
- 对仍然过厚但 formal-home 正确的 runtime hotspot 做 inward split / concern-local 收窄；
- 同步最小充分的测试、ledger 与 baseline truth，保证删除/拆薄结果 machine-checkable；
- 不把本 phase 扩大成 giant assurance topicization 或 milestone closeout；那些分别留给 `Phase 87` 与 `Phase 88`。

</domain>

<decisions>
## Implementation Decisions

### Compatibility cleanup
- **D-01:** `ShareWorkerClient` 继续是 anonymous-share worker client 的唯一 formal home；`Phase 86` 可以清 residual，但不能把 outward ownership 从该 formal home 挪走。
- **D-02:** `_safe_read_json()` backward-compatible alias 与 bool-only `submit_share_payload()` shim 属于已登记 delete-gate debt；本 phase 默认目标是删除它们，并让 production/tests 只承认 typed outcome-native path。
- **D-03:** 本 phase 不允许为了迁移再新增新 compat wrapper / adapter / second story；如果 caller 仍依赖旧语义，应直接改 caller 或其局部测试，而不是保留桥接层。

### Runtime hotspot decomposition
- **D-04:** `runtime_infra.py` 仍保留 shared runtime infra 的 formal-home 身份，但内部 concern 必须继续 inward split，优先切开 listener reload planning、pending task bookkeeping、listener setup/teardown 与 lock/bootstrap orchestration。
- **D-05:** inward split 只能落在 localized support/helper cluster；不得创建新的 public runtime root、helper-owned public truth、或 control-facing backdoor。
- **D-06:** 遵从契约者偏好：只在明确提升可维护性、测试定位与认知负担时才拆；不为了“拆而拆”。

### Boundary preservation
- **D-07:** `protocol / runtime / control / domain` 的 single-root / thin-adapter / localized-helper 边界是硬约束；任何重构都不得恢复 second root、package export 回流或 helper folklore。
- **D-08:** 本 phase 可以修改直接相邻的 production tests 与 review ledgers，但不承担 giant assurance suites 的 topicization，也不提前做 `Phase 88` 的全域治理 freeze。

### Verification and truth sync
- **D-09:** 计划必须覆盖 `tests/core/test_share_client_{primitives,submit}.py`、`tests/core/test_runtime_infra.py` 与匹配的 meta / ledger truth 更新，避免“代码变了但 route ledger 还旧着”。
- **D-10:** 如果某个 residual / delete gate 被关闭，`.planning/reviews/{V1_23_TERMINAL_AUDIT,FILE_MATRIX,RESIDUAL_LEDGER,KILL_LIST}.md` 与相关 baseline / guard 必须在同一 phase 内同步收口。

### the agent's Discretion
- 是否把 `runtime_infra.py` 的 inward split 落成 support module、helper cluster 或 file-local decomposition，只要 outward entry points 不漂移即可。
- 是否顺手清理 share-client 周边的小型命名/测试残留，只要它直接服务于本 phase 的 delete-gate closure。
- 允许把与 residual 删除直接相关的非阻塞小尾巴一并清掉，但不打开新的 feature scope。

</decisions>

<specifics>
## Specific Ideas

- 契约者已明确偏好：**“能提升代码质量与水平以及后续维护便利性该拆的拆，该重构的重构，如果没有提升的意义，那就没必要为了拆而拆。”**
- 契约者还要求：non-blocking residual 若有明确收益，也应在可控范围内一并清掉；不要留下临时妥协式补丁或 conversation-only carry-forward。
- `share_client.py` 当前已经具备 `safe_read_json()` / `submit_share_payload_with_outcome()` / `refresh_install_token_with_outcome()` typed path，因此 `Phase 86` 的正确方向是删除 compat 壳，而不是再重设计第三套提交语义。
- `runtime_infra.py` 当前已有明显的 helper cluster 与配套测试，说明它适合继续 inward split；但 split 后 formal home 仍应保持在 `runtime_infra.py` 这一正式入口上。

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Route truth and phase contract
- `AGENTS.md` — repo-wide north-star, boundary, verification, and workflow contract
- `.planning/PROJECT.md` — current active route, next phase handoff, and milestone-level truth
- `.planning/ROADMAP.md` — `Phase 86` scope, success criteria, and dependency on `Phase 85`
- `.planning/REQUIREMENTS.md` — `HOT-37` / `ARC-22` requirement contract
- `.planning/STATE.md` — current session continuity and next-step routing
- `tests/meta/governance_current_truth.py` — machine-readable current route constants

### Phase 85 audit outputs to consume
- `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-CONTEXT.md` — prior phase locked decisions
- `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-RESEARCH.md` — repo-wide audit findings and route rationale
- `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-01-SUMMARY.md` — baseline/docs truth sync closeout
- `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-02-SUMMARY.md` — terminal audit ledger freeze
- `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-03-SUMMARY.md` — focused guard and route-truth closeout
- `.planning/reviews/V1_23_TERMINAL_AUDIT.md` — file-level verdict and `Phase 86` production routing source
- `.planning/reviews/RESIDUAL_LEDGER.md` — active production residual inventory for `Phase 86`
- `.planning/reviews/KILL_LIST.md` — symbol-level delete gates and explicit non-targets
- `.planning/reviews/FILE_MATRIX.md` — file ownership / residual annotations for target files

### Production targets
- `custom_components/lipro/core/anonymous_share/share_client.py` — `ShareWorkerClient` formal home with remaining compat shells
- `custom_components/lipro/runtime_infra.py` — formal runtime-infra home with lingering hotspot density
- `custom_components/lipro/core/anonymous_share/share_client_flows.py` — existing typed submit/refresh flow collaborators
- `custom_components/lipro/core/anonymous_share/share_client_support.py` — token/payload helper contracts used by `ShareWorkerClient`

### Adjacent tests and guards
- `tests/core/test_share_client_primitives.py` — current JSON/token primitive coverage
- `tests/core/test_share_client_submit.py` — current submit/outcome compatibility coverage
- `tests/core/test_runtime_infra.py` — runtime-infra ownership and listener/reload tests
- `tests/meta/test_phase85_terminal_audit_route_guards.py` — audit-routed production targets must stay explicit
- `tests/meta/test_phase72_runtime_bootstrap_route_guards.py` — runtime route guard family that should not regress

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `custom_components/lipro/core/anonymous_share/share_client_flows.py` — already owns typed submit / refresh / JSON-reading flow logic; lets `ShareWorkerClient` delete compat shells without inventing new orchestration homes.
- `custom_components/lipro/core/anonymous_share/share_client_support.py` — centralized payload/token extraction helpers; useful for keeping cleanup local to the existing anonymous-share family.
- `tests/core/test_share_client_support.py` and topicized share-client suites — existing test scaffold makes it practical to delete bool/alias seams and re-anchor assertions on typed outcomes.
- `tests/core/test_runtime_infra.py` — current hotspot already has focused unit coverage around listener/reload behavior, so inward split can remain behavior-preserving.

### Established Patterns
- Formal homes stay stable while support/flow/helper modules absorb inward decomposition; this is already the repo’s favored refactor style.
- Typed outcome surfaces are preferred over bool-returning bridges; compat shells are allowed only as explicit temporary delete-gate debt.
- Review ledgers (`FILE_MATRIX`, `RESIDUAL_LEDGER`, `KILL_LIST`, audit docs) are part of the implementation contract, not optional afterthoughts.

### Integration Points
- Anonymous-share service / diagnostics / tests consume `ShareWorkerClient`; any compat shell removal must be reflected in those callers or their topicized tests.
- `runtime_infra.py` is consumed by integration/control setup paths; inward split must preserve the same top-level entry points used by existing runtime/control wiring.
- `Phase 86` closeout must feed directly into `Phase 87`/`88`; therefore route updates must keep the remaining production truth explicit and machine-readable.

</code_context>

<deferred>
## Deferred Ideas

- `tests/core/api/test_api_diagnostics_service.py`、`tests/core/api/test_protocol_contract_matrix.py` 与 `tests/core/coordinator/runtime/test_mqtt_runtime.py` 的 giant-suite topicization 继续留给 `Phase 87`。
- 全域 governance sync、quality-proof closeout 与 milestone freeze 留给 `Phase 88`。
- 任何新的 feature capability、public API redesign、或跨 plane 的大规模 architecture reshaping 都不属于 `Phase 86`。

</deferred>

---

*Phase: 86-production-residual-eradication-and-boundary-re-tightening*
*Context gathered: 2026-03-27*
