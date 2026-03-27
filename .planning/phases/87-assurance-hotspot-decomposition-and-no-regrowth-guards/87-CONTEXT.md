# Phase 87: Assurance hotspot decomposition and no-regrowth guards - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning
**Source:** `$gsd-next` after `Phase 86 complete` + `Phase 85` audit verdict + current governance truth

<domain>
## Phase Boundary

本 phase 只处理 `v1.23` 已正式登记的 assurance hotspots，目标是把 giant / thick test roots 继续按真实 concern family 切薄，让 failure-localization、suite ownership 与 no-regrowth guard 都回到可维护状态。

范围仅限以下 routed hotspots 及其直接相关的守卫/文档同步：

1. `tests/core/api/test_api_diagnostics_service.py`
2. `tests/core/api/test_protocol_contract_matrix.py`
3. `tests/core/coordinator/runtime/test_mqtt_runtime.py`
4. 与上述 topicization 直接绑定的 focused guards、verification/file-matrix truth、最小必要 shared support helpers

本 phase 不处理生产代码架构迁移，不重新打开 `Phase 86` 已关闭的 production residual，也不把 assurance 拆分扩张为新的 capability phase。

</domain>

<decisions>
## Implementation Decisions

### Scope Lock
- **D-01:** `HOT-38` / `TST-27` 只收敛 audit 已点名的 3 个 assurance hotspots；任何新增产品能力、协议边界重写、runtime 正式根调整都属于越界。
- **D-02:** topicization 的目标是降低 giant truth-carrier 密度与 triage 成本，不是为了“拆而拆”；若某块 concern 已足够清晰，可保留在现有 home。
- **D-03:** 所有拆分必须复用现有 test tree 的自然 home，不得为了局部整洁再造第二套测试故事线、隐藏入口或新的 mega-suite。

### Hotspot-Specific Direction
- **D-04:** `tests/core/api/test_api_diagnostics_service.py` 应按真实 API concern 拆分，至少把 `OTA/info fallback`、`sensor/history & command result`、`user-cloud/raw-body` 这类彼此可独立定位的族群从 giant root 中解耦出来。
- **D-05:** `tests/core/api/test_protocol_contract_matrix.py` 应按 boundary family / replay authority / unified-root smoke 等 concern topicize；planner 可以保留 thin shell，但不能再让一个单文件承载所有 north-star protocol contract truth。
- **D-06:** `tests/core/coordinator/runtime/test_mqtt_runtime.py` 应按 runtime facet 拆分，例如 `initialization & DI`、`connection/reconnect`、`message handling/dedup`、`notification/reset` 等；共享 fixture/support 应 inward 收敛到同目录 helper home。

### Guard and Truth Discipline
- **D-07:** 每个被切薄的 hotspot 都必须有 focused guard 或 targeted regression 锁住其最终 topology；不接受“文件拆了但 guard 还靠口头记忆”的半闭环。
- **D-08:** 若 topicization 触及 `FILE_MATRIX`、`VERIFICATION_MATRIX`、review ledgers 或 route guards，只能做与 hotspot topology / verification entry 直接相关的最小同步，不得顺手改写无关 current story。
- **D-09:** thin shell 可以存在，但只允许做 topicized suite 的显式聚合入口，不能重新成为 giant truth-carrier。

### the agent's Discretion
- **D-10:** 具体拆分粒度、文件命名、是否保留原根文件作为 thin shell、support helper 的最小抽取范围，由 researcher/planner 以“最少扰动、最大定位收益”为准则裁定。
- **D-11:** focused guards 可以落在现有 `tests/meta` 家族，也可以贴近 topical suite 新增更小 guard；前提是维护者能从失败面直接定位具体 concern。
- **D-12:** 若某些断言更适合通过 `pytest.param(..., id=...)`、helper 工厂命名或 assertion message 增强来提升定位，而不是继续拆文件，允许采用该策略。

</decisions>

<specifics>
## Specific Ideas

- `test_api_diagnostics_service.py` 当前同时承载 OTA row helper、V1/V2 fallback、degraded outcome、sensor history、query_user_cloud、command result external-boundary fixture 等多个 story，约 `622` 行；适合至少分为 2–4 个 topical suites。
- `test_protocol_contract_matrix.py` 当前混合 unified protocol root smoke、MQTT facade telemetry、REST/MQTT boundary decoders、replay manifest authority、phase-1 contract fixture reuse，约 `627` 行；宜以 `boundary decoder` / `facade runtime` / `fixture authority` 三大族群切开。
- `test_mqtt_runtime.py` 当前覆盖 constructor DI、connect/reconnect、message handling、disconnect notification、reset/backoff gate 等，约 `644` 行；共享依赖注入模式已很明显，适合先抽 support helper，再按 runtime facet 切成多个 focused modules。
- 优先复用仓库中已存在的模式：`tests/core/test_share_client.py`、`tests/meta/test_public_surface_guards.py`、`tests/meta/test_dependency_guards.py` 等 thin shell/topicized suite 形态，以及 `tests/core/coordinator/runtime/test_command_runtime_support.py` 这类 support-only helper home。
- `Phase 87` 应把 routed hotspot 从“audit verdict”推进到“可执行的 topicized topology + no-regrowth guard”；不要把 `Phase 88` 的治理冻结工作提前吞进来。

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star and current governance truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 单主链、边界与 assurance 不得反向定义架构真相的总裁决
- `AGENTS.md` — formal-root / truth-order / docs-sync / verification 约束
- `.planning/PROJECT.md` — 当前 active route 与 default next command
- `.planning/ROADMAP.md` — `Phase 87` goal / requirements / success criteria
- `.planning/REQUIREMENTS.md` — `HOT-38` / `TST-27` traceability truth
- `.planning/STATE.md` — `Phase 86 complete` 后的 current mode 与 next-step truth

### Audit routing and residual truth
- `.planning/reviews/V1_23_TERMINAL_AUDIT.md` — `Phase 85` 审计对 assurance hotspots 的正式 verdict
- `.planning/reviews/RESIDUAL_LEDGER.md` — active routed residual truth（仅 giant assurance carriers 仍 route next）
- `.planning/reviews/KILL_LIST.md` — delete gate / non-delete routing policy，明确 giant assurance carriers 不是 file-kill target
- `.planning/reviews/FILE_MATRIX.md` — file ownership 与 future topology sync truth
- `.planning/baseline/VERIFICATION_MATRIX.md` — required runnable proof 与 phase 85/86/87 continuity constraints

### Prior-phase research and reusable planning patterns
- `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-RESEARCH.md` — `Phase 87` routed hotspots、拆分方向与不该做的事
- `.planning/phases/49-mega-test-topicization-and-failure-localization-hardening/49-CONTEXT.md` — mega-test topicization 的已验证上下文模式
- `.planning/phases/49-mega-test-topicization-and-failure-localization-hardening/49-RESEARCH.md` — thin-root / topicized suites / focused guard 的成熟研究模板

### Hotspot files
- `tests/core/api/test_api_diagnostics_service.py` — diagnostics API assurance hotspot
- `tests/core/api/test_protocol_contract_matrix.py` — protocol contract matrix hotspot
- `tests/core/coordinator/runtime/test_mqtt_runtime.py` — MQTT runtime hotspot

### Existing reusable test-topology patterns
- `tests/core/test_share_client.py` — thin shell for topicized suites
- `tests/core/test_share_client_support.py` — support-only helper home pattern
- `tests/core/coordinator/runtime/test_command_runtime.py` — topicized runtime suite shell
- `tests/core/coordinator/runtime/test_command_runtime_support.py` — runtime support helper pattern
- `tests/meta/test_public_surface_guards.py` — topicized meta guard shell pattern
- `tests/meta/test_dependency_guards.py` — focused guard shell pattern

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/core/api/conftest.py`：已提供 topicized API suites 的共享导入 home，可承接 diagnostics/protocol split 后的公共 imports。
- `tests/core/coordinator/runtime/test_command_runtime_support.py`：展示了同目录 support helper 的收敛方式，适合作为 `test_mqtt_runtime.py` 拆分后的参考。
- `tests/core/test_share_client.py` + `tests/core/test_share_client_support.py`：展示了 `thin shell + sibling support/topic suites` 的轻量组合模式。

### Established Patterns
- 薄根文件允许存在，但应只作为 import 聚合入口，而不是继续堆积断言。
- shared helper 应 inward 收敛到 `*_support.py` 或同目录 fixture home，而不是散落到多层随机 util。
- focused guard 倾向用更小的 meta suites 锁住 topology / truth，而不是再造一个更大的治理总表。

### Integration Points
- 拆分 hotspots 后，需同步更新 `.planning/reviews/FILE_MATRIX.md` 与 `.planning/baseline/VERIFICATION_MATRIX.md` 中的 suite home / runnable proof。
- 若新增或替换 thin shell，需要确认 `tests/meta/test_public_surface_guards.py`、`tests/meta/test_dependency_guards.py`、`scripts/check_file_matrix.py --check` 仍承认同一条 topology truth。
- `Phase 88` 会消费 `Phase 87` 的最终 topology 与质量证明，因此 `Phase 87` 计划必须显式产出可验证的 suite map，而不是仅靠摘要描述。

</code_context>

<deferred>
## Deferred Ideas

- 不在本 phase 内触碰生产代码 formal root、protocol/runtime/control boundary 或任何 vendor payload normalization 逻辑。
- 不把 `Phase 88` 的 milestone freeze / governance closeout / full-quality proof 提前并入 `Phase 87`。
- 不引入新的测试依赖、snapshot 框架、生成器工具或大规模 fixture 重写。
- 不把 giant assurance carriers 误叙述为 file-delete target；本 phase 的目标是 topicization / thin-root / guard strengthening。

</deferred>

---

*Phase: 87-assurance-hotspot-decomposition-and-no-regrowth-guards*
*Context gathered: 2026-03-27 after Phase 86 completion*
