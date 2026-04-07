# Phase 25 Research

**Status:** `research complete`
**Date:** `2026-03-17`
**Mode:** `route-owning parent phase for v1.3`
**Requirement:** `GOV-19`

## Executive Judgment

最优方案已经不是“选一个首相先打哪里”，而是：

1. 先用 `Phase 25` 把全部终极复审意见路由完毕。
2. 再用 `25.1 / 25.2 / 26 / 27` 分 tranche 执行。
3. 把用户裁决过的协议约束（尤其 `MD5` 登录哈希）写进真源，避免后续代理再次误判。

这是唯一能满足“所有审查意见都进入计划”且又不把一个 phase 炸成黑洞的方案。

## Route Rationale

### Phase 25.1 — Snapshot atomicity and refresh arbitration

**承接问题：**
- partial-failure 覆盖全量状态
- snapshot 路径 broad-catch / 灰区 arbitration
- refresh rejection / last-known-good / degraded semantics

**为何先做：**
- 这是最接近 correctness 事故的问题
- 它独立、边界清晰、收益高

### Phase 25.2 — Telemetry formal-surface closure and planning-truth sync

**承接问题：**
- `coordinator.client` ghost seam
- formal surface 与旧术语并存
- governance drift / derived-map honesty

**为何第二：**
- 它依赖 `25.1` 先稳定 runtime correctness story
- 它兼具代码 seam 与 planning truth 双重收口特征

### Phase 26 — Release trust chain and open-source productization hardening

**承接问题：**
- 默认 `wget | bash` 安装叙事
- provenance / signing / SBOM / attestation
- support matrix / bilingual consistency / maintainer redundancy
- version / compatibility / support policy honesty

**为何单独成相：**
- 它横跨 README、installer、release workflow、runbook、support/security/CODEOWNERS
- 若与 runtime correctness 混做，scope 一定失控

### Phase 27 — Hotspot slimming, dependency strategy and maintainability follow-through

**承接问题：**
- giant roots / pure forwarding layers
- naming residue / phase narration / historical leftovers
- dependency / version / support policy follow-through
- local persistence / observability tails
- mega-suite tests decomposition

**为何最后：**
- 它是“长期质量 10 分工程化”主战场，但不应该抢在 P0 correctness 与 trust chain 前面
- 它最容易 scope creep，必须等前几相先把主线锁住

## Explicit Exclusion: Protocol-Constrained Crypto

- reverse-engineered vendor `MD5` 登录哈希路径，不作为仓库独立的“弱密码学债”登记。
- 这条路径若无上游可替代协议，仓库层面的正确做法是：
  - 诚实记录其约束身份
  - 继续把影响限制在 protocol/auth boundary
  - 不误导性地承诺“靠重构仓库即可消灭”
- 同理，其他协议受限密码学实现只有在替代 upstream contract 被证实后，才进入执行相。

## Review-to-Phase Coverage Matrix

| Review item | Routed phase | Reason |
|-------------|--------------|--------|
| 安装/发布 trust chain 不够硬 | Phase 26 | 横跨 installer/release/docs/productization |
| snapshot partial-failure correctness | Phase 25.1 | 最直接的 correctness 风险 |
| telemetry `coordinator.client` seam | Phase 25.2 | formal-surface honesty + control/exporter closure |
| giant roots / pure forwarding layers | Phase 27 | 长线 maintainability，不宜挤进 P0 相 |
| 依赖与兼容策略偏松 | Phase 26 + 27 | 既有产品化面，也有代码 follow-through |
| `.planning/codebase/TESTING.md` 漂移 | Phase 25.2 | planning-truth honesty |
| 单维护者 / 双语 / 支持矩阵 | Phase 26 | 开源产品化主题 |
| 过渡命名 / phase 注释残留 | Phase 27 | maintainability residue |
| 次级 broad-catch / local persistence / observability tails | Phase 27 | 不是首相 blocker，但必须继续收口 |
| 测试巨石 | Phase 27 | 维护性专题，不与 P0 correctness 混做 |

## Recommended Plan Structure

### Plan 25-01 — translate final review into requirement ledger and explicit exclusions
- 把所有审查意见正式映射到 requirement ids 与 child phases。
- 写清哪些问题被排除、为何排除。
- 把 `MD5` 协议约束裁决写成 planning truth。

### Plan 25-02 — define `25.1 / 25.2 / 26 / 27` boundaries, ordering and success gates
- 在 roadmap / project 中锁定 phase 边界、先后顺序与 success criteria。
- 防止 child phases 互相踩踏或 scope overlap。

### Plan 25-03 — sync roadmap, requirements, project, state and handoff truths
- 让 active truth 与 handoff story 讲同一条新路线图。
- 更新 next focus 与 next command，避免继续误指向旧版 `Phase 25`。

### Plan 25-04 — freeze route-map validation, no-return rules and next-command handoff
- 给这张路线图补齐最小治理验证与 no-return 规则。
- 保证后续 planning/execution 不会再把 child phase 混回母相。

## Risks And Boundaries

### Risk 1 — 母相写成“把所有事都先做一点”
**控制：** `Phase 25` 只做 route planning truth，不做 child-phase 实现。

### Risk 2 — 仍有审查意见没有被正式收编
**控制：** 用 review-to-phase matrix 强制逐项映射。

### Risk 3 — 再次把协议约束误判为仓库债务
**控制：** 把 `MD5` 这条裁决写进 requirement / handoff / context。

### Risk 4 — child phases 边界重叠，后续又失焦
**控制：** `25-02` 必须明确 no-overlap / no-second-root / no-black-hole-phase 规则。

## Minimal Validation Set

- roadmap / requirements / state / project / handoff 对 `25 / 25.1 / 25.2 / 26 / 27` 讲同一条故事。
- `Phase 25` 明确覆盖全部终极复审问题，没有 silent defer。
- `MD5` 协议约束裁决已被写成真源，而不是只留在对话中。
- next command 已从旧版 `Phase 25` 切换到 `Phase 25.1` 规划入口。
