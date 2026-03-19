---
gsd_state_version: 1.0
milestone: v1.4
milestone_name: Sustainment, Trust Gates & Final Hotspot Burn-down
status: closeout_ready
last_updated: "2026-03-19T23:59:00Z"
progress:
  total_phases: 6
  completed_phases: 6
  total_plans: 19
  completed_plans: 19
---

# Project State

## Project Reference

See: `.planning/PROJECT.md`

**Current milestone:** `v1.4 Sustainment, Trust Gates & Final Hotspot Burn-down`
**Core value:** 在不回退 `LiproProtocolFacade` / `Coordinator` 单一正式主链的前提下，把 continuity / release trust、protocol/runtime hotspots、typed exception hardening、control-home truth、authority naming、governance current story 与 mega-test topology 收口成一条可验证、可归档的正式能力链。
**Current mode:** `Phase 39 complete`；`Phase 34 -> 39` 已于 `2026-03-19` 全部执行完成并通过 fresh hard gates，`v1.4` 当前处于 closeout-ready。`v1.2` 继续保持 archive-ready / handoff-ready，`v1.3` 继续保持 closeout-eligible 历史语义；当前默认 next action 是 `$gsd-complete-milestone v1.4`，而不是继续计划 `Phase 39`。

## Current Position

- `v1.0` 已归档到 `.planning/MILESTONES.md` 与 `.planning/milestones/v1.0-*.md`
- `v1.1` 已完成全部计划执行：`15 phases / 58 plans` 全绿落表
- `v1.1` / `v1.2` 的 roadmap / requirements archive snapshots 已落入 `.planning/milestones/`，后续里程碑可停止复用同一份历史 planning truth
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
- `Phase 18` 已完成：host-neutral boundary nucleus、shared auth bootstrap、device/capability truth 与 adapter projection guards 已全部落地。
- `Phase 19` 已完成：headless proof boot seam、single-chain device/replay/evidence proof、platform thin-shell demotion 与 second-root guards 已全部落地。
- `Phase 20` 已完成：remaining REST/MQTT boundary families、authority/replay fixtures、inventory/governance closeout 与 full gate evidence 已全部落地。
- `Phase 21` 已完成：remaining families replay/evidence coverage、shared failure taxonomy、broad-catch arbitration tightening 与 replay/evidence failure contract 已全部落地。
- `Phase 22` 已完成：diagnostics / system health / developer / support / evidence consumers 的 shared `failure_summary` vocabulary 收口与 governance sync 已全部落地。
- `Phase 23` 已完成：baseline/reviews/lifecycle truth、contributor docs/templates 与 release evidence pointer 已统一到 v1.2 最终故事线。
- `Phase 24` 已完成并于 2026-03-17 重新验证：final repo audit、milestone audit、evidence index、archive-ready bundle 与 `v1.3` handoff 已再次通过 fresh gates。
- `v1.2` 里程碑 closeout bundle 已按 reopened truth 回写：`.planning/reviews/V1_2_EVIDENCE_INDEX.md`、`.planning/v1.2-MILESTONE-AUDIT.md` 与 `.planning/v1.3-HANDOFF.md` 继续构成 archive-ready / handoff-ready bundle。
- `Phase 25` 已从单一 tranche 改为 v1.3 的总计划母相；`25.1 / 25.2 / 26 / 27` 路线已完成 seed routing，并显式排除了“把 vendor-defined MD5 登录路径误记为仓库弱密码学债”的错误口径。
- `Phase 34` 已完成：single-maintainer continuity 已被 formal custody / freeze / restoration contract 固化，release path 已具备 tagged `CodeQL` hard gate、keyless `cosign` signing bundles 与 provenance verification；public docs、runbook、CODEOWNERS 与 guard truth 已统一收口。
- `Phase 35` 已完成：protocol hotspot 继续 inward 到 `transport_executor.py` / `endpoint_surface.py` / `rest_port.py` / `mqtt_facade.py`；single protocol-root story 与定向回归/治理真相同步保持稳定。
- `Phase 36` 已完成：`CoordinatorPollingService` 已承接 polling/status/outlet/snapshot orchestration；runtime mainline broad catches 已进一步收口到 typed arbitration / fail-closed semantics，并同步 phase31 no-growth budget。
- `Phase 37` 已完成：init/runtime/governance mega-tests 已 topicize 成 `tests/core/test_init_service_handlers*.py`、`tests/core/test_init_runtime*.py` 与 `tests/meta/test_governance_phase_history*.py`；derived maps、verification guidance 与 drift guards 也已对齐到真实拓扑。
- `Phase 38` 已完成：external-boundary advisory naming residual 已关闭；firmware trust-root/advisory 语义、coverage-diff / benchmark truth 与 governance closeout anchors 已统一到 fresh-audit baseline。
- `Phase 25` 已完成：总计划母相已冻结 routed requirements、child-phase boundaries、no-return rules 与 next-command handoff；`.planning/codebase/*` 对本轮仍只保留 derived-map 身份。
- `Phase 25.1` 已完成：snapshot refresh 现采用 atomic rejection + last-known-good arbitration；coordinator fail-closed 主链与相关测试切片已全部转成正式语义。
- `Phase 25.2` 已完成：telemetry bridge 现只 pull `Coordinator.protocol` / `telemetry_service` formal surfaces；touched authority / residual / derived-map docs 已完成诚实同步。
- `Phase 26` 已完成：默认支持安装链已切到 verified release assets，release tail 现发布 installer / SBOM / provenance attestation，support/security/product metadata 也已统一到诚实口径。
- `Phase 27` 已完成：`protocol_service` formal capability port、coordinator pure forwarder retirement、phase residue cleanup 与测试巨石拆分/治理图谱同步已全部落地。
- `Phase 28` 已完成：tagged release security gate、artifact attestation verification、release identity manifest 与 maintainer continuity/support lifecycle truth 已全部落地。
- `Phase 29` 已完成：`LiproRestFacade` remaining hotspot 已沿 child-façade 主链继续切薄，REST tests 也已按 `transport/auth`、`command/pacing`、`capability wrappers` 专题化并通过 file-matrix / public-surface truth。
- `Phase 30` 已完成：REST response/result spine、protocol boundary contracts 与 control lifecycle named failure contracts 已全部收口；phase gate `293 passed` 且 protocol/control/static truth 全绿。
- `Phase 30-03` 已完成：control lifecycle setup/unload/reload named failure contracts 已冻结为 `setup_auth_failed/setup_not_ready/setup_failed`、`unload_shutdown_degraded`、`reload_auth_failed/reload_not_ready/reload_failed`；system health 仍只同步 shared `failure_summary` 最小载荷，未扩成 diagnostics payload cleanup；Phase 31 继续独占 runtime/service/platform typed budget 与 broad-catch closeout。
- `Phase 31` 已完成：runtime/service/platform touched zones 的 typed budget、warning cleanup、broad-catch closure 与 governance/toolchain truth 已全部收口；phase gate `445 passed` + touched-zone `mypy` 全绿。
- `Phase 32` 已执行完成：planning truth convergence、repo-wide gate honesty、release/maintainer/docs convergence、derived-map freshness 与 hotspot / test / typed / exception / residue follow-through 已全部完成收口；`uv run ruff check .` 与 `uv run mypy` 均已 repo-wide 真绿。
- `Phase 33` 已于 `2026-03-18` 执行完成：runtime contract dual-truth、control 去回路、giant hotspots / broad-catch / gate drift / dependency posture / deep-doc continuity / mega-test topicization 已全部收口；`uv run ruff check .` 全绿，`uv run python scripts/check_translations.py && uv run python scripts/check_file_matrix.py --check` 全绿，family 回归与 governance/public-surface closeout 合计 `656 passed`。
- `Phase 34` 已于 `2026-03-18` 执行完成：continuity/custody/freeze contract、tagged `CodeQL` hard gate、keyless `cosign` signing bundles、release identity manifest truth 与 planning/governance 回写均已收口。

## Completed Milestone Scope

- `Phase 18`：Host-Neutral Boundary Nucleus Extraction（complete）
- `Phase 19`：Headless Consumer Proof & Adapter Demotion（complete）
- `Phase 20`：Remaining Boundary Family Completion（complete）
- `Phase 21`：Replay Coverage & Exception Taxonomy Hardening（complete）
- `Phase 22`：Observability Surface Convergence & Signal Exposure（complete）
- `Phase 23`：Governance convergence, contributor docs and release evidence closure（complete）
- `Phase 24`：Final milestone audit, archive readiness and v1.3 handoff prep（complete）

## Carry-Forward Truths

- 正式协议根仍是 `LiproProtocolFacade`
- 正式 runtime root 仍是 `Coordinator`
- `Coordinator` 的正式 home 继续固定在 `custom_components/lipro/coordinator_entry.py`
- compat/residual 仍必须显式登记，不能重新合法化
- canonical normalization 仍必须在 protocol boundary 完成
- telemetry/replay/evidence 都只能 pull 正式真源，不得反向定义第二套事实
- 未来 CLI / 其他宿主若要复用，只能建立在 host-neutral boundary/auth/device contracts 之上，而不是把 HA runtime 抽成 second root
- `.planning/codebase/*.md` 只作为 derived collaboration maps / 协作图谱；若与 north-star、baseline 或 review truth 冲突，必须优先修正图谱而非倒逼真源
- `MqttTransport` 继续只是 localized concrete transport，不得被回抬为 protocol root 或 public surface

## Accumulated Context

### Roadmap Evolution

- Phase 23 added: Governance convergence, contributor docs and release evidence closure
- Phase 24 added: Final milestone audit, archive readiness and v1.3 handoff prep
- Phase 32 added: Truth convergence, gate honesty, and quality-10 closeout
- Phase 33 added: Contract-truth unification, hotspot slimming, and productization hardening
- Phase 38 added: External-boundary residual retirement and quality-signal hardening
- Phase 39 added: Governance current-story convergence, control-home clarification, and mega-test decomposition

- Phase 10 executed and completed: API Drift Isolation & Core Boundary Prep
- Phase 11 executed and completed: Control Router Formalization & Wiring Residual Demotion
- Phase 11 audit-expansion addendum executed and closed
- Phase 12 completed: Type Contract Alignment, Residual Cleanup & Governance Hygiene (5 plans / 3 waves)
- Phase 13 added and completed: Explicit Domain Surface, Governance Guard Hardening & Hotspot Boundary Decomposition (3 plans / 2 waves)
- Phase 14 added and completed: Legacy Stack Final Closure, API Spine Demolition & Governance Truth Consolidation (4 plans / 3 waves)
- Phase 15 completed: Support feedback contract hardening, governance truth repair, and maintainability follow-through (5 plans / 3 waves)
- Phase 16 completed: Post-audit truth alignment, hotspot decomposition, and residual endgame (all 6 plans complete; second-pass audit recorded)
- Phase 17 completed: Final residual retirement, typed-contract tightening, governance closeout, and final repo audit (4 plans / 3 waves)
- Phase 18-24 completed and revalidated: host-neutral nucleus -> headless proof -> remaining-family completion -> replay / observability / governance / milestone closeout 全链条在 2026-03-17 fresh gates 下再次收官。
- Phase 38 completed: external-boundary residual retirement、quality-signal hardening 与 fresh-audit governance baseline alignment 已全部落地。
- Phase 39 completed: canonical current-story convergence、control-home clarification、dead-shell retirement、authority naming sync、governance guard topicization 与 closeout evidence promotion 已全部落地。

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

## Phase Asset Promotion Contract

- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 是 `.planning/phases/**` 的显式 promoted allowlist。
- 未列入 allowlist 的 phase `PLAN / CONTEXT / RESEARCH / PRD` 与临时 closeout 文件默认保持执行痕迹身份，不作为长期治理 / CI 证据。

## Current Milestone Status

- **Milestone:** `v1.4 Sustainment, Trust Gates & Final Hotspot Burn-down`
- **Phase range:** `34 -> 39`
- **Completed so far:** `Phase 34` 到 `Phase 39`
- **Closeout state:** `closeout-ready`（hard gates refreshed `2026-03-19`）
- **Closeout assets:** `.planning/phases/39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition/39-SUMMARY.md`, `.planning/phases/39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition/39-VERIFICATION.md`, `.planning/phases/39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition/39-VALIDATION.md`
- **Historical archives:** `.planning/milestones/v1.2-ROADMAP.md`, `.planning/milestones/v1.2-REQUIREMENTS.md`
- **Next focus:** `$gsd-complete-milestone v1.4`——归档当前里程碑并提升 Phase 39 closeout 资产；若只想复核当前 tranche，可运行 hard-gate 命令或 `$gsd-progress` 查看最终状态。

## Recommended Next Command

1. `$gsd-complete-milestone v1.4` —— 归档当前里程碑并把 `Phase 39` closeout 资产提升为正式里程碑证据
2. `$gsd-progress` —— 查看 `v1.4 / Phase 39 complete` 当前状态与 traceability
3. `uv run ruff check . && uv run mypy && uv run pytest -q tests/meta/test_governance*.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` —— 作为 post-closeout recheck snapshot
4. `$gsd-plan-milestone-gaps` —— 仅当新的 repo audit 发现真实缺口时使用；不得把已完成的 `Phase 39` 回写成 placeholder

**Historical launch pointer:** `$gsd-execute-phase 29`

## Session Continuity

If resuming, read in this order:
1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/MILESTONES.md`
3. `.planning/PROJECT.md`
4. `.planning/ROADMAP.md`
5. `.planning/REQUIREMENTS.md`
6. `.planning/STATE.md`
7. `.planning/phases/39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition/39-VERIFICATION.md`
8. `.planning/phases/39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition/39-SUMMARY.md`
9. `.planning/phases/39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition/39-VALIDATION.md`
10. `.planning/phases/38-external-boundary-residual-retirement-and-quality-signal-hardening/38-VERIFICATION.md`
11. `.planning/phases/38-external-boundary-residual-retirement-and-quality-signal-hardening/38-SUMMARY.md`
12. `.planning/phases/37-test-topology-and-derived-truth-convergence/37-VERIFICATION.md`
13. `.planning/phases/37-test-topology-and-derived-truth-convergence/37-SUMMARY.md`
14. `.planning/phases/36-runtime-root-and-exception-burn-down/36-VERIFICATION.md`
15. `.planning/phases/36-runtime-root-and-exception-burn-down/36-SUMMARY.md`
16. `.planning/phases/35-protocol-hotspot-final-slimming/35-VERIFICATION.md`
17. `.planning/phases/35-protocol-hotspot-final-slimming/35-SUMMARY.md`
18. `.planning/phases/34-continuity-and-hard-release-gates/34-VERIFICATION.md`
19. `.planning/phases/34-continuity-and-hard-release-gates/34-SUMMARY.md`
20. `.planning/phases/33-contract-truth-unification-hotspot-slimming-and-productization-hardening/33-VERIFICATION.md`
21. `.planning/phases/33-contract-truth-unification-hotspot-slimming-and-productization-hardening/33-SUMMARY.md`
22. `.planning/reviews/V1_2_EVIDENCE_INDEX.md`
23. `.planning/v1.2-MILESTONE-AUDIT.md`
24. `.planning/v1.3-HANDOFF.md`
25. `.planning/phases/32-truth-convergence-gate-honesty-and-quality-10-closeout/32-CONTEXT.md`
26. `.planning/phases/32-truth-convergence-gate-honesty-and-quality-10-closeout/32-RESEARCH.md`
27. `.planning/phases/31-runtime-service-typed-budget-and-exception-closure/31-VERIFICATION.md`
28. `.planning/phases/30-protocol-control-typed-contract-tightening/30-VERIFICATION.md`
29. `.planning/phases/24-final-milestone-audit-archive-readiness-and-v1-3-handoff-prep/24-VERIFICATION.md`
30. `.planning/baseline/*.md`
31. `.planning/reviews/*.md`
32. `AGENTS.md`
33. `CLAUDE.md`（若使用 Claude Code）
34. `docs/developer_architecture.md`
