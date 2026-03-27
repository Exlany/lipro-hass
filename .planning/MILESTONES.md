# Milestones

> Machine-readable bootstrap truth now lives in the shared `governance-route` contract block below; milestone chronology remains human-readable archive history instead of the parser-visible selector.

<!-- governance-route-contract:start -->
```yaml
contract_version: 1
contract_name: governance-route
active_milestone:
  version: v1.22
  name: Maintainer Entry Contracts, Release Operations Closure & Contributor Routing
  status: Phase 84 complete (2026-03-27)
  phase: "84"
  phase_title: Governance/open-source guard coverage and milestone truth freeze
  route_mode: Phase 84 complete
latest_archived:
  version: v1.21
  name: Governance Bootstrap Truth Hardening & Planning Route Automation
  status: archived / evidence-ready (2026-03-26)
  phase: "80"
  phase_title: Governance typing closure and final meta-suite hotspot topicization
  phase_dir: 80-governance-typing-closure-and-final-meta-suite-hotspot-topicization
  audit_path: .planning/v1.21-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_21_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.20
  name: Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement
  evidence_path: .planning/reviews/V1_20_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.22 active route / Phase 84 complete / latest archived baseline = v1.21
  default_next_command: $gsd-complete-milestone v1.22
  latest_archived_evidence_pointer: .planning/reviews/V1_21_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->

## v1.21 Governance Bootstrap Truth Hardening & Planning Route Automation (Shipped: 2026-03-26; Closeout: 2026-03-26)

**Phase range:** `76 -> 80`
**Phases completed:** 5 phases, 15 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** latest archived evidence index = `.planning/reviews/V1_21_EVIDENCE_INDEX.md`

**Key accomplishments:**
- 把 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 的 bootstrap selector 收口为 machine-readable `governance-route` contract，并在 archive promotion 后稳定切到 `no active milestone route / latest archived baseline = v1.21`，同时保留 historical closeout route truth = `no active milestone route / latest archived baseline = v1.21`
- 完成 focused bootstrap smoke、route-handoff quality gate 与 promoted-evidence / review-ledger 冻结，让 `$gsd-next` 只能把下一步前推到 `$gsd-new-milestone`
- 拆薄 `check_file_matrix_registry` hotspot、topicize release-contract mega-suite，并保持 governance/tooling outward contract 与 file-matrix honesty 稳定
- 收口 governance/tooling typing regressions、补齐 `77-VALIDATION` 与 final meta-suite hotspot topicization，把 `Phase 76 -> 80` 一次性冻结为 archived-only evidence bundle

**Closeout assets:**
- `.planning/v1.21-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_21_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.21-ROADMAP.md`
- `.planning/milestones/v1.21-REQUIREMENTS.md`
- `.planning/phases/76-governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation/{76-01-SUMMARY.md,76-02-SUMMARY.md,76-03-SUMMARY.md,76-VERIFICATION.md,76-VALIDATION.md}`
- `.planning/phases/77-governance-guard-topicization-bootstrap-smoke-coverage-and-literal-drift-reduction/{77-01-SUMMARY.md,77-02-SUMMARY.md,77-03-SUMMARY.md,77-VERIFICATION.md,77-VALIDATION.md}`
- `.planning/phases/78-quality-gate-formalization-route-handoff-ergonomics-and-milestone-closeout-readiness/{78-01-SUMMARY.md,78-02-SUMMARY.md,78-03-SUMMARY.md,78-SUMMARY.md,78-VERIFICATION.md,78-VALIDATION.md}`
- `.planning/phases/79-governance-tooling-hotspot-decomposition-and-release-contract-topicization/{79-01-SUMMARY.md,79-02-SUMMARY.md,79-03-SUMMARY.md,79-SUMMARY.md,79-VERIFICATION.md,79-VALIDATION.md}`
- `.planning/phases/80-governance-typing-closure-and-final-meta-suite-hotspot-topicization/{80-01-SUMMARY.md,80-02-SUMMARY.md,80-03-SUMMARY.md,80-SUMMARY.md,80-VERIFICATION.md,80-VALIDATION.md}`

---

## v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement (Shipped: 2026-03-25; Closeout: 2026-03-25)

**Phase range:** `72 -> 75`
**Phases completed:** 4 phases, 16 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** latest archived evidence index = `.planning/reviews/V1_20_EVIDENCE_INDEX.md`

**Key accomplishments:**
- 收口 `Coordinator` bootstrap / lifecycle orchestration / `runtime_access` probing，把 startup 与 lifecycle hotspot 压回既有 formal homes
- 完成 service-router forwarding family、diagnostics/helper duplication、entity runtime strategy 与 schedule runtime surface 的 formalize / deduplicate
- 继续退役 auth legacy snapshot / compatibility wrapper，完成 suite topicization、governance cleanup 与 archive-readiness arbitration
- 统一 private-access honest story、promoted closeout evidence allowlist 与 thin-adapter typing，并保留 historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.20`

**Closeout assets:**
- `.planning/v1.20-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_20_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.20-ROADMAP.md`
- `.planning/milestones/v1.20-REQUIREMENTS.md`
- `.planning/phases/72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement/{72-01-SUMMARY.md,72-02-SUMMARY.md,72-03-SUMMARY.md,72-04-SUMMARY.md,72-VERIFICATION.md,72-VALIDATION.md}`
- `.planning/phases/73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization/{73-01-SUMMARY.md,73-02-SUMMARY.md,73-03-SUMMARY.md,73-04-SUMMARY.md,73-VERIFICATION.md,73-VALIDATION.md}`
- `.planning/phases/74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout/{74-01-SUMMARY.md,74-02-SUMMARY.md,74-03-SUMMARY.md,74-04-SUMMARY.md,74-VERIFICATION.md,74-VALIDATION.md}`

---

## v1.0 North Star Rebuild (Shipped: 2026-03-13)

**Phase range:** `1 -> 7`（含 `1.5 / 2.5 / 2.6`）
**Phases completed:** 10 phases, 32 plans, 0 tasks
**Status:** shipped / archived

**Key accomplishments:**

- 重建北极星单一正式主链
- 收口 protocol / runtime / control / assurance / governance 五平面骨架
- 建立 v1.0 归档资产与 milestone 级基线

---

## v1.1 Protocol Fidelity & Operability (Closeout: 2026-03-15)

**Phase range:** `7.1 -> 17`
**Phases completed:** 15 phases, 58 plans, 0 tasks
**Status:** archived / evidence-ready

**Key accomplishments:**

- formalized boundary decoder families、architecture policy enforcement、runtime telemetry exporter 与 replay/evidence 主链
- 完成 final residual retirement、typed contract tightening、governance closeout 与 `v1.1-MILESTONE-AUDIT.md`
- 固化 `V1_1_EVIDENCE_INDEX.md` 作为 pull-only closeout pointer

**Closeout assets:**

- `.planning/v1.1-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_1_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.1-ROADMAP.md`
- `.planning/milestones/v1.1-REQUIREMENTS.md`

---

## v1.2 Host-Neutral Core & Replay Completion (Closeout revalidated: 2026-03-17)

**Phase range:** `18 -> 24`
**Phases completed:** 7 phases, 24 plans, 0 tasks
**Status:** archived snapshots created / handoff-ready；archive-ready verdict revalidated 2026-03-17

**Key accomplishments:**

- 完成 host-neutral boundary/auth/device nucleus 抽取，并以 headless consumer proof 证明 single-chain reuse
- 完成 remaining boundary family formalization、replay/evidence explicit coverage、shared failure taxonomy 与 observability consumer convergence
- 完成 governance/docs/release evidence closeout、`v1.2` milestone audit、final repo audit 与 `v1.3` handoff bundle
- `Phase 24` reopen (`24-04` / `24-05`) 已修复 closeout gate regressions，并用 fresh evidence 重新验证 archive-ready / handoff-ready verdict

**Closeout assets:**

- `.planning/reviews/V1_2_EVIDENCE_INDEX.md`
- `.planning/v1.2-MILESTONE-AUDIT.md`
- `.planning/v1.3-HANDOFF.md`
- `.planning/milestones/v1.2-ROADMAP.md`
- `.planning/milestones/v1.2-REQUIREMENTS.md`

---

## v1.4 Sustainment, Trust Gates & Final Hotspot Burn-down (Shipped: 2026-03-19)

**Phase range:** `34 -> 39`
**Phases completed:** 6 phases, 19 plans, 0 tasks
**Status:** archived / evidence-ready

**Key accomplishments:**

- formalized continuity / custody / freeze contract，并补齐 tagged `CodeQL` hard gate、keyless `cosign` signing 与 provenance verification
- 完成 protocol/runtime hotspot 最后一轮瘦身，把 exception / typed budget 与 child-façade seams 收回正式主链
- 完成 mega-test 第三波 topicization、derived-truth convergence 与 final external-boundary residual retirement
- 完成 governance current-story convergence、control-home clarification、dead-shell retirement 与 full hard-gate closeout promotion

**Closeout assets:**

- `.planning/v1.4-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_4_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.4-ROADMAP.md`
- `.planning/milestones/v1.4-REQUIREMENTS.md`
- `.planning/phases/39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition/39-SUMMARY.md`
- `.planning/phases/39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition/39-VERIFICATION.md`

---

## v1.5 Governance Truth Consolidation & Control-Surface Finalization (Shipped: 2026-03-19)

**Phase range:** `40`
**Phases completed:** 1 phase, 7 plans, 0 tasks
**Status:** archived / evidence-ready

**Key accomplishments:**

- unified active truth, archive identity, promoted phase assets, and continuity order into one current-story contract
- introduced `.planning/baseline/GOVERNANCE_REGISTRY.json` as machine-readable governance truth and synchronized release/support/install routing
- converged control/services runtime reads through `runtime_access` and removed parallel traversal / lookup stories
- unified schedule service auth/error execution through the formal shared executor and closed touched naming residue

**Closeout assets:**

- `.planning/v1.5-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_5_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.5-ROADMAP.md`
- `.planning/milestones/v1.5-REQUIREMENTS.md`
- `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-SUMMARY.md`
- `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-VERIFICATION.md`
- `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-VALIDATION.md`

---

## v1.6 Delivery Trust Hardening, Runtime Boundary Decoupling & Maintainability Closure (Closeout: 2026-03-20)

**Phase range:** `42 -> 45`
**Phases completed:** 4 phases, 16 plans, 0 tasks
**Status:** archived / evidence-ready

**Key accomplishments:**

- formalized maintainer continuity, release artifact install smoke, dual coverage gates, and compatibility preview truth
- decoupled `control/` ↔ `services/`, typed `RuntimeAccess`, and moved runtime infra back to their formal homes
- pruned phase-trace authority noise, converged façade-era terminology, and clarified contributor fast-path / bilingual boundary
- decomposed hotspot files, introduced typed failure semantics, and upgraded benchmark evidence into anti-regression truth

**Closeout assets:**

- `.planning/v1.6-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_6_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.6-ROADMAP.md`
- `.planning/milestones/v1.6-REQUIREMENTS.md`
- `.planning/phases/45-hotspot-decomposition-and-typed-failure-semantics/45-SUMMARY.md`
- `.planning/phases/45-hotspot-decomposition-and-typed-failure-semantics/45-VERIFICATION.md`

---

## v1.12 Verification Localization & Governance Guard Topicization (Closeout: 2026-03-22)

**Phase range:** `59`
**Phases completed:** 1 phase, 3 plans, 0 tasks
**Status:** archived / evidence-ready

**Key accomplishments:**

- public-surface / governance-history / follow-up-route megaguards 退成 thin shell runnable roots，并按 truth family localized
- `device_refresh` giant suite 已拆成 parsing / filter / snapshot / runtime focused verification topology
- current-story docs、verification matrix、testing map 与 review ledgers 已冻结 localized verification / no-growth story

**Closeout assets:**

- `.planning/v1.12-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_12_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.12-ROADMAP.md`
- `.planning/milestones/v1.12-REQUIREMENTS.md`
- `.planning/phases/59-verification-localization-and-governance-guard-topicization/59-SUMMARY.md`
- `.planning/phases/59-verification-localization-and-governance-guard-topicization/59-VERIFICATION.md`

---

## v1.13 Tooling Truth Decomposition, Formal-Home Slimming & Naming/Discoverability Convergence (Closeout: 2026-03-22)

**Phase range:** `60 -> 62`
**Phases completed:** 3 phases, 11 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** prior archive-ready closeout baseline = `.planning/reviews/V1_13_EVIDENCE_INDEX.md`

**Key accomplishments:**

- 完成 tooling truth / file-governance hotspot inward decomposition，并冻结 `FILE_MATRIX / VERIFICATION_MATRIX / TESTING` 的 current story
- 继续切薄 `anonymous_share` / diagnostics / OTA / `select` 等 large-but-correct formal homes，并补齐 focused maintainability evidence
- 收口 support-seam naming、public docs fast path 与 discoverability / anti-regression governance truth

**Closeout assets:**

- `.planning/v1.13-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_13_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.13-ROADMAP.md`
- `.planning/milestones/v1.13-REQUIREMENTS.md`
- `.planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/60-SUMMARY.md`
- `.planning/phases/61-formal-home-slimming-for-large-but-correct-production-modules/61-SUMMARY.md`
- `.planning/phases/62-naming-clarity-support-seam-governance-and-public-discoverability/62-SUMMARY.md`

---

## v1.14 Governance Truth Realignment, Typed Runtime Access & Final Hidden-Root Closure (Closeout: 2026-03-23)

**Phase range:** `63 -> 66`
**Phases completed:** 4 phases, 15 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** prior archive-ready closeout baseline = `.planning/reviews/V1_14_EVIDENCE_INDEX.md`

**Key accomplishments:**

- 完成 governance latest-pointer / release-target fidelity 对齐，并把 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES / docs / runbook` 收束到同一 archive story
- 把 `RuntimeAccess`、telemetry / schedule / diagnostics、runtime alias / device extras 与 anonymous-share submit contract 全部收口到更诚实的 typed formal seams
- 清理 HA root adapter folklore，并为 `transport_executor` / `protocol_service` / `protocol facade` 铺设 focused seam regressions，结束 mega-matrix 独占验证

**Closeout assets:**

- `.planning/v1.14-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_14_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.14-ROADMAP.md`
- `.planning/milestones/v1.14-REQUIREMENTS.md`
- `.planning/phases/63-governance-truth-realignment-typed-runtime-access-and-hidden-root-closure/63-SUMMARY.md`
- `.planning/phases/64-telemetry-typing-schedule-contracts-and-diagnostics-hotspot-slimming/64-SUMMARY.md`
- `.planning/phases/65-runtime-access-de-reflection-and-anonymous-share-hotspot-closure/65-SUMMARY.md`
- `.planning/phases/66-release-target-fidelity-adapter-root-cleanup-and-focused-protocol-coverage-hardening/66-SUMMARY.md`

---

## v1.15 Typed Contract Convergence, Tooling Kernel Hardening & Mypy Closure (Closeout: 2026-03-24)

**Phase range:** `67`
**Phases completed:** 1 phase, 6 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** prior archive-ready closeout baseline = `.planning/reviews/V1_15_EVIDENCE_INDEX.md`

**Key accomplishments:**

- 把 telemetry / REST / anonymous-share / control telemetry surface / service-handler fixtures 全部收口到更诚实的 typed formal seams，并让 `uv run mypy` 回到正式绿色
- 统一 toolchain/governance payload narrowing、typed test doubles、runtime/control wiring callable truth，结束 broad `object` / stale route 双真相
- 以 `PROJECT / ROADMAP / REQUIREMENTS / STATE / docs/README` 为核心冻结 `v1.15` closeout truth，并在同一轮通过 repo-wide quality gates

**Closeout assets:**

- `.planning/v1.15-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_15_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.15-ROADMAP.md`
- `.planning/milestones/v1.15-REQUIREMENTS.md`
- `.planning/phases/67-typed-contract-convergence-toolchain-hardening-and-mypy-closure/67-SUMMARY.md`
- `.planning/phases/67-typed-contract-convergence-toolchain-hardening-and-mypy-closure/67-VERIFICATION.md`

---

## v1.16 Master Audit Follow-Through, Hotspot Finalization & Docs Contract Hardening (Closeout: 2026-03-24)

**Phase range:** `68`
**Phases completed:** 1 phase, 6 plans, 0 tasks
**Status:** archived / evidence-ready with carry-forward
**Route truth (at v1.16 closeout):** latest archive-ready closeout pointer = `.planning/reviews/V1_16_EVIDENCE_INDEX.md`

**Key accomplishments:**
- 完成 refreshed repo-wide audit follow-through，继续 inward split telemetry / MQTT / anonymous-share / OTA / runtime hotspots，并冻结 regrowth budget 与 no-growth story
- 统一 `README*`、`docs/README.md`、`manifest.json`、`pyproject.toml`、GitHub templates 与 governance guards 的 docs first-hop / version / release contract
- 在同一轮通过 focused proof、`ruff`、`mypy`、architecture policy、file-matrix 与 full pytest，并把 non-blocking residual 正式 carry-forward 到 `v1.17 / Phase 69`

**Closeout assets:**
- `.planning/v1.16-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_16_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.16-ROADMAP.md`
- `.planning/milestones/v1.16-REQUIREMENTS.md`
- `.planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/68-SUMMARY.md`
- `.planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/68-VERIFICATION.md`
- `.planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/68-VALIDATION.md`

---

## v1.17 Residual Formalization, Quality-Balance Hardening & Open-Source Contract Closure (Closeout: 2026-03-24)

**Phase range:** `69`
**Phases completed:** 1 phase, 5 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth (at v1.17 closeout):** latest archive-ready closeout pointer = `.planning/reviews/V1_17_EVIDENCE_INDEX.md`

**Key accomplishments:**
- formalize `runtime_access` read-model seams、继续 thin `runtime_access_support.py` / `runtime_infra.py`，并保持 single outward runtime home 不漂移
- 把 schedule/service path 压回 typed device-context contract，去掉 protocol-shaped choreography 与多余 wrapper / shim / lazy-import 故事
- 统一 checker、focused integration、open-source docs / metadata / continuity truth，并把里程碑切换到 latest archived baseline / no active milestone route

**Closeout assets:**
- `.planning/v1.17-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_17_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.17-ROADMAP.md`
- `.planning/milestones/v1.17-REQUIREMENTS.md`
- `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/69-SUMMARY.md`
- `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/69-VERIFICATION.md`
- `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/69-VALIDATION.md`

---

## v1.18 Support-Seam Slimming, OTA Resolver Consolidation & Governance Test Topicization (Closeout: 2026-03-24)

**Phase range:** `70`
**Phases completed:** 1 phase, 5 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** latest archive-ready closeout pointer = `.planning/reviews/V1_18_EVIDENCE_INDEX.md`

**Key accomplishments:**
- 将 `runtime_access_support.py` inward split 为更窄的 support-only helper cluster，并继续保持 `runtime_access.py` 唯一 outward runtime home
- 收口 anonymous-share submit/refresh/outcome 与 OTA query/selection shared helper truth，避免 helper-owned second story 与 entity-local choreography 回流
- 冻结 archive-vs-current version truth、topicize governance mega-tests，并在同一轮通过 focused gates、`ruff`、`mypy`、architecture policy 与 file-matrix

**Closeout assets:**
- `.planning/v1.18-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_18_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.18-ROADMAP.md`
- `.planning/milestones/v1.18-REQUIREMENTS.md`
- `.planning/phases/70-support-seam-slimming-ota-resolver-consolidation-and-governance-test-topicization/70-SUMMARY.md`
- `.planning/phases/70-support-seam-slimming-ota-resolver-consolidation-and-governance-test-topicization/70-VERIFICATION.md`
- `.planning/phases/70-support-seam-slimming-ota-resolver-consolidation-and-governance-test-topicization/70-VALIDATION.md`

---

---

## v1.19 Audit-Driven Final Hotspot Decomposition & Governance Truth Projection (Closeout: 2026-03-25)

**Phase range:** `71`
**Phases completed:** 1 phase, 5 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** latest archive-ready closeout pointer = `.planning/reviews/V1_19_EVIDENCE_INDEX.md`

**Key accomplishments:**
- 继续 inward split OTA diagnostics / firmware-install orchestration，保持 entity outward surface 与 helper-owned second story 不回流
- 收口 anonymous-share submit、request pacing 与 command-runtime 长流程，把热点切回更窄 typed helper seams
- 统一 planning / docs / tests 的 route truth，完成 `v1.19 -> v1.20` 的 archive-transition 交接并退为历史归档基线

**Closeout assets:**
- `.planning/v1.19-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_19_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.19-ROADMAP.md`
- `.planning/milestones/v1.19-REQUIREMENTS.md`
- `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-SUMMARY.md`
- `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VERIFICATION.md`
- `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VALIDATION.md`

---
