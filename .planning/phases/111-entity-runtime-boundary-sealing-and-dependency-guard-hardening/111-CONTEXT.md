# Phase 111: Entity-runtime boundary sealing and dependency-guard hardening - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning
**Source:** v1.31 milestone initialization from repository-wide architecture / governance / quality audit

<domain>
## Phase Boundary

本阶段只处理 `entity / control -> runtime internals` 的 concrete bypass、对应 machine-checkable guards，以及最小充分的 changed-surface validation。

本阶段完成后，正式主线必须满足：
- entity / control 消费者只经 sanctioned runtime public surface 或 control contracts 协作；
- 任何 direct import concrete `Coordinator`、runtime concrete cast、private-state reach-through 都会被自动守卫拒绝；
- 与此次边界封印相关的 failure branches / guard branches 能在 focused validation 中暴露。

本阶段**不**处理：
- public metadata / support / security reachability 的外部托管问题；
- maintainer delegate identity 或 backup maintainer 的现实授权；
- 大范围 hotspot burn-down（留给后续 Phase 113）。
</domain>

<decisions>
## Implementation Decisions

### Boundary sealing
- `custom_components/lipro/entities/**` 不再直接 import concrete `Coordinator`，也不再通过 concrete cast 读取 runtime internals。
- entity adapters 必须改为依赖 sanctioned runtime public surface、runtime view type、或更局部的 typed contract；不能以兼容为名把 concrete runtime root 重新暴露给 entity 层。
- control surfaces 若仍存在 direct runtime concrete bypass，也必须一并收口到 sanctioned helper / contract，不得新增第二条 runtime access story。

### Guard hardening
- `tests/meta/test_dependency_guards.py` 与相关 architecture-policy checks 必须把 entity / control → `core.coordinator` direct dependency 纳入 machine-checkable 规则。
- 守卫失败信息必须能明确指出 forbidden import / forbidden cast / forbidden private-state reach-through，而不是只给模糊断言。

### Validation scope
- focused validation 必须覆盖：
  - entity runtime binding 正常工作；
  - 新 dependency guards 能抓到越界；
  - changed surface 相关 failure branches 至少覆盖 command/request guard 的关键错误路径。
- 不允许用 repo-wide line coverage 代替本阶段的 targeted proof。

### North-star constraints
- 不得引入 compat shell、second root、friend-style bypass、全局单例回退。
- 不得为通过测试而把 concrete runtime internals 重新包装成 outward public surface。
- 命名调整应朝 formal-home discoverability 前进，而不是制造新的中间术语层。

### the agent's Discretion
- 可自行决定以 `Protocol`、runtime view dataclass、或更局部 helper contract 承载 entity 所需最小能力，只要不破坏现有 outward behavior。
- 可自行决定 dependency guards 落在 `tests/meta`、`scripts/check_architecture_policy.py`、或二者组合，只要 machine-checkable 且 CI 可复用。
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / governance truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 单一主线、formal homes、runtime public surface 与禁止项总裁决。
- `.planning/PROJECT.md` — `v1.31` active route 目标与 blocker 分层。
- `.planning/ROADMAP.md` — `Phase 111` 目标、依赖与 success criteria。
- `.planning/REQUIREMENTS.md` — `ARC-28`, `GOV-71`, `TST-38` 的正式 requirement truth。
- `.planning/STATE.md` — 当前 phase / status / current route truth。
- `.planning/baseline/DEPENDENCY_MATRIX.md` — control/entity/platform 与 runtime/protocol 依赖方向裁决。
- `.planning/baseline/ARCHITECTURE_POLICY.md` — machine-checkable policy 约束基线。

### Current violating / target code
- `custom_components/lipro/entities/base.py` — 当前 entity 对 concrete `Coordinator` 的 direct import / cast 样本。
- `custom_components/lipro/runtime_types.py` — runtime-facing typed surface 现状。
- `custom_components/lipro/control/runtime_access.py` — sanctioned runtime access helper truth。
- `custom_components/lipro/control/runtime_access_types.py` — runtime read-model / view types。
- `custom_components/lipro/control/runtime_access_support_views.py` — runtime view builder / naming current state。
- `custom_components/lipro/control/developer_router_support.py` — control-side runtime access usage现状。

### Guards / quality proof
- `tests/meta/test_dependency_guards.py` — 当前 dependency guard 实现与扩展点。
- `scripts/check_architecture_policy.py` — architecture policy 自动检查入口。
- `tests/core/test_init_service_handlers_commands.py` — changed-surface command validation 现有 focused proof。
- `custom_components/lipro/services/command.py` — command/request changed surface，需在 focused validation 中纳入关键 failure branches。

### Archived predecessor evidence
- `.planning/reviews/V1_30_EVIDENCE_INDEX.md` — latest archived evidence pointer。
- `.planning/v1.30-MILESTONE-AUDIT.md` — 进入 `v1.31` 前的 closeout verdict。
</canonical_refs>

<specifics>
## Specific Ideas

- 优先修正 `custom_components/lipro/entities/base.py` 中 concrete `Coordinator` import / cast，并验证 Home Assistant entity lifecycle / update path 不回退。
- 若 `runtime_types.py` 或 `runtime_access_types.py` 已能表达 entity 所需最小 surface，应优先复用，而不是再创建一个新 outward abstraction。
- dependency guard 最少要对 `custom_components/lipro/entities/**` 与 `custom_components/lipro/control/**` 的 forbidden imports 生效。
- changed-surface tests 应尽量在定向 suite 中即可覆盖，无需依赖全仓大回归才能发现边界回流。
</specifics>

<deferred>
## Deferred Ideas

- `ARC-29` / `GOV-72` 的 formal-home discoverability 与 stale governance anchors 留到 `Phase 112`。
- `QLT-46` 的 broader hotspot burn-down 留到 `Phase 113`。
- `OSS-14` / `SEC-09` 的 public reachability honesty 与 security-surface normalization 留到 `Phase 114`。
</deferred>

*Context gathered: 2026-03-31 via v1.31 milestone initialization and terminal audit continuation*
