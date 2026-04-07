# Phase 25 Context

**Phase:** `25 Quality-10 remediation master plan and execution routing`
**Milestone seed:** `v1.3 route-owning parent phase`
**Date:** `2026-03-17`
**Status:** `Ready for planning`
**Source:** `v1.3-HANDOFF.md` + 2026-03-17 repo-wide architect review + user arbitration on all review findings

## Why Phase 25 Exists

契约者要求的不再是“只规划一个首相”，而是把终极复审里的**全部真实问题**都制度化，不能遗漏、不能口头递延、不能让任何问题继续停留在对话历史里。

因此 `Phase 25` 被提升为 **总计划母相**：

- 它本身不负责执行代码重构主线
- 它负责把全部审查意见路由成 `25.1 / 25.2 / 26 / 27`
- 它负责定义哪些是本仓库 debt，哪些只是上游协议约束
- 它负责锁定边界、顺序、success gates 与 no-return rules

## Goal

1. 把终极复审的全部 P0 / P1 / P2 问题路由到明确的 child phase。
2. 给 `25.1 / 25.2 / 26 / 27` 锁定不重叠的执行边界，避免第一阶段失焦。
3. 把用户的裁决（如 `MD5` 登录哈希属于逆向 API 约束，而非仓库弱密码学债）写成 planning truth。
4. 同步 `ROADMAP / REQUIREMENTS / PROJECT / STATE / v1.3-HANDOFF`，确保下一位执行者不必再重新仲裁路线图。

## Routed Review Matrix

- `P0` 安装/发布 trust chain 不够硬 → `Phase 26`
- `P0` 设备快照 partial-failure correctness → `Phase 25.1`
- `P0` telemetry `coordinator.client` ghost seam → `Phase 25.2`
- `P1` giant roots / pure forwarding layers → `Phase 27`
- `P1` dependency / compatibility / support strategy → `Phase 26` + `Phase 27`
- `P1` governance drift / derived-map honesty → `Phase 25.2`
- `P1` 单维护者 / 双语 / 产品化不足 → `Phase 26`
- `P2` naming residue / phase narration / broad-catch tails / local persistence-observability follow-through / test megafiles → `Phase 27`

## Decisions (Locked)

- `Phase 25` 只负责**母相路由与真源同步**，不把 child phases 的实现硬塞回本相。
- `Phase 25.1` 只吃 snapshot correctness；`Phase 25.2` 只吃 telemetry + truth sync；`Phase 26` 吃 trust chain + productization；`Phase 27` 吃 hotspot / maintainability。
- reverse-engineered vendor `MD5` 登录哈希路径按当前认知属于**上游协议约束**，不是仓库内部“弱密码学债”；只有验证到替代协议时才升级为执行目标。
- `AES-ECB` / `SHA1` 一类协议受限实现同样按“协议约束 + 边界隔离 + 诚实记录”处理，除非确认可替代 upstream contract。
- `.planning/codebase/*` 继续只是 derived collaboration maps；它们可以被刷新，但不得反向成为 authority source。

## Non-Negotiable Constraints

- 不把 `25.1 / 25.2 / 26 / 27` 再混成一个“万能债务相”。
- 不允许用 second root / global bus / heavy DI 去“顺手”解决 hotspot 问题。
- 不允许把用户已明确裁决过的协议约束再错误登记成仓库 debt。
- 任何未纳入 child phase 的问题都必须显式说明为何排除，不能 silent defer。

## Canonical References

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 北极星主链与正式边界
- `.planning/v1.3-HANDOFF.md` — post-closeout handoff 与新的 route order
- `.planning/ROADMAP.md` — `25 / 25.1 / 25.2 / 26 / 27` 真源
- `.planning/REQUIREMENTS.md` — routed requirement ledger
- `.planning/STATE.md` — 当前 active truth 与 next command
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` — release trust-chain/productization 现状
- `README.md` / `README_zh.md` — installer / public-entry surfaces
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py` — snapshot correctness hotspot evidence
- `custom_components/lipro/control/telemetry_surface.py` — telemetry seam evidence
- `custom_components/lipro/core/api/client.py` / `custom_components/lipro/core/coordinator/coordinator.py` — giant-root / forwarding evidence
- `tests/core/test_init.py` / `tests/meta/test_governance_guards.py` — mega-suite evidence

## Explicit Exclusions

- 本 phase 不直接执行 `25.1 / 25.2 / 26 / 27` 的代码改动。
- 本 phase 不把 vendor-defined `MD5` 登录哈希路径当作独立 crypto-hardening deliverable。
- 本 phase 不提前替 `26 / 27` 写实现级 PLAN，只负责把路线图与 requirement ownership 钉死。
