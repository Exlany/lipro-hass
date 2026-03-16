---
gsd_state_version: 1.0
milestone: v1.2
milestone_name: Host-Neutral Core & Replay Completion
status: active
last_updated: "2026-03-16T09:15:00Z"
progress:
  total_phases: 5
  completed_phases: 3
  total_plans: 15
  completed_plans: 10
---

# Project State

## Project Reference

See: `.planning/PROJECT.md`

**Current milestone:** `v1.2 Host-Neutral Core & Replay Completion`
**Core value:** 在不破坏 `LiproProtocolFacade` / `Coordinator` 单一正式主链的前提下，把 host-neutral nucleus、headless proof、remaining boundary/replay family 收口与 observability/governance follow-through 推进成下一轮正式能力。
**Current mode:** `Phase 20 complete`；`Phase 18-20` 已执行完成，当前下一步是 `Phase 21 Replay / Observability / Exception Hardening`。

## Current Position

- `v1.0` 已归档到 `.planning/MILESTONES.md` 与 `.planning/milestones/v1.0-*.md`
- `v1.1` 已完成全部计划执行：`15 phases / 58 plans` 全绿落表
- `Phase 7.1` 已完成：boundary inventory / decoder skeleton / representative REST+MQTT pipeline / replay-ready fixtures / governance handoff
- `Phase 7.2` 已完成：architecture policy baseline、shared policy helpers、architecture script、meta guards refactor、CI fail-fast ordering 与 verification evidence 已落地
- `Phase 7.3` 已完成：exporter formal home、真实运行信号、consumer convergence、black-box evidence 与治理回写均已落地
- `Phase 7.4` 已完成：authority-indexed replay manifests、deterministic driver、REST/MQTT replay assertions、replay run summary 与 meta guards 已形成 assurance 资产
- `Phase 7.5` 已完成：governance matrix sync、`V1_1_EVIDENCE_INDEX.md`、`07.5-SUMMARY.md`、residual/delete gate closeout arbitration 已落地
- `Phase 8` 已完成：AI debug evidence pack formal home、唯一 exporter entrypoint、integration/meta guards 与 governance handoff 已全部落地
- `Phase 9` 已完成：production residual closure 与 legacy test convergence addendum 已落地；API mega-test、runtime/platform/integration tests 与治理文档已对齐到正式架构
- `Phase 10` 已完成：boundary family 与 canonical contracts 已正式落地，`AuthSessionSnapshot` 成为 formal auth/session truth，`core/__init__.py` 已不再导出 `Coordinator`
- `Phase 11` 已完成：control router formalization、wiring compat demotion、REST/runtime surface convergence、runtime-access hardening、entity/platform truth convergence、firmware-update hotspot slimming 与 governance/open-source coherence 已统一收口
- `Phase 12` 已完成：typed surface convergence、compat narrowing、hotspot decomposition 与 contributor-facing governance hygiene 已全部落地并通过治理回写
- `Phase 13` 已完成：explicit domain surface、runtime/status hotspot boundary decomposition 与 governance guard hardening 已全部落地并通过治理回写
- `Phase 14` 已完成：`CoordinatorProtocolService`、schedule residual closeout、`status_fallback.py` / `developer_router_support.py` helper-home extraction 与 governance truth consolidation 已全部落地并通过治理回写
- `Phase 15` 已完成：developer feedback upload contract、governance/source-path truth、README/support/version truth、support hotspot typing narrowing 与 tooling/residual arbitration 已全部落地并通过治理回写
- `Phase 16` 已完成：post-audit truth alignment、toolchain/DX truth、control/service contract、protocol/runtime hotspot decomposition、domain/entity/OTA rationalization 与 test-layer/docs follow-through `6 plans / 3 waves` 已全部落地
- `Phase 17` 已完成：API residual spine 物理退场、auth/outlet-power typed contract 收口、MQTT canonical naming/no-export guard、governance closeout 与 final repo audit 已全部落地
- `v1.1` 里程碑审计已更新：`.planning/v1.1-MILESTONE-AUDIT.md` 现覆盖 `Phase 7.1-17` 全范围，记录 `69/69 requirements`、`15/15 phases`，判定为 `tech_debt`（仅保留明确 de-scope/out-of-scope debt，不再保留 Phase 16 carry-forward residual）
- `Phase 18` 已完成：host-neutral boundary nucleus、shared auth bootstrap、device/capability truth 与 adapter projection guards 已全部落地。
- `Phase 19` 已完成：headless proof boot seam、single-chain device/replay/evidence proof、platform thin-shell demotion 与 second-root guards 已全部落地。
- `Phase 20` 已完成：remaining REST/MQTT boundary families、authority/replay fixtures、inventory/governance closeout 与 full gate evidence 已全部落地。

## Active Milestone Scope

- `Phase 18`：Host-Neutral Boundary Nucleus Extraction（complete）
- `Phase 19`：Headless Consumer Proof & Adapter Demotion（complete）
- `Phase 20`：Remaining Boundary Family Completion（complete）
- `Phase 21`：Replay / Observability / Exception Hardening（next）
- `Phase 22`：Governance, Docs & Release Readiness Closeout

## Carry-Forward Truths

- 正式协议根仍是 `LiproProtocolFacade`
- 正式 runtime root 仍是 `Coordinator`
- `Coordinator` 的正式 home 继续固定在 `custom_components/lipro/coordinator_entry.py`
- compat/residual 仍必须显式登记，不能重新合法化
- canonical normalization 仍必须在 protocol boundary 完成
- telemetry/replay/evidence 都只能 pull 正式真源，不得反向定义第二套事实
- 未来 CLI / 其他宿主若要复用，只能建立在 host-neutral boundary/auth/device contracts 之上，而不是把 HA runtime 抽成 second root
- `.planning/codebase/*.md` 只作为 derived collaboration maps / 协作图谱；若与 north-star、baseline 或 review truth 冲突，必须优先修正图谱而非倒逼真源
- `MqttTransportClient` 只是 localized concrete transport，不得回流成 package/root public surface

## Cross-Phase Arbitration (7.3-17)

1. `07.3` 只锁定 telemetry truth（fields / redaction / cardinality / timestamp / pseudo-id compatibility）
2. `07.4` 只锁定 replay truth（manifests / deterministic driver / replay assertions / run summary）
3. `07.5` 只锁定 governance closeout（matrices / evidence index / residual / delete gate）
4. `08` 只锁定 AI debug packaging（collector / schema / exporter entrypoint）
5. `09` 已完整完成：production residual surface closure 与 legacy test convergence 已统一收敛到 formal surface / shared harness / explicit compat seam
6. `10` 已完整完成：boundary contract closure、host-neutral auth/result contracts、HA adapter 降耦与文档/治理同步均已落地；仍不把 physical shared core 抽离提升为正式里程碑目标
7. `11` 已完整完成：control router formalization、runtime access/diagnostics hardening、entity/platform truth convergence 与 OTA hotspot slimming 已统一到同一条正式故事线
8. `12` 已完整完成：typed surface convergence、compat narrowing、hotspot decomposition 与 contributor-facing governance hygiene 已落地；不得重新打开已在 `Phase 11` 关闭的 residual truth
9. `13` 已完整完成：显式领域表面、runtime/status 热点 helper 边界与公开治理资产结构化守卫已锁定；后续不得重新引入 device/state 动态委托
10. `14` 已完整完成：`Coordinator.client` / `ScheduleApiService` 已退出正式故事线，`status_fallback.py` 与 `developer_router_support.py` 成为 helper homes，residual guard hardening 与 subordinate governance truth 已同步落地
11. `15` 已完整完成：developer feedback upload truth、active governance source-path guard、install/support/version truth、support hotspot typing narrowing 与 tooling/residual arbitration 已统一收口；未重开第二条正式主链
12. `16` 已完整完成：只做 post-audit truth alignment、hotspot decomposition、type/exception tightening、residual endgame、domain/entity/OTA rationalization 与 contributor DX follow-through；未重开第二条正式主链、第二套 protocol/runtime story 或无 gate rename campaign
13. `17` 已完整完成：Phase 16 carry-forward residual 全部得到真实 disposition；governance / audit / docs / guards 已同步到 final closeout truth

## Accumulated Context

### Roadmap Evolution

- Phase 10 executed and completed: API Drift Isolation & Core Boundary Prep
- Phase 11 executed and completed: Control Router Formalization & Wiring Residual Demotion
- Phase 11 audit-expansion addendum executed and closed
- Phase 12 completed: Type Contract Alignment, Residual Cleanup & Governance Hygiene (5 plans / 3 waves)
- Phase 13 added and completed: Explicit Domain Surface, Governance Guard Hardening & Hotspot Boundary Decomposition (3 plans / 2 waves)
- Phase 14 added and completed: Legacy Stack Final Closure, API Spine Demolition & Governance Truth Consolidation (4 plans / 3 waves)
- Phase 15 completed: Support feedback contract hardening, governance truth repair, and maintainability follow-through (5 plans / 3 waves)
- Phase 16 completed: Post-audit truth alignment, hotspot decomposition, and residual endgame (all 6 plans complete; second-pass audit recorded)
- Phase 17 completed: Final residual retirement, typed-contract tightening, governance closeout, and final repo audit (4 plans / 3 waves)

## Governance Truth Sources

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/MILESTONES.md`
3. `.planning/ROADMAP.md`
4. `.planning/REQUIREMENTS.md`
5. `.planning/STATE.md`
6. `.planning/baseline/*.md`
7. `.planning/reviews/*.md`
8. `docs/developer_architecture.md`
9. `AGENTS.md`
10. `CLAUDE.md`（若使用 Claude Code）

## Current Milestone Status

- **Milestone:** `v1.2 Host-Neutral Core & Replay Completion`
- **Phase range:** `18 -> 22`
- **Completed so far:** `Phase 18`, `Phase 19`, `Phase 20`
- **Next focus:** replay/evidence expansion、broad-catch 收窄与 observability/governance hardening

## Recommended Next Command

1. `$gsd-plan-phase 21` —— 为 replay / observability / exception hardening 制定详细执行计划
2. `$gsd-execute-phase 21` —— 执行 broad-catch / observability hardening
3. `$gsd-progress` —— 查看 v1.2 当前推进态

## Session Continuity

If resuming, read in this order:
1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/MILESTONES.md`
3. `.planning/milestones/v1.0-ROADMAP.md`
4. `.planning/milestones/v1.0-REQUIREMENTS.md`
5. `.planning/PROJECT.md`
6. `.planning/REQUIREMENTS.md`
7. `.planning/ROADMAP.md`
8. `.planning/STATE.md`
9. `.planning/phases/18-host-neutral-boundary-nucleus-extraction/18-CONTEXT.md`
10. `.planning/phases/18-host-neutral-boundary-nucleus-extraction/18-RESEARCH.md`
11. `.planning/phases/18-host-neutral-boundary-nucleus-extraction/18-VERIFICATION.md`
12. `.planning/phases/19-headless-consumer-proof-adapter-demotion/19-CONTEXT.md`
13. `.planning/phases/19-headless-consumer-proof-adapter-demotion/19-RESEARCH.md`
14. `.planning/phases/19-headless-consumer-proof-adapter-demotion/19-VALIDATION.md`
15. `.planning/phases/19-headless-consumer-proof-adapter-demotion/19-VERIFICATION.md`
16. `.planning/phases/19-headless-consumer-proof-adapter-demotion/19-01-PLAN.md`
17. `.planning/phases/19-headless-consumer-proof-adapter-demotion/19-02-PLAN.md`
18. `.planning/phases/19-headless-consumer-proof-adapter-demotion/19-03-PLAN.md`
19. `.planning/phases/19-headless-consumer-proof-adapter-demotion/19-04-PLAN.md`
20. `.planning/baseline/*.md`
21. `.planning/reviews/*.md`
22. `AGENTS.md`
23. `CLAUDE.md`（若使用 Claude Code）
24. `docs/developer_architecture.md`
