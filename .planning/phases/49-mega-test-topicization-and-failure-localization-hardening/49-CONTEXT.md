# Phase 49: Mega-test topicization and failure-localization hardening - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning
**Source:** `Phase 46` audit + `Phase 47/48` closeout + targeted mega-test hotspot re-read

<domain>
## Phase Boundary

本 phase 只处理 `Phase 46` 已正式路由到 `49 -> 50` 的测试拓扑与失败定位债，不改变业务行为真相，也不借测试重构偷渡新的架构故事。

聚焦四类对象：

1. `tests/meta/test_governance_closeout_guards.py` 仍承载多批次 phase continuity / promoted assets / roadmap consistency / review truth 断言，失败时需要人工在巨石文件内二次定位；
2. `tests/core/test_coordinator.py` 与 `tests/core/test_diagnostics.py` 仍带有 runtime facet 交织与 topic 密度偏高的问题；
3. `tests/platforms/test_update.py` 已覆盖 OTA / manifest / certification / install flow / cache arbitration 等多个 concern，但仍是 platform 侧 megatest；
4. `tests/test_coordinator_public.py`、`tests/test_coordinator_runtime.py` 这类 stray top-level tests 需要回到更自然的 domain home，并让参数化 / assertion id 直接报告真实 concern、phase、doc 或 runtime facet。

本 phase 的目标是提升失败定位与维护可读性，而不是降低 coverage、复制第二套 truth、或把 execution-trace 文档重新合法化成长期治理真源。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- `tests/meta/test_governance_closeout_guards.py` 的拆分必须保持治理诚实：phase / doc / token / promoted asset 仍需 machine-checkable，不能因切分而放松断言。
- runtime / diagnostics / update platform 测试的 topicization 只能改善文件粒度、夹具归属、断言命名与失败摘要；不得借机改变正式 public surface 或实际业务行为。
- stray top-level tests 必须进入更自然的 domain home；若移动文件，需同步更新 file-matrix / import-path / pytest discovery 相关真相，不能留下第二个影子入口。
- assertion ids、parameterization labels、helper names 必须以实际 concern 为中心，优先暴露 `(phase, doc, token)`、runtime facet、platform concern，而不是抽象的 case 序号。
- 本 phase 若需触碰 `.planning/reviews/FILE_MATRIX.md`、baseline 或 closeout guards，只能做与测试 topicization / truth sync 直接相关的最小更改。

### Claude's Discretion
- governance megaguards 可拆成同文件内按 concern family 的 test class / helper cluster，也可拆分到多个 meta test 文件；只要最终 failure-localization 明显提升且 truth 不漂移即可。
- runtime megatests 可通过新增 focused test modules、抽取共享 fixtures/helpers、移动 stray tests 到 `tests/core/` 子树等方式收敛；选择最少扰动且最清晰的 home。
- update-platform megatests 可按 parser / arbitration / entity install flow / certification policy concern 切分，但无需为了“切分”而制造过细碎文件。
- 允许在测试中引入更明确的 helper factory / parametrized ids / assertion messages，但不要引入新的测试框架、插件或额外依赖。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / governance truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 单主链、边界与治理法则
- `AGENTS.md` — formal root / truth order / execution-trace 与 promoted asset 约束
- `.planning/PROJECT.md` — `v1.7` 当前 follow-up route 与默认入口
- `.planning/ROADMAP.md` — `Phase 49` / `Phase 50` 的正式目标与 success criteria
- `.planning/REQUIREMENTS.md` — `TST-09` / `QLT-17` traceability truth
- `.planning/STATE.md` — 当前 next action 与 phase continuity truth

### Audit and prior-phase anchors
- `.planning/phases/39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition/39-SUMMARY.md` — mega-test decomposition 的前序治理背景
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-AUDIT.md` — 全仓审计结论与 hotspot verdict
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-SCORE-MATRIX.md` — quality / architecture scoring 与 phase routing rationale
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-REMEDIATION-ROADMAP.md` — `Phase 49` 原始 remediation route
- `.planning/phases/47-continuity-contract-governance-entrypoint-compression-and-tooling-discoverability/47-SUMMARY.md` — continuity/tooling closeout 基线
- `.planning/phases/48-runtime-access-and-formal-root-hotspot-decomposition-without-public-surface-drift/48-SUMMARY.md` — current-story 最近 closeout truth

### Test hotspots
- `tests/meta/test_governance_closeout_guards.py`
- `tests/core/test_coordinator.py`
- `tests/core/test_diagnostics.py`
- `tests/platforms/test_update.py`
- `tests/test_coordinator_public.py`
- `tests/test_coordinator_runtime.py`
- `tests/platforms/test_update_task_callback.py`

### Review / baseline truth that may need sync
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- `.planning/reviews/README.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/PUBLIC_SURFACES.md`

### Verification suites
- `tests/meta/test_governance_closeout_guards.py`
- `tests/meta/test_dependency_guards.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/core/test_coordinator.py`
- `tests/core/test_diagnostics.py`
- `tests/platforms/test_update.py`
- `tests/test_coordinator_public.py`
- `tests/test_coordinator_runtime.py`
- `scripts/check_file_matrix.py`

</canonical_refs>

<specifics>
## Specific Ideas

- governance closeout guards 可按 continuity / promoted assets / phase-complete truth / shipped-baseline archive / current route truth 等 family 分组，必要时拆到多个文件；
- `tests/core/test_coordinator.py` 可按 service/runtime components、entity lifecycle、update flow 再细化成更自然的 topic module；
- `tests/core/test_diagnostics.py` 可按 config-entry diagnostics、device diagnostics、redaction helper 等 concern 收束，减少单文件跨 topic 跳转；
- `tests/platforms/test_update.py` 适合按 parser/arbitration、entity state/install flow、certification policy、version comparison 等 concern 切分；
- 若 `tests/test_coordinator_public.py` 与 `tests/test_coordinator_runtime.py` 迁移到 `tests/core/` 或其子树，应同时更新 `FILE_MATRIX` 与相关命令/文档锚点；
- failure-localization 不只体现在文件拆分，还应体现在 `pytest.param(..., id=...)`、断言消息、helper 命名与 fixture home 上。

</specifics>

<deferred>
## Deferred Ideas

- 不在本 phase 内改变产品代码或协议/runtime/control formal roots；
- 不在本 phase 内执行 `Phase 50` 的 REST typed-surface reduction、command/result ownership convergence、diagnostics auth-error duplication closure；
- 不把 execution-trace 资产自动 promoted；promotion 仍只针对 closeout evidence；
- 不为测试切分引入新依赖、snapshot framework 或复杂测试生成器。

</deferred>

---

*Phase: 49-mega-test-topicization-and-failure-localization-hardening*
*Context gathered: 2026-03-21 after Phase 48 completion*
