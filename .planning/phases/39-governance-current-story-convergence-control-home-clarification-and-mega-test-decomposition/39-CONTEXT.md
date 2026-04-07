# Phase 39: Governance Current-Story Convergence, Control-Home Clarification, and Mega-Test Decomposition - Context

**Gathered:** 2026-03-19
**Status:** Executed and completed (2026-03-19)
**Source:** PRD Express Path (`39-PRD.md`)

<domain>
## Phase Boundary

本 phase 只处理 current-story convergence、control/services formal role clarification、dead shell / naming residual retirement、fixture/replay authority rename、governance + mega-test topicization。

本 phase 不重开已关闭的 protocol/runtime residual，也不另建根、事件总线、DI 容器或兼容壳。
</domain>

<decisions>
## Implementation Decisions

### Governance Truth
- `ROADMAP / REQUIREMENTS / STATE / PROJECT` 必须共同承认当前主叙事已进入 `v1.4` sustainment / fresh-audit continuation。
- `REQUIREMENTS` coverage/traceability 区块必须可被算术校验，不允许出现人工抄写错误。
- `STATE` 的 current milestone / current mode / recommended next command / session continuity 不得自相矛盾。

### Documentation Truth
- `docs/developer_architecture.md` 必须重写为 current-topology 文档，不再携带 `Version 4.3` / `Phase 17` 一类 stale metadata。
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` 只定义终态，但必须把 control-home、current priority 与目录映射更新到当前 truth。

### Control Plane Truth
- `custom_components/lipro/control/` 是 formal control-plane home。
- `custom_components/lipro/services/` 只承载 service declaration / adapter / handler helper，不再被描述为 legacy carrier。
- 根层 `__init__.py`、`diagnostics.py`、`system_health.py` 继续保持 thin adapters。

### Residual Retirement
- `custom_components/lipro/core/protocol/compat.py` 若无人引用，直接删除。
- `get_device_list.envelope.json` 现作为唯一 authority asset 命名保留；phase 的目标是消灭双命名期与 stale compat/wrapped folklore，而不是再次改名。
- replay manifests / readmes / tests / guards 一并迁移，不能保留双命名期。

### Test Topology
- `tests/core/test_device.py`、`tests/core/mqtt/test_mqtt.py`、`tests/flows/test_config_flow.py`、`tests/core/test_anonymous_share.py` 继续按专题拆分。
- `tests/meta/test_governance_closeout_guards.py` 等治理巨石应优先从 stale prose 断言迁向 structured anchors；必要时顺带拆分。

### Claude's Discretion
- 具体的测试文件命名、plan wave 切分、helper/support 模块布局，由保持最小认知负担的方案决定。
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Governance and authority
- `.planning/ROADMAP.md` — phase route, milestone story, phase 39 slot
- `.planning/REQUIREMENTS.md` — current requirement traceability and coverage blocks
- `.planning/STATE.md` — current mode, read order, next command, roadmap evolution
- `.planning/PROJECT.md` — v1.3 closeout vs v1.4 seed story
- `.planning/reviews/FILE_MATRIX.md` — file ownership truth for control/services/protocol/tests
- `.planning/reviews/RESIDUAL_LEDGER.md` — residual disposition truth
- `.planning/reviews/KILL_LIST.md` — delete-gated residue history
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` — promoted phase artifact contract

### Architecture docs
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — north-star planes, roots, directory mapping
- `docs/developer_architecture.md` — contributor-facing current topology map

### Code and fixtures
- `custom_components/lipro/control/`
- `custom_components/lipro/services/`
- `custom_components/lipro/core/protocol/compat.py`
- `custom_components/lipro/services/diagnostics/__init__.py`
- `tests/fixtures/api_contracts/README.md`
- `tests/fixtures/api_contracts/get_device_list.envelope.json`
- `tests/fixtures/protocol_replay/rest/*.json`
- `tests/meta/test_protocol_replay_assets.py`
- `tests/core/api/test_protocol_contract_matrix.py`

### Mega-test suites
- `tests/core/test_device.py`
- `tests/core/mqtt/test_mqtt.py`
- `tests/flows/test_config_flow.py`
- `tests/core/test_anonymous_share.py`
- `tests/meta/test_governance_closeout_guards.py`
- `tests/meta/test_governance_phase_history*.py`
</canonical_refs>

<specifics>
## Specific Ideas

- `get_device_list.envelope.json` 成为唯一 authority asset；相关 replay/tests/readmes/guards 全部同步
- 新增 requirement IDs：`GOV-32`, `DOC-03`, `CTRL-08`, `RES-09`, `TST-07`
- 治理守卫增加 coverage math / authority doc freshness / control-home component-set assertions
</specifics>

<deferred>
## Deferred Ideas

- 进一步大规模拆薄 `LiproProtocolFacade` / `Coordinator` 的生产代码，如果没有 clear seam，则不在本 phase 强行重构。
- 新里程碑归档动作（例如 `complete-milestone v1.4`）不在本 phase 内自动触发。
</deferred>

---

*Phase: 39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition*
*Context gathered: 2026-03-19 via PRD Express Path*
