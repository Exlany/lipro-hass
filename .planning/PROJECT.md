# Project: Lipro-HASS North Star Evolution


**Status:** Active
**Current route:** `no active milestone route / latest archived baseline = v1.21`；latest archived evidence index = `.planning/reviews/V1_21_EVIDENCE_INDEX.md`.
**Legacy route-string compatibility:** **Status:** `no active milestone route / latest archived baseline = v1.21`；latest archived closeout pointer = `.planning/reviews/V1_21_EVIDENCE_INDEX.md`.
**Goal:** 以 `v1.21` archived baseline、`.planning/v1.21-MILESTONE-AUDIT.md` verdict 与 `.planning/reviews/V1_21_EVIDENCE_INDEX.md` pull-only archived evidence 作为下一条正式路线的唯一 seed；后续 `$gsd-plan-phase / $gsd-execute-phase / $gsd-next` 只应从 `$gsd-new-milestone` 显式开立的新里程碑继续推进，不得把 `Phase 76 -> 80` closeout truth 回写成隐式 active route。
**Default next step:** `$gsd-new-milestone`
**Active baseline:** no active milestone；latest archived baseline = `v1.21`；previous archived baseline = `v1.20`。

<!-- governance-route-contract:start -->
```yaml
contract_version: 1
contract_name: governance-route
active_milestone: null
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
  current_route: no active milestone route / latest archived baseline = v1.21
  default_next_command: $gsd-new-milestone
  latest_archived_evidence_pointer: .planning/reviews/V1_21_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->

## Latest Archived Milestone (v1.21)

**Name:** `v1.21 Governance Bootstrap Truth Hardening & Planning Route Automation`

**Why now:** `v1.20` 已把 bootstrap / lifecycle / service-family / auth-residual 收口为 archived baseline，但 bootstrap parser drift、route-contract literal duplication 与 governance/tooling hotspot maintainability 仍暴露出 planning/bootstrap truth 与 closeout handoff 之间的治理成本。`Phase 76 -> 80` 已把 machine-readable route contract、focused bootstrap smoke、route-handoff quality gate、registry hotspot decomposition、release-contract topicization 与 typing closure 一次性收口为 archived-only baseline。

**North-star fit:** `v1.21` 归档后继续确认以下裁决：

- machine-readable route contract 继续是 parser-stable 单一 selector；human-readable milestone body 只保留 archive / audit 身份。
- `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES / baselines / reviews / tests/meta` 共同承认 `no active milestone route / latest archived baseline = v1.21`，不再为 closeout 补写第二套 current story。
- governance/tooling maintainability hotspot、release-contract mega-suite 与 typed JSON boundary 已完成 inward cleanup，不重开生产热点主链。
- latest archived evidence index 现已固定为 `.planning/reviews/V1_21_EVIDENCE_INDEX.md`；`v1.21` 成为 latest archived baseline，`v1.20` 退为 previous archived baseline；下一条正式路线只能通过 `$gsd-new-milestone` 显式建立。

**Current status:** `archived / evidence-ready (2026-03-26)`
**Starting baseline:** `.planning/v1.20-MILESTONE-AUDIT.md`, `.planning/reviews/V1_20_EVIDENCE_INDEX.md`, `.planning/milestones/v1.20-ROADMAP.md`, `.planning/milestones/v1.20-REQUIREMENTS.md`, `.planning/phases/75-access-mode-truth-closure-evidence-promotion-formalization-and-thin-adapter-typing-hardening/{75-01-SUMMARY.md,75-02-SUMMARY.md,75-03-SUMMARY.md,75-04-SUMMARY.md,75-VERIFICATION.md,75-VALIDATION.md}`
**Requirements basket:** `GOV-57`, `ARC-20`, `DOC-04`, `TST-23`, `QLT-31`, `GOV-58`, `HOT-35`, `TST-24`, `QLT-32`, `GOV-59`, `TYP-22`, `HOT-36`, `TST-25`, `QLT-33`
**Archive assets:** .planning/v1.21-MILESTONE-AUDIT.md, .planning/reviews/V1_21_EVIDENCE_INDEX.md, .planning/milestones/v1.21-ROADMAP.md, .planning/milestones/v1.21-REQUIREMENTS.md, .planning/phases/76-governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation/{76-01-SUMMARY.md,76-02-SUMMARY.md,76-03-SUMMARY.md,76-VERIFICATION.md,76-VALIDATION.md}, .planning/phases/77-governance-guard-topicization-bootstrap-smoke-coverage-and-literal-drift-reduction/{77-01-SUMMARY.md,77-02-SUMMARY.md,77-03-SUMMARY.md,77-VERIFICATION.md,77-VALIDATION.md}, .planning/phases/78-quality-gate-formalization-route-handoff-ergonomics-and-milestone-closeout-readiness/{78-01-SUMMARY.md,78-02-SUMMARY.md,78-03-SUMMARY.md,78-SUMMARY.md,78-VERIFICATION.md,78-VALIDATION.md}, .planning/phases/79-governance-tooling-hotspot-decomposition-and-release-contract-topicization/{79-01-SUMMARY.md,79-02-SUMMARY.md,79-03-SUMMARY.md,79-SUMMARY.md,79-VERIFICATION.md,79-VALIDATION.md}, .planning/phases/80-governance-typing-closure-and-final-meta-suite-hotspot-topicization/{80-01-SUMMARY.md,80-02-SUMMARY.md,80-03-SUMMARY.md,80-SUMMARY.md,80-VERIFICATION.md,80-VALIDATION.md}
**Default next command:** `$gsd-new-milestone`

## Previous Archived Milestone (v1.20)

**Name:** `v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement`

**Why now:** `v1.19` 已把 archive/current governance truth、OTA / anonymous-share / request-pacing / command-runtime hotspot 与 `Phase 71` closeout 收口到 archived baseline；`.planning/reviews/V1_19_TERMINAL_AUDIT.md` 则登记了 bootstrap / lifecycle / runtime-access / service-family / diagnostics-helper / entity-runtime / auth-legacy 这些仍值得沿既有 north-star seams inward convergence 的 residual。`Phase 72 -> 75` 已全部完成，最终把 access-mode honesty、promoted closeout evidence formalization 与 thin-adapter typing hardening 一并收口为 archived baseline。

**North-star fit:** `v1.20` 的 archived contract 继续确认以下裁决：

- bootstrap / lifecycle / runtime-access 只能回收到现有 `control/` 与 runtime formal homes，不得新建 orchestration root、builder folklore 或 shadow bootstrap chain。
- service-family / diagnostics/helper / schedule / entity runtime strategy 只能做 inward deduplication 与 formal-home clarification，不得恢复 helper-owned second story。
- auth legacy snapshot / compatibility wrapper 只能继续退役并缩窄 outward contract，不得引入新的 legacy alias / compat root。
- latest archived evidence index 已升级为 `.planning/reviews/V1_21_EVIDENCE_INDEX.md`；`v1.20` 现固定为 previous archived baseline，`.planning/reviews/V1_20_EVIDENCE_INDEX.md` 继续只承担历史 pull-only 身份。

**Current status:** `archived / evidence-ready (2026-03-25)`
**Archive assets:** .planning/v1.20-MILESTONE-AUDIT.md, .planning/reviews/V1_20_EVIDENCE_INDEX.md, .planning/milestones/v1.20-ROADMAP.md, .planning/milestones/v1.20-REQUIREMENTS.md, .planning/phases/72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement/{72-01-SUMMARY.md,72-02-SUMMARY.md,72-03-SUMMARY.md,72-04-SUMMARY.md,72-VERIFICATION.md,72-VALIDATION.md}, .planning/phases/73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization/{73-01-SUMMARY.md,73-02-SUMMARY.md,73-03-SUMMARY.md,73-04-SUMMARY.md,73-VERIFICATION.md,73-VALIDATION.md}, .planning/phases/74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout/{74-01-SUMMARY.md,74-02-SUMMARY.md,74-03-SUMMARY.md,74-04-SUMMARY.md,74-VERIFICATION.md,74-VALIDATION.md}
**Default next command:** `$gsd-new-milestone`

## Historical Archived Baseline (v1.19)

**Name:** `v1.19 Audit-Driven Final Hotspot Decomposition & Governance Truth Projection`

**Why now:** `v1.18` 已把 support-seam、anonymous-share / OTA helper convergence、archive/current version truth freeze 与治理 topicization 收口到归档态；repo-wide terminal audit 锁定的高杠杆热点则在 `Phase 71` 被继续 inward split，并于 `2026-03-25` 完成 archive promotion。当前它已退为 `v1.21` 的 historical archived baseline。

**North-star fit:** `v1.19` 的 archived contract 继续确认以下裁决：

- OTA / firmware update / anonymous-share / request pacing / command runtime 只允许 inward decomposition，不得新增 outward root、compat shell 或 second story。
- `PROJECT / ROADMAP / REQUIREMENTS / STATE / docs / meta guards` 在 `v1.19` archive promotion 当时共同承认 archived-only transition truth；当前治理状态已切换为 `no active milestone route / latest archived baseline = v1.21`，并把 `v1.20` 固定为 previous archived baseline。
- latest archived evidence index 已升级为 `.planning/reviews/V1_21_EVIDENCE_INDEX.md`；`.planning/reviews/V1_19_EVIDENCE_INDEX.md` 继续只承担 historical / pull-only 身份。
- `Phase 71` 留下的 focused no-growth guards 持续冻结 touched scope，防止 function-density 与 route drift 在 archived closeout 之后回流。

**Current status:** `archived / evidence-ready (2026-03-25)`
**Archive assets:** `.planning/v1.19-MILESTONE-AUDIT.md`, `.planning/reviews/V1_19_EVIDENCE_INDEX.md`, `.planning/milestones/v1.19-ROADMAP.md`, `.planning/milestones/v1.19-REQUIREMENTS.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/{71-SUMMARY.md,71-VERIFICATION.md,71-VALIDATION.md}`
**Default next command:** `$gsd-new-milestone`

## Archived Milestone (v1.17)

**Name:** `v1.17 Residual Formalization, Quality-Balance Hardening & Open-Source Contract Closure`

**Why now:** `v1.16` 已把 refreshed repo-wide audit 的主干问题归档，但明确保留了一组 non-blocking residual：`runtime_access_support.py` 的 read-model formalization、schedule/service path 的去协议化、wrapper/shim/lazy-import residue 的继续削减、checker/integration quality balance 的补强，以及 release-aware docs URL / machine-readable HA support / maintainer continuity truth 的最后收口。`Phase 69` 已把这些 residual 进一步压向更窄的正式 seams，并在同一轮完成静态门禁、focused proof 与归档准备。

**North-star fit:** `v1.17` 沿单一正式主链完成收口：

- `runtime_access.py` 持续作为唯一 outward runtime home；`runtime_access_support.py` 与 `runtime_infra.py` 只保留 inward helper / read-model seam 身份
- schedule、protocol-service 与 wrapper 链继续把协议细节往下压，没有借“收口”之名引入新的 facade / helper root
- 质量门从“只靠 meta/budget story”回到 checker + behavior + integration 的平衡组合
- 开源治理只记录 honest contract：允许诚实表达单维护者现实与 live-docs 限制，但不再让 stale pointer 与 active-route folklore 并存

**Phase range:** `Phase 69 -> 69`
**Current status:** `archived / evidence-ready (2026-03-24)`
**Starting baseline:** `.planning/v1.16-MILESTONE-AUDIT.md`, `.planning/reviews/V1_16_EVIDENCE_INDEX.md`, `.planning/milestones/v1.16-ROADMAP.md`, `.planning/milestones/v1.16-REQUIREMENTS.md`, `.planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/68-SUMMARY.md`, `.planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/68-VERIFICATION.md`, `.planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/68-VALIDATION.md`
**Requirements basket:** `GOV-53`, `ARC-16`, `HOT-26`, `HOT-27`, `OSS-09`, `TST-19`, `QLT-27`
**Archive assets:** `.planning/v1.17-MILESTONE-AUDIT.md`, `.planning/reviews/V1_17_EVIDENCE_INDEX.md`, `.planning/milestones/v1.17-ROADMAP.md`, `.planning/milestones/v1.17-REQUIREMENTS.md`, `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/69-SUMMARY.md`, `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/69-VERIFICATION.md`, `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/69-VALIDATION.md`
**Default next command:** `$gsd-new-milestone`

## Archived Milestone (v1.16)

**Name:** `v1.16 Master Audit Follow-Through, Hotspot Finalization & Docs Contract Hardening`

**Why now:** 本轮终极审阅重新确认：主链架构已基本正确，但 remaining debt 仍集中在少数“正确但偏厚”的 formal homes 与对外文档/版本契约漂移——例如 `core/telemetry/models.py`、`core/mqtt/message_processor.py`、`core/anonymous_share/share_client_flows.py`、`core/api/diagnostics_api_ota.py`、`runtime_infra.py` 等仍承载过多 decision density；与此同时，`README*` / `manifest.json` / `pyproject.toml` / `CHANGELOG.md` / `.github/*` 之间的 first-hop、version-signal、release-example 与 docs navigation 也出现了可验证的 current-story drift。`Phase 68` 已把这些问题沿单一正式主链收口完毕，并把 non-blocking residual 正式登记为后续 carry-forward route。

**North-star fit:** `v1.16` 在归档后继续承担 previous archive baseline 身份：

- remaining hotspots 只允许 `keep formal home + split inward + freeze budgets`，不得新建 public root / helper-owned second story / compat shell
- review 结论必须转成 phase plan、cross-AI review、focused guards 与 verification evidence；不允许停留在对话式意见
- public docs / metadata / release examples 必须共同承认同一 first-hop 与 version truth；不能让 README、manifest、workflow、templates 各讲一套故事
- 组织性限制（例如 maintainer bus factor）必须诚实记录，但不得通过伪 delegate 或虚构 support promise 来“修复”

**Phase range:** `Phase 68 -> 68`
**Current status:** `archived / evidence-ready with carry-forward (2026-03-24)`
**Starting baseline:** `.planning/v1.15-MILESTONE-AUDIT.md`, `.planning/reviews/V1_15_EVIDENCE_INDEX.md`, `.planning/milestones/v1.15-ROADMAP.md`, `.planning/milestones/v1.15-REQUIREMENTS.md`, `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-REMEDIATION-ROADMAP.md`, `.planning/phases/67-typed-contract-convergence-toolchain-hardening-and-mypy-closure/67-SUMMARY.md`
**Requirements basket:** `GOV-52`, `ARC-15`, `HOT-24`, `HOT-25`, `OSS-08`, `TST-18`, `QLT-26`
**Archive assets:** `.planning/v1.16-MILESTONE-AUDIT.md`, `.planning/reviews/V1_16_EVIDENCE_INDEX.md`, `.planning/milestones/v1.16-ROADMAP.md`, `.planning/milestones/v1.16-REQUIREMENTS.md`, `.planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/68-SUMMARY.md`, `.planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/68-VERIFICATION.md`, `.planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/68-VALIDATION.md`
**Carry-forward route result:** `closed by v1.17 archive (2026-03-24)`
**Default next command:** `$gsd-new-milestone`

## Archived Milestone (v1.15)

**Name:** `v1.15 Typed Contract Convergence, Tooling Kernel Hardening & Mypy Closure`

**Why now:** 最新全仓复审已证明 lint、architecture policy、file matrix 与 full pytest 都已恢复绿色，但 `uv run mypy` 仍报告 `339` 个错误，集中暴露了 telemetry typed dict / JSON-safe sink、REST endpoint ports、anonymous-share submit manager、control telemetry surface、service-handler 测试夹具与 YAML/meta/toolchain 解析辅助的 formal contract 漂移。只要这些裂隙继续存在，`v1.14` 的 archive-ready story 仍缺少“类型系统真相”这一最后硬门。

**North-star fit:** `v1.15` 继续沿单一正式主链推进：

- typed contract 必须收口到 protocol/runtime/control/test/tooling 的显式 formal ports，而不是继续允许 `object` / broad `dict[str, object]` / implicit union indexing 充当真源
- telemetry / anonymous-share / REST hotspots 只允许 inward tighten，不得引入新 public surface、compat shell 或 second root
- 测试夹具与 meta/toolchain helpers 只允许通过 Protocol、typed loader、narrowing helper 收口，不得继续依赖“运行时能跑即可”的弱类型 folklore
- 本轮 closeout 必须让 `mypy + ruff + architecture policy + file matrix + targeted pytest + full pytest` 同轮全绿，证明不是表面消音

**Phase range:** `Phase 67 -> 67`
**Current status:** `archived / evidence-ready (2026-03-24)`
**Starting baseline:** `.planning/v1.14-MILESTONE-AUDIT.md`, `.planning/reviews/V1_14_EVIDENCE_INDEX.md`, `.planning/milestones/v1.14-ROADMAP.md`, `.planning/milestones/v1.14-REQUIREMENTS.md`
**Requirements basket:** `GOV-51`, `TYP-19`, `ARC-14`, `HOT-23`, `TST-17`, `QLT-25`
**Archive assets:** `.planning/v1.15-MILESTONE-AUDIT.md`, `.planning/reviews/V1_15_EVIDENCE_INDEX.md`, `.planning/milestones/v1.15-ROADMAP.md`, `.planning/milestones/v1.15-REQUIREMENTS.md`, `.planning/phases/67-typed-contract-convergence-toolchain-hardening-and-mypy-closure/67-SUMMARY.md`, `.planning/phases/67-typed-contract-convergence-toolchain-hardening-and-mypy-closure/67-VERIFICATION.md`, `.planning/phases/67-typed-contract-convergence-toolchain-hardening-and-mypy-closure/67-VALIDATION.md`
**Default next command:** `$gsd-new-milestone`

## Archived Milestone (v1.14)

**Name:** `v1.14 Governance Truth Realignment, Typed Runtime Access & Final Hidden-Root Closure`

**Why now:** `v1.13` 已把 tooling truth、large-but-correct formal homes 与 naming/discoverability 收口到 archive-ready；`Phase 63 -> 64` 又已把 governance truth、typed runtime access、tooling/test hidden-root、telemetry / schedule / diagnostics hotspots 收口完毕。但 renewed review 仍指出三类最后高杠杆尾债：`runtime_access_support.py` 仍带 mock-aware probing 痕迹、runtime identity 仍借 alias sidecar 输送真相、anonymous-share submit path 仍保留 bool-only bridge 与 aggregate outcome 漂移。

**North-star fit:** `v1.14` 继续沿单一正式主链推进：

- 先修治理真相指针与 anti-drift guards，再做热点 inward split
- `RuntimeAccess` 只允许收口到 typed read-model，不得扩张成第二 runtime root
- `__init__.py` 只允许继续变薄，把 wiring/context 继续下沉到 `control/` formal homes
- tooling / tests 的目标是消灭 hidden-root 与 second truth，不是再造 helper folklore
- command failure / anonymous-share 只做 inward typed tightening，不引入新的 public surface 或 compat shell

**Phase range:** `Phase 63 -> 66`
**Current status:** `archived / evidence-ready (2026-03-23)`
**Starting baseline:** `.planning/v1.13-MILESTONE-AUDIT.md`, `.planning/reviews/V1_13_EVIDENCE_INDEX.md`, `.planning/milestones/v1.13-ROADMAP.md`, `.planning/milestones/v1.13-REQUIREMENTS.md`, `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-REMEDIATION-ROADMAP.md`, `.planning/phases/63-governance-truth-realignment-typed-runtime-access-and-hidden-root-closure/63-SUMMARY.md`
**Requirements basket:** `GOV-46`, `GOV-47`, `HOT-16`, `HOT-17`, `TST-13`, `TYP-16`, `QLT-21`, `ARC-11`, `HOT-18`, `HOT-19`, `TYP-17`, `TST-14`, `GOV-48`, `QLT-22`, `ARC-12`, `HOT-20`, `HOT-21`, `TYP-18`, `TST-15`, `GOV-49`, `QLT-23`, `GOV-50`, `OSS-07`, `ARC-13`, `HOT-22`, `TST-16`, `QLT-24`
**Archive assets:** `.planning/v1.14-MILESTONE-AUDIT.md`, `.planning/reviews/V1_14_EVIDENCE_INDEX.md`, `.planning/milestones/v1.14-ROADMAP.md`, `.planning/milestones/v1.14-REQUIREMENTS.md`, `.planning/phases/63-governance-truth-realignment-typed-runtime-access-and-hidden-root-closure/63-SUMMARY.md`, `.planning/phases/64-telemetry-typing-schedule-contracts-and-diagnostics-hotspot-slimming/64-SUMMARY.md`, `.planning/phases/65-runtime-access-de-reflection-and-anonymous-share-hotspot-closure/65-SUMMARY.md`, `.planning/phases/66-release-target-fidelity-adapter-root-cleanup-and-focused-protocol-coverage-hardening/66-SUMMARY.md`
**Default next command:** `$gsd-new-milestone`

## Archived Milestone (v1.6)

**Name:** `v1.6 Delivery Trust Hardening, Runtime Boundary Decoupling & Maintainability Closure`

**Why now:** `Phase 41` 审阅证明主链已经成熟，但仍存在五类值得正式路由的高杠杆尾债：release/install 缺少真实 artifact smoke、coverage/diff/local-CI parity 仍不足、`control/` ↔ `services/` 边界继续发黏、`RuntimeAccess` 仍带反射式读模型、`.planning/phases/**` 与术语/贡献入口噪音正在侵蚀 current truth 清晰度。

**North-star fit:** `v1.6` 继续沿单一正式主链推进：

- 先补 delivery truth 与 continuity hard gate，再做架构解耦，不重开第二主链
- 不把 `Phase 41` 审计 execution trace 误升为长期治理真源
- 不让 control/services/runtime 长回双向 helper / locator / infra story
- 热点拆分只沿正式 seams 收口，不扩张 public surface 或 compatibility folklore

**Phase range:** `Phase 42 -> 45`
**Current status:** `Phase 42 -> 45 archived / evidence-ready`（`16/16` 个执行 plans 已完成，`.planning/v1.6-MILESTONE-AUDIT.md`、`.planning/reviews/V1_6_EVIDENCE_INDEX.md`、`.planning/milestones/v1.6-ROADMAP.md` 与 `.planning/milestones/v1.6-REQUIREMENTS.md` 已落盘；next action is `$gsd-new-milestone`）
**Archive assets:** `.planning/v1.6-MILESTONE-AUDIT.md`, `.planning/reviews/V1_6_EVIDENCE_INDEX.md`, `.planning/milestones/v1.6-ROADMAP.md`, `.planning/milestones/v1.6-REQUIREMENTS.md`, `.planning/phases/45-hotspot-decomposition-and-typed-failure-semantics/45-SUMMARY.md`, `.planning/phases/45-hotspot-decomposition-and-typed-failure-semantics/45-VERIFICATION.md`
**Primary closeout targets:** delivery trust hardening、typed runtime read-model、control/services decoupling、governance asset pruning、terminology convergence、hotspot decomposition、typed failure semantics。

## Archived Milestone (v1.13)

**Name:** `v1.13 Tooling Truth Decomposition, Formal-Home Slimming & Naming/Discoverability Convergence`

**Why now:** `Phase 58` 已把 refreshed remediation route 明确写成 `Phase 59 -> 62`，而 `Phase 59` 又先完成了 verification localization。`v1.13` 的职责就是沿低噪声验证基线依次完成 tooling hotspot、large-but-correct formal homes 与 naming/discoverability 收口，并把结果提升为可供下一里程碑复用的 archive truth。

**North-star fit:** `v1.13` 沿单一正式主链完成 closeout：

- 先拆 tooling truth hotspot，再瘦 large-but-correct production homes，最后收口命名 / discoverability 噪音
- `FILE_MATRIX / VERIFICATION_MATRIX / TESTING / current-story docs` 始终保持单一 authority chain，不重开第二治理故事
- production refactor 只做 inward split，不恢复 compat shell、public wrapper 或第二 formal root
- public docs / discoverability follow-through 建立在代码与治理真相已经收敛之后，而不是反向定义架构

**Phase range:** `Phase 60 -> 62`
**Current status:** `archived / evidence-ready (2026-03-22)`
**Archive assets:** `.planning/v1.13-MILESTONE-AUDIT.md`, `.planning/reviews/V1_13_EVIDENCE_INDEX.md`, `.planning/milestones/v1.13-ROADMAP.md`, `.planning/milestones/v1.13-REQUIREMENTS.md`, `.planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/60-SUMMARY.md`, `.planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/60-VERIFICATION.md`, `.planning/phases/61-formal-home-slimming-for-large-but-correct-production-modules/61-SUMMARY.md`, `.planning/phases/61-formal-home-slimming-for-large-but-correct-production-modules/61-VERIFICATION.md`, `.planning/phases/62-naming-clarity-support-seam-governance-and-public-discoverability/62-SUMMARY.md`, `.planning/phases/62-naming-clarity-support-seam-governance-and-public-discoverability/62-VERIFICATION.md`
**Starting baseline:** `.planning/v1.12-MILESTONE-AUDIT.md`, `.planning/reviews/V1_12_EVIDENCE_INDEX.md`, `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-REMEDIATION-ROADMAP.md`, `.planning/phases/59-verification-localization-and-governance-guard-topicization/59-SUMMARY.md`, `.planning/phases/59-verification-localization-and-governance-guard-topicization/59-VERIFICATION.md`
**Requirements basket:** `HOT-14`, `TST-12`, `GOV-44`, `HOT-15`, `QLT-20`, `TYP-15`, `RES-14`, `DOC-07`, `GOV-45`
**Phase 60 delivered:** thin `scripts/check_file_matrix.py` root + `4` 个 tooling truth siblings、thin `tests/meta/test_toolchain_truth.py` root + `6` 个 truth-family modules，以及回写到 `FILE_MATRIX / VERIFICATION_MATRIX / TESTING / current-story docs` 的正式 freeze。
**Phase 61 delivered:** `anonymous_share` / diagnostics / OTA / select formal homes 现已 thin-root + focused collaborators，`test_select_behavior.py` 与 `.planning/reviews/FILE_MATRIX.md` 也已同步冻结新的 maintainability story。
**Phase 62 delivered:** `DeviceExtras` support helper 已与 `extras*` family 对齐，README/docs/CONTRIBUTING/SUPPORT public fast path 已压成单一路由，baseline/review truth 与 focused Phase 62 guards 也已冻结命名 / discoverability closeout。
**Follow-through after closeout:** 下一轮 milestone 应从 `v1.13` archived evidence 出发，经 `$gsd-new-milestone` 重新立项；`v1.12` / `v1.11` 继续保留为 refreshed route 历史基线。

## Archived Milestone (v1.12)

**Name:** `v1.12 Verification Localization & Governance Guard Topicization`

**Why now:** `Phase 58` 已经把全仓 refreshed audit 与 `Phase 59+` remediation route 固化为 current truth；`v1.12` 的职责就是先把 megaguards / megasuites 的 failure radius 缩小，让后续整改能在更窄、更诚实的验证边界上推进。

**North-star fit:** `v1.12` 沿单一正式主链完成 closeout：

- 未新增 public surface / second helper root / second governance story
- 只沿现有 verification truth seams topicize meta guards 与 core mega suite
- 先降低 failure localization 半径，再把后续 tooling / production surgery 路由到下一 milestone
- 所有 split 均已同步回 current-story docs 与 verification truth，而不是停留在 conversation-only 建议

**Phase range:** `Phase 59`
**Current status:** `archived / evidence-ready (2026-03-22)`
**Archive assets:** `.planning/v1.12-MILESTONE-AUDIT.md`, `.planning/reviews/V1_12_EVIDENCE_INDEX.md`, `.planning/milestones/v1.12-ROADMAP.md`, `.planning/milestones/v1.12-REQUIREMENTS.md`, `.planning/phases/59-verification-localization-and-governance-guard-topicization/59-SUMMARY.md`, `.planning/phases/59-verification-localization-and-governance-guard-topicization/59-VERIFICATION.md`
**Requirements basket:** `TST-11`, `QLT-19`, `GOV-43`
**Follow-through after closeout:** `v1.13` 已承接 `Phase 60 -> 62`，继续推进 tooling hotspot、formal-home slimming 与 naming/discoverability convergence
**Next route after Phase 59:** `$gsd-plan-phase 60`

## Planned Milestone (v1.11)

**Name:** `v1.11 Repository Audit Refresh & Next-Wave Remediation Routing`

**Why now:** `v1.10` 已完成其单一 scoped command-result 目标，但契约者当前要求一轮覆盖所有 Python / docs / config / governance surfaces 的终极审阅。最诚实的动作不是继续扩写 `v1.10`，而是把这轮 refreshed audit 本身立成新 milestone。

**North-star fit:** `v1.11` 继续沿单一正式主链推进：

- 不把旧 audit 文档误当永久权威，而是以它们为 baseline 重新核对当前代码真相
- 不为“找问题”而虚构 residual；只登记当前仍成立的风险、噪音与后续价值点
- 先形成 refreshed master verdict 与 remediation route，再决定后续局部重构
- 执行痕迹默认继续留在 phase 目录，只有显式 promoted 资产进入长期治理真源

**Phase range:** `Phase 58`
**Current status:** `Phase 58 complete (2026-03-22)`（architecture/code audit、governance/open-source audit、remediation roadmap 与 truth freeze 已完成）
**Seed input:** `.planning/reviews/V1_11_MILESTONE_SEED.md`
**Phase 58 PRD:** `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-PRD.md`
**Phase 58 planning assets:** `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-CONTEXT.md`, `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-RESEARCH.md`, `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-VALIDATION.md`, `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-01-PLAN.md`, `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-02-PLAN.md`, `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-03-PLAN.md`
**Phase 58 closeout:** `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-SUMMARY.md`, `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-VERIFICATION.md`
**Requirements basket:** `AUD-03`, `ARC-10`, `OSS-06`, `GOV-42`
**Immediate focus after closeout:** archive `v1.11` or seed the next remediation milestone from `58-REMEDIATION-ROADMAP.md`
**Next route after Phase 58:** `$gsd-complete-milestone v1.11`

## Planned Milestone (v1.10)

**Name:** `v1.10 Command-Result Typed Outcome & Reason-Code Hardening`

**Why now:** `v1.9` 已把 generic backoff residual 收口为 neutral helper truth；当前最高价值的 follow-up 不再是 retry ownership，而是把 command-result family 从 scattered literals 收口到 typed outcome / reason-code contract，让 `result_policy.py` / `result.py` / runtime sender / diagnostics query consumers 讲同一条故事。

**North-star fit:** `v1.10` 继续沿单一正式主链推进：

- 不新增 command helper root、compat shell 或第二套 outcome vocabulary
- 保持 `result_policy.py` 作为 classification/polling home、`result.py` 作为 stable export / failure arbitration home
- 不改变 diagnostics/runtime outward behavior，只提高内部 contract honesty 与 typeability
- 以 baseline / review / meta guard 冻结 typed command-result truth，而不是停留在 conversation-only improvement

**Phase range:** `Phase 57`
**Current status:** `Phase 57 complete (2026-03-22)`（`ERR-12 / TYP-14 / GOV-41` 已全部通过 code / typing / governance closeout 收口）
**Seed input:** `.planning/reviews/V1_10_MILESTONE_SEED.md`
**Phase 57 planning assets:** `.planning/phases/57-command-result-typed-outcome-and-reason-code-hardening/57-CONTEXT.md`, `.planning/phases/57-command-result-typed-outcome-and-reason-code-hardening/57-RESEARCH.md`, `.planning/phases/57-command-result-typed-outcome-and-reason-code-hardening/57-VALIDATION.md`, `.planning/phases/57-command-result-typed-outcome-and-reason-code-hardening/57-01-PLAN.md`, `.planning/phases/57-command-result-typed-outcome-and-reason-code-hardening/57-02-PLAN.md`, `.planning/phases/57-command-result-typed-outcome-and-reason-code-hardening/57-03-PLAN.md`
**Phase 57 closeout:** `.planning/phases/57-command-result-typed-outcome-and-reason-code-hardening/57-SUMMARY.md`, `.planning/phases/57-command-result-typed-outcome-and-reason-code-hardening/57-VERIFICATION.md`
**Immediate focus after closeout:** archive `v1.10` or seed the next milestone from the updated command-result contract baseline
**Requirements basket:** `ERR-12`, `TYP-14`, `GOV-41`
**Next route after Phase 57:** `$gsd-complete-milestone v1.10`

## Planned Milestone (v1.9)

**Name:** `v1.9 Shared Backoff Neutralization & Cross-Plane Retry Hygiene`

**Why now:** `v1.8` 已完成 second-round sustainment，而当前唯一仍在 active residual ledger 中显式挂到 `Phase 56+` 的 carry-forward，是 generic exponential backoff helper leak。此时最正确的动作不是重开大扫除，而是把这条 ownership lie 关掉：`RequestPolicy` 只保留 API-local policy truth，pure backoff primitive 回到 neutral shared home。

**North-star fit:** `v1.9` 继续沿单一正式主链推进：

- 不把 neutral helper 升格成 shared retry manager、second root 或新 public surface
- 不把 command/runtime/MQTT 的 retry semantics 强行统一，只共享一个 honest primitive
- 不改写 `RequestPolicy` 的 API-local `429` / busy / pacing ownership，只纠正它的 cross-plane utility leakage
- 以 baseline / review / meta guard 关闭 residual，而不是只在代码里“修一下”

**Phase range:** `Phase 56`
**Current status:** `Phase 56 complete (2026-03-22)`（`RES-13 / ARC-09 / GOV-40` 已全部通过 code / governance closeout 收口）
**Seed input:** `.planning/reviews/V1_9_MILESTONE_SEED.md`
**Phase 56 planning assets:** `.planning/phases/56-shared-backoff-neutralization-and-cross-plane-retry-hygiene/56-CONTEXT.md`, `.planning/phases/56-shared-backoff-neutralization-and-cross-plane-retry-hygiene/56-RESEARCH.md`, `.planning/phases/56-shared-backoff-neutralization-and-cross-plane-retry-hygiene/56-VALIDATION.md`, `.planning/phases/56-shared-backoff-neutralization-and-cross-plane-retry-hygiene/56-01-PLAN.md`, `.planning/phases/56-shared-backoff-neutralization-and-cross-plane-retry-hygiene/56-02-PLAN.md`, `.planning/phases/56-shared-backoff-neutralization-and-cross-plane-retry-hygiene/56-03-PLAN.md`
**Phase 56 closeout:** `.planning/phases/56-shared-backoff-neutralization-and-cross-plane-retry-hygiene/56-SUMMARY.md`, `.planning/phases/56-shared-backoff-neutralization-and-cross-plane-retry-hygiene/56-VERIFICATION.md`
**Immediate focus after closeout:** archive `v1.9` or seed the next milestone from the updated residual ledger
**Requirements basket:** `RES-13`, `ARC-09`, `GOV-40`
**Next route after Phase 56:** `$gsd-complete-milestone v1.9`

## Planned Milestone (v1.8)

**Name:** `v1.8 Operational Continuity Automation, Formal-Root Sustainment & Hotspot Round 2`

**Why now:** `Phase 46 -> 50` 已证明仓库主链正确且可持续精修；当前最高杠杆问题已不再是“再做一次大审计”，而是把 continuity automation、governance-registry projection、verify-only release rehearsal，以及 canonical formal roots / helper hotspots / mega-tests 的 second-round sustainment 路线正式化。

**North-star fit:** `v1.8` 继续沿单一正式主链推进：

- 不恢复第二套 root / public surface / compat shell，只继续 inward slimming canonical homes
- 先补 continuity automation、registry projection 与 release rehearsal resilience，再继续 formal-root / helper hotspot 限流
- 不把 helper hotspot 或 mega-test topicization 讲成新架构；只是把现有 formal home 收得更窄、更稳
- typing / tests 继续作为 machine-checkable sustainment contract，而不是 prose-only aspiration

**Phase range:** `Phase 51 -> 55`
**Current status:** `Phase 51 -> 55 complete (2026-03-21)`（`GOV-38 / GOV-39 / QLT-18 / ARC-08 / HOT-12 / HOT-13 / TST-10 / TYP-13` 已全部通过 governance/docs/workflow/protocol/runtime/helper/test/typing closeout 收口）
**Seed input:** `.planning/reviews/V1_8_MILESTONE_SEED.md`
**Phase 51 planning assets:** `.planning/phases/51-continuity-automation-governance-registry-projection-and-release-rehearsal-hardening/51-CONTEXT.md`, `.planning/phases/51-continuity-automation-governance-registry-projection-and-release-rehearsal-hardening/51-RESEARCH.md`, `.planning/phases/51-continuity-automation-governance-registry-projection-and-release-rehearsal-hardening/51-VALIDATION.md`, `.planning/phases/51-continuity-automation-governance-registry-projection-and-release-rehearsal-hardening/51-01-PLAN.md`, `.planning/phases/51-continuity-automation-governance-registry-projection-and-release-rehearsal-hardening/51-02-PLAN.md`, `.planning/phases/51-continuity-automation-governance-registry-projection-and-release-rehearsal-hardening/51-03-PLAN.md`
**Phase 51 closeout:** `.planning/phases/51-continuity-automation-governance-registry-projection-and-release-rehearsal-hardening/51-SUMMARY.md`, `.planning/phases/51-continuity-automation-governance-registry-projection-and-release-rehearsal-hardening/51-VERIFICATION.md`
**Phase 52 planning assets:** `.planning/phases/52-protocol-root-second-round-slimming-and-request-policy-isolation/52-CONTEXT.md`, `.planning/phases/52-protocol-root-second-round-slimming-and-request-policy-isolation/52-RESEARCH.md`, `.planning/phases/52-protocol-root-second-round-slimming-and-request-policy-isolation/52-VALIDATION.md`, `.planning/phases/52-protocol-root-second-round-slimming-and-request-policy-isolation/52-01-PLAN.md`, `.planning/phases/52-protocol-root-second-round-slimming-and-request-policy-isolation/52-02-PLAN.md`, `.planning/phases/52-protocol-root-second-round-slimming-and-request-policy-isolation/52-03-PLAN.md`
**Phase 52 closeout:** `.planning/phases/52-protocol-root-second-round-slimming-and-request-policy-isolation/52-SUMMARY.md`, `.planning/phases/52-protocol-root-second-round-slimming-and-request-policy-isolation/52-VERIFICATION.md`
**Phase 53 planning assets:** `.planning/phases/53-runtime-and-entry-root-second-round-throttling/53-CONTEXT.md`, `.planning/phases/53-runtime-and-entry-root-second-round-throttling/53-RESEARCH.md`, `.planning/phases/53-runtime-and-entry-root-second-round-throttling/53-VALIDATION.md`, `.planning/phases/53-runtime-and-entry-root-second-round-throttling/53-01-PLAN.md`, `.planning/phases/53-runtime-and-entry-root-second-round-throttling/53-02-PLAN.md`, `.planning/phases/53-runtime-and-entry-root-second-round-throttling/53-03-PLAN.md`
**Phase 53 closeout:** `.planning/phases/53-runtime-and-entry-root-second-round-throttling/53-SUMMARY.md`, `.planning/phases/53-runtime-and-entry-root-second-round-throttling/53-VERIFICATION.md`
**Phase 54 planning assets:** `.planning/phases/54-helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families/54-CONTEXT.md`, `.planning/phases/54-helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families/54-RESEARCH.md`, `.planning/phases/54-helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families/54-VALIDATION.md`, `.planning/phases/54-helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families/54-01-PLAN.md`, `.planning/phases/54-helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families/54-02-PLAN.md`, `.planning/phases/54-helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families/54-03-PLAN.md`, `.planning/phases/54-helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families/54-04-PLAN.md`
**Phase 54 closeout:** `.planning/phases/54-helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families/54-SUMMARY.md`, `.planning/phases/54-helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families/54-VERIFICATION.md`
**Phase 55 planning assets:** `.planning/phases/55-mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification/55-CONTEXT.md`, `.planning/phases/55-mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification/55-RESEARCH.md`, `.planning/phases/55-mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification/55-VALIDATION.md`, `.planning/phases/55-mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification/55-01-PLAN.md`, `.planning/phases/55-mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification/55-02-PLAN.md`, `.planning/phases/55-mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification/55-03-PLAN.md`, `.planning/phases/55-mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification/55-04-PLAN.md`, `.planning/phases/55-mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification/55-05-PLAN.md`
**Phase 55 closeout:** `.planning/phases/55-mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification/55-SUMMARY.md`, `.planning/phases/55-mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification/55-VERIFICATION.md`
**Immediate focus after closeout:** archive `v1.8` or seed the next milestone from the completed evidence bundle
**Requirements basket:** `GOV-38`, `GOV-39`, `QLT-18`, `ARC-08`, `HOT-12`, `HOT-13`, `TST-10`, `TYP-13`
**Next route after Phase 55:** `$gsd-new-milestone`

## Completed Follow-up Milestone (v1.7)

**Name:** `v1.7 Full-Spectrum Repository Audit, Open-Source Maturity & Remediation Routing`

**Why it mattered:** `v1.6` 已把 delivery trust、boundary decoupling、governance noise 与热点拆薄推进到 archived / evidence-ready；`v1.7` 则完成覆盖全仓 Python / docs / config / tests / governance assets 的终极审阅，并把高价值整改路线正式化为 `Phase 47 -> 50`。

**North-star fit:** `v1.7` 没有引入新架构，而是用 promoted audit evidence + focused follow-up phases 继续验证单一北极星主链的先进性、缺陷与 sustainment debt。

**Phase range:** `Phase 46 -> 50`
**Current status:** `Phase 46 -> 50 complete (2026-03-21)`（`Phase 46` audit package、`Phase 47` continuity/docs/tooling closeout、`Phase 48` formal-root hotspot decomposition、`Phase 49` mega-test topicization/failure-localization hardening 与 `Phase 50` REST typed-surface / ownership convergence 均已落盘并通过验证）
**Formalized follow-up route:** `Phase 47 -> 50`（由 `46-REMEDIATION-ROADMAP.md` 升格为正式 roadmap entries）
**Promoted audit package:** `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-AUDIT.md`, `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-SCORE-MATRIX.md`, `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-REMEDIATION-ROADMAP.md`, `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-SUMMARY.md`, `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-VERIFICATION.md`
**Promoted follow-up closeout:** `.planning/phases/47-continuity-contract-governance-entrypoint-compression-and-tooling-discoverability/47-SUMMARY.md`, `.planning/phases/47-continuity-contract-governance-entrypoint-compression-and-tooling-discoverability/47-VERIFICATION.md`, `.planning/phases/48-runtime-access-and-formal-root-hotspot-decomposition-without-public-surface-drift/48-SUMMARY.md`, `.planning/phases/48-runtime-access-and-formal-root-hotspot-decomposition-without-public-surface-drift/48-VERIFICATION.md`, `.planning/phases/49-mega-test-topicization-and-failure-localization-hardening/49-SUMMARY.md`, `.planning/phases/49-mega-test-topicization-and-failure-localization-hardening/49-VERIFICATION.md`, `.planning/phases/50-rest-typed-surface-reduction-and-command-result-ownership-convergence/50-SUMMARY.md`, `.planning/phases/50-rest-typed-surface-reduction-and-command-result-ownership-convergence/50-VERIFICATION.md`
**Next route source:** `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-REMEDIATION-ROADMAP.md`

## Archived Milestone (v1.5)

**Name:** `v1.5 Governance Truth Consolidation & Control-Surface Finalization`

**Why now:** `v1.4` 已经把 release trust、control-home truth、热点瘦身与 mega-test 拆分推进到 archived / evidence-ready，但 fresh audit 仍发现两类仍值得正式路由的尾债：一是 authority precedence / archive snapshot / derived-map identity 的口径没有完全同步；二是 `runtime_access` / diagnostics / device lookup / maintenance / schedule execution 之间还残留少量 duplicated read-model 与 auth/error chain。

**North-star fit:** `v1.5` 不是新架构，而是继续沿现有单一正式主链推进：

- 不重开 `compat shell`、`legacy client` 或第二 protocol/runtime/control root
- 不把 `.planning/milestones/*.md` 或 `.planning/codebase/*.md` 误升为 active truth
- 不让 control/services 重新各自复制 runtime locator / device read-model / auth-error semantics
- 不用“兼容壳保留”来掩盖 stale naming、forwarding residue 或 governance drift

**Phase range:** `Phase 40`
**Current status:** `Phase 40 archived`（seven executable plans executed, validated, audited, and archived on `2026-03-19`; next action is `$gsd-new-milestone`）
**Primary closeout targets:** authority layering、machine-readable governance truth、runtime-access read-model convergence、shared service execution contract、touched naming residue 收口。
**Archive assets:** `.planning/v1.5-MILESTONE-AUDIT.md`, `.planning/reviews/V1_5_EVIDENCE_INDEX.md`, `.planning/milestones/v1.5-ROADMAP.md`, `.planning/milestones/v1.5-REQUIREMENTS.md`, `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-SUMMARY.md`, `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-VERIFICATION.md`, `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-VALIDATION.md`, local tag `v1.5`

## Archived Milestone (v1.4)

**Name:** `v1.4 Sustainment, Trust Gates & Final Hotspot Burn-down`

**Why it mattered:** `v1.3` 的 formal gap 虽已关闭，但显式 retained tech debt 仍需要一次独立里程碑来完成最终收口；`Phase 34 -> 39` 已把 continuity、release trust、protocol/runtime root、quality-signal、governance current story 与 mega-test topology 全部推进到 shipped / archived。

**North-star fit:** 当前里程碑继续沿单一正式主链推进：

- 不创建第二个 runtime / protocol root
- 不把 `services/` 回写成 control-plane formal home
- 不让 replay/fixture/readme 形成第二 authority truth
- 不把 compat / legacy / placeholder story 重新合法化

**Milestone outcomes:**

1. continuity / release trust、protocol/runtime hotspots 与 typed exception hardening 已完成 fresh-audit 收口
2. `custom_components/lipro/control/` 已在 north-star、developer docs、reviews 与 guards 中被固定为 formal control-plane home
3. governance current story、promoted assets、dead-shell retirement 与 mega-test decomposition 已全部同步到 Phase 39 closeout evidence

**Phase range:** `Phase 34 -> 39`

**Execution status:** `Phase 34-39 complete / archived`
**Archive assets:** `.planning/v1.4-MILESTONE-AUDIT.md`, `.planning/reviews/V1_4_EVIDENCE_INDEX.md`, `.planning/milestones/v1.4-ROADMAP.md`, `.planning/milestones/v1.4-REQUIREMENTS.md`, `.planning/phases/39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition/39-SUMMARY.md`, `.planning/phases/39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition/39-VERIFICATION.md`, local tag `v1.4`
**Historical archive assets:** `.planning/milestones/v1.1-ROADMAP.md`, `.planning/milestones/v1.1-REQUIREMENTS.md`, `.planning/milestones/v1.2-ROADMAP.md`, `.planning/milestones/v1.2-REQUIREMENTS.md`, `.planning/milestones/v1.4-ROADMAP.md`, `.planning/milestones/v1.4-REQUIREMENTS.md`

## v1.3 Closeout & Post-closeout Continuation

**Route-freeze status:** `Phase 25 -> 37` 已于 `2026-03-18` 全部执行完成；`Phase 38` 也已在同日作为 fresh-audit next tranche 落地，关闭最后一条 active residual family，并把 quality-signal / governance closeout baseline 收紧到更诚实的 machine-checkable story。

**Continuation closeout status:** `Phase 32 -> 37` 的 execution / verification 资产已全部落地，`38-VERIFICATION.md` / `38-SUMMARY.md` 现进一步构成 fresh-audit follow-through evidence chain：`.planning/v1.3-HANDOFF.md` 继续作为 `Phase 25 -> 31` 历史 closeout baseline，`33-VERIFICATION.md` / `33-SUMMARY.md` 负责承接 post-v1.3 continuation closeout，而 `34-VERIFICATION.md` / `35-VERIFICATION.md` / `36-VERIFICATION.md` / `37-VERIFICATION.md` / `38-VERIFICATION.md` 则共同构成 post-closeout quality hardening baseline。若继续追求 10 分质量，下一步应从新的 fresh-audit tranche 继续起相，而不是回退到旧 handoff 语境。

**Parent phase:** `Phase 25 — Quality-10 remediation master plan and execution routing`

**Route map:**
1. `Phase 25.1` — snapshot atomicity and refresh arbitration
2. `Phase 25.2` — telemetry formal-surface closure and planning-truth sync
3. `Phase 26` — release trust chain and open-source productization hardening
4. `Phase 27` — hotspot slimming, dependency strategy and maintainability follow-through
5. `Phase 28` — release trust gate completion and maintainer resilience
6. `Phase 29` — REST child-façade slimming and test topicization
7. `Phase 30` — protocol/control typed contract tightening
8. `Phase 31` — runtime/service typed budget and exception closure
9. `Phase 32` — truth convergence, gate honesty, and quality-10 closeout

**Review coverage promise:**
- `P0` 安装/发布 trust chain → `Phase 26`
- `P0` snapshot partial-failure correctness → `Phase 25.1`
- `P0` telemetry `coordinator.client` ghost seam → `Phase 25.2`
- `P1` giant roots / pure forwarding layers → `Phase 27`
- `P1` dependency / compatibility / support strategy → `Phase 26` + `Phase 27`
- `P1` governance drift / derived-map honesty → `Phase 25.2`
- `P1` 单维护者 / 双语 / 支持矩阵 / 产品化不足 → `Phase 26`
- `P2` naming residue / phase narration / local persistence-observability follow-through → `Phase 27`
- `P1/P2` maintainer continuity / release identity hardening / operational governance debt → `Phase 28`
- `P1/P2` remaining REST hotspot / child-façade overload / second-wave mega-test topicization / residual honesty debt → `Phase 29`
- `P1/P2` protocol/control typed contract tightening / broad-catch arbitration debt → `Phase 30`
- `P1/P2` runtime/service typed backlog / exception closure / no-growth governance debt → `Phase 31`
- planning truth convergence / requirement traceability / supersession notes → `Phase 32`
- repo-wide `ruff` / `mypy` / CI / docs gate honesty → `Phase 32`
- release identity / code-scanning defer / maintainer continuity / contributor template convergence → `Phase 32`
- `.planning/codebase` freshness / derived-map disclaimer / bilingual public-doc sync → `Phase 32`
- giant roots / giant governance scripts / mega-test topicization → `Phase 32`
- typed debt / broad-catch / fallback-legacy-phase residue follow-through → `Phase 32`

**Explicit clarification:**
- reverse-engineered vendor login flow 中要求的 `MD5` 哈希口令路径，按当前认知属于**上游协议约束**，不是本仓库单独可消灭的“弱密码学债”；除非后续确认存在可替换的上游协议路径，否则不把它登记为仓库内部独立交付目标。
- `AES-ECB` / `SHA1` 一类协议受限实现也只在“可替换协议已被证实”时才升级为重构目标；当前先以边界隔离与诚实记录为准。
- `Phase 32` 只处理仓库可裁决的 truth / gate / hotspot debt；不会把上游协议未证实可替换的实现伪装成仓库内部“马上可消灭”的重构目标。

## Phase 33 Audit-Driven Continuation

**Why now:** `Phase 25 -> 32` 关闭了旧 P0，但最新全仓终审仍明确留下了一簇 repo-internal hardening debt：runtime contract 双真源、control 回路、giant roots / forwarding layers、broad-catch arbitration、CI/perf gate drift、dependency reproducibility、deep-doc bilingual parity 与 maintainer continuity。

**Execution promise:** `Phase 33` 不是第二套路线图，而是把上述 remaining P1/P2 全量压进单一正式主链上的下一轮 hardening tranche；任何交付都必须继续沿 `protocol / control / runtime / services / tests / docs` 现有 homes 推进。

**Execution result:**
- `33-01 / 33-02` 已关闭 runtime contract dual-truth、control reflection loop、snapshot leakage 与 over-wide exports。
- `33-03 / 33-04` 已继续切薄 giant roots，并把 exception policy / typed debt / naming residue 收口成更少、更诚实的 arbitration points。
- `33-05 / 33-06` 已收紧 CI/pre-push/benchmark/release evidence truth、dependency posture、deep-doc parity、maintainer continuity 与 mega-test topicization。





## v1.4 Route & Hardening Updates

**Why now:** `v1.3` 现在的真实状态不是“缺少 formal gap closure”，而是“requirements 与审计闭环已完成，但 retained tech debt 仍值得再打一轮”。因此下一步更合理的语义不是继续把 tranche 塞回 `v1.3`，而是把它们提升为 `v1.4` 的新目标：连续性冗余、硬 release gate、协议/运行根热点继续瘦身、宽异常继续 burn-down、巨石测试第三波 topicization，以及 derived truth 再对齐。

**Milestone contract:** `v1.4` 继续沿现有北极星主链推进，不新建第二 root、不虚构隐藏 maintainer redundancy、不把 vendor-constrained crypto 伪装成仓库内部立刻可消灭的重构债。

**Route map:**
1. `Phase 34` — continuity and hard release gates
2. `Phase 35` — protocol hotspot final slimming
3. `Phase 36` — runtime root and exception burn-down
4. `Phase 37` — test topology and derived-truth convergence
5. `Phase 38` — external-boundary residual retirement and quality-signal hardening
6. `Phase 39` — governance current-story convergence, control-home clarification, and mega-test decomposition

**Default next step:** `$gsd-plan-phase 40` → `$gsd-execute-phase 40`

## Phase 34 Seed Hardening Update

`Phase 34` 已于 `2026-03-18` 完成：single-maintainer continuity 现有 formal custody / freeze / restoration contract；release path 已具备 tagged `CodeQL` hard gate、keyless `cosign` signing bundle、provenance verification 与同步后的 public docs truth。`v1.3` 仍保持 closeout-eligible with retained debt，而 `v1.4` seed 的默认下一步已切到 `Phase 35`。

## Phase 35 Protocol Hotspot Slimming Update

`Phase 35` 已于 `2026-03-18` 完成：`LiproRestFacade` 现通过 `RestTransportExecutor` 与 `RestEndpointSurface` inward 收口 request/endpoint 复杂度；`LiproProtocolFacade` 则通过 `rest_port.py` 与 `mqtt_facade.py` 保持 single protocol-root story，同时没有引入新的 package-level public surface。

## Phase 36 Runtime Root Burn-Down Update

`Phase 36` 已于 `2026-03-18` 完成：`CoordinatorPollingService` 已正式承接 polling/status/outlet/snapshot orchestration，`Coordinator` 继续变薄；runtime 主链上的高风险 broad catches 也已收口到 typed arbitration / fail-closed semantics，并同步回写 phase31 budget truth。

## Phase 37 Test Topology & Derived-Truth Update

`Phase 37` 已于 `2026-03-18` 完成：`test_init_service_handlers*`、`test_init_runtime*` 与 `test_governance_phase_history*` 已 topicize 成稳定专题套件；`.planning/codebase/*`、`VERIFICATION_MATRIX`、`CONTRIBUTING.md` 与相关 drift guards 也已回写到同一条 topology truth。

## Phase 38 External-Boundary Residual & Quality-Signal Hardening Update

`Phase 38` 已于 `2026-03-18` 完成：最后一条 active residual family（`External-boundary advisory naming`）已关闭；firmware authority truth 现统一为 bundled local trust-root asset + remote advisory payload；`coverage_diff.py` / CI / `CONTRIBUTING.md` / `.planning/codebase/TESTING.md` 现讲同一条 floor-only + explicit-baseline-diff + advisory-with-artifact 故事，而 governance closeout guards 也进一步收敛到 `ROADMAP` / `REQUIREMENTS` / command anchors。

## Phase 39 Governance Current-Story & Mega-Test Closeout Update

`Phase 39` 已于 `2026-03-19` 完成并在同日完成 milestone archive promotion：`ROADMAP / REQUIREMENTS / STATE / PROJECT` 的 current story 已从 `closeout-ready` 升格为 shipped / archived；`docs/NORTH_STAR_TARGET_ARCHITECTURE.md` 与 `docs/developer_architecture.md` 已刷新 control-home truth；`custom_components/lipro/core/protocol/compat.py` 已删除；authority fixtures / replay manifests / guards 已完成单命名收口；device / mqtt / flows / anonymous-share / governance 套件继续 topicize，并留下 promoted closeout evidence。

## Why This Milestone Exists

`v1.0` 已完成北极星主链重建，但还缺少几类“高杠杆正式能力”：

- protocol boundary schema / decoder family，让外部输入在边界被统一规范化
- architecture enforcement，把北极星裁决从文档提升为可自动阻断的规则链
- runtime telemetry exporter，把当前 snapshot/diagnostics 进化为正式导出面
- protocol replay / simulator harness，把逆向协议证据沉淀为可重复回放的 assurance asset
- AI debug evidence pack：把 telemetry/replay/边界库存统一导出为“可给 AI 分析”的脱敏证据包

这些能力不是孤立功能，而是为了让仓库进入下一阶段：

- **协议变更可被回放与比对**
- **结构回退可被规则自动拦截**
- **运行信号能被正式导出，而不是散落在 diagnostics 里**
- **AI 可分析优先**：telemetry/export/replay/evidence 的产物必须机器友好（结构化、稳定 schema、可版本化、带时间戳、带事件序列），同时严格脱敏。

## Current Foundation Before v1.2

### 1. Boundary Truth 更严格

- protocol boundary family 成为 decode authority 的正式归属
- REST / MQTT 进入 runtime 前，必须先落 canonical contract
- schema / decoder / authority / fixture / drift detection 形成统一链路

### 2. Architecture Policy 更可执行

- 北极星约束不再只存在于文档里
- plane / root / public surface / authority / residual 规则可由 CI 与 meta tests 执行
- 双主链、compat 回流、跨层直连与 raw payload leakage 被更早阻断

### 3. Telemetry / Replay / Evidence 形成 assurance 主链

- telemetry exporter 收口 runtime/protocol 的正式运维信号
- replay harness 用正式 public path 回放协议样本
- evidence pack 从正式真源 pull 结构化证据给 AI 调试与分析

### 4. Residual Surface 更收敛

- protocol formal public surface 已显式化；child-defined contract 与 compat export 不再反向定义正式主链
- runtime 对设备集合的正式访问已收口为只读 view / formal primitive
- outlet power 已进入正式 primitive；remaining compat seam 只能作为显式 residual 存在

### 5. API Drift Isolation / Core Boundary Prep 已完成

- `rest.device-list` / `rest.device-status` / `rest.mesh-group-status` 已在 protocol boundary 输出 canonical contract
- `AuthSessionSnapshot` 已成为 host-neutral auth/session truth；`config_flow` / `entry_auth` 不再依赖 raw login dict
- `core/__init__.py` 已不再导出 `Coordinator`；HA runtime home 继续固定在 `custom_components/lipro/coordinator_entry.py`

### 6. Phase 11 Control / Runtime / OTA / Governance 收口已完成

- `control/service_router.py` 已成为 formal control-plane service callback home，`services/wiring.py` compat shell 已删除
- runtime-access / diagnostics / status isolation 已统一到 `control/runtime_access.py` 与 formal runtime contract
- supplemental entity truth、firmware update projection 与 OTA helper cluster 已收敛为单一正式故事线
- release / CI / issue / PR / security disclosure / phase assets 已形成一致的开源治理口径

### 7. Phase 12 Type / Residual / Governance 收口已完成

- `uv run mypy` 已恢复全绿，typed runtime / REST / diagnostics 合同重新与 concrete 实现对齐
- `core.api.LiproClient`、`LiproProtocolFacade.get_device_list`、`LiproMqttFacade.raw_client` 与 `DeviceCapabilities` 已从生产 public surface 清退，不再为测试保留插件 compat 入口
- `core/api/client.py` 与 device snapshot 主链继续沿 formal boundary 收薄，未引入任何第二 orchestration story
- contributor-facing docs / config / CI / community governance 已同步到当前仓库真相，shellcheck 已纳入 lint 门禁

### 8. Phase 13 显式领域表面 / 治理守卫 / 热点边界收口已完成

- `core/device/device.py`、`state.py` 与相关测试已移除动态 `__getattr__`，设备域正式表面变成显式 property / method 集合
- `core/coordinator/orchestrator.py`、`core/coordinator/lifecycle.py`、`core/api/status_service.py` 与 `control/service_router_{handlers,support}.py` 已进一步拆成更小 helper，runtime/control 内部协作者术语继续向正式 surface 收口
- README / README_zh / CONTRIBUTING / SUPPORT / CODEOWNERS / quality-scale / devcontainer 已被 meta guards 结构化校验，治理入口不再只靠文案约定

### 9. Phase 14 旧 API Spine 终局收口与治理真源归一已完成

- `core/coordinator/coordinator.py` 已把 protocol-facing runtime ops 统一收口到 `CoordinatorProtocolService`，`Coordinator.client` 不再构成合法内部术语。
- `ScheduleApiService` 与 schedule passthrough 已退出正式主链；schedule truth 固定为 `ScheduleEndpoints` + focused helpers。
- `core/api/status_fallback.py` 与 `control/developer_router_support.py` 已承接 fallback/glue 内核；`status_service.py` 与 `service_router.py` 仅保留 public orchestration / handler 身份。
- `PUBLIC_SURFACES`、`ARCHITECTURE_POLICY`、`VERIFICATION_MATRIX`、`FILE_MATRIX`、`RESIDUAL_LEDGER`、`KILL_LIST` 与 Phase 14 closeout 资产已同步到当前仓库真相。

### 10. Phase 15 支持反馈契约 / 治理真源修补 / 可维护性跟进已完成

- developer feedback upload contract 与 local debug view 已正式分家：上传保留 `iotName` 等供应商判型标识，但匿名化 `deviceName` / `name` / `roomName` / `productName` / `keyName` / IR 资产展示名等用户自定义标签。
- `PROJECT / ROADMAP / STATE / Phase 15 assets`、README / SUPPORT / SECURITY / bug template 与 source-path guards 已讲同一条完成态故事线，不再容忍死链、版本漂移或 phase-status drift。
- support hotspot typing narrowing、tooling/security arbitration 与 residual locality governance 已完成收口；`service_router.py` 仍保持 public handler home，未重开第二条正式主链。

### 11. Phase 16 后审计收口线已完成

- `Phase 16` 的 `3 waves / 6 plans` 已全部执行完成：governance/toolchain truth、control/service contract、protocol/runtime hardening、domain/entity/OTA rationalization 与 docs/test-layer closeout 已统一落地。
- 第二轮全仓审计已执行并回写到 `VERIFICATION_MATRIX.md`、`RESIDUAL_LEDGER.md` 与 `KILL_LIST.md`；remaining residual 只允许以 owner/delete-gate/evidence 清晰的本地低风险形态存在。
- `docs/TROUBLESHOOTING.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 已成为 contributor / maintainer 的唯一正式入口；`release.yml` 继续复用 CI 并从 tag ref 构建资产。
- `Phase 16` 的最终裁决仍然遵守同一禁令：不重开第二条正式主链、不做无 gate rename campaign、不把 residual cleanup 包装成物理重命名工程。

### 12. Phase 17 最终残留退役 / 类型契约收紧 / 里程碑收官已完成

- `Phase 17` 的 `3 waves / 4 plans` 已全部执行完成：API residual spine 已物理退场，`_ClientTransportMixin`、endpoint legacy mixin family、`LiproMqttClient` legacy naming、`get_auth_data()` compat projection 与 synthetic outlet-power wrapper 均已退出正式故事线。
- `session_state.py` 现只保留 `RestSessionState`；`transport_executor.py` 现只保留 `RestTransportExecutor` 与显式 transport helpers；`core/mqtt` concrete transport 名称统一到 `MqttTransport`，并由 no-export ban / locality guard fail-fast 锁定。
- `ROADMAP / REQUIREMENTS / STATE / baseline / review ledgers / AGENTS / developer_architecture / milestone audit` 已统一到同一条 final closeout story；`v1.1` 当前达到 archive-ready 水位。
- `Phase 17` 的最终裁决继续遵守同一禁令：不重开第二条正式主链、不把 cleanup 伪装成新架构、不留下 silent defer。


### 13. Phase 18 Host-Neutral Boundary Nucleus 抽取已完成

- `core/auth/bootstrap.py`、host-neutral capability/device helpers 与 adapter-only projection guards 已落地；共享 nucleus 不再吸入 Home Assistant runtime 类型。
- `ConfigEntryLoginProjection` 继续只是 HA config-entry projection；`AuthSessionSnapshot` 仍是唯一正式 auth/session truth。
- `helpers/platform.py`、`CapabilityRegistry`、`CapabilitySnapshot` 与 `LiproDevice` 的边界已固定，Phase 18 没有引入第二 protocol/runtime root。

### 14. Phase 19 Headless Consumer Proof / Adapter Demotion 已完成

- `custom_components/lipro/headless/boot.py`、`tests/harness/headless_consumer.py` 与 headless integration proof 已证明同一套 nucleus 可被非 HA consumer 复用，而不是复制第二实现。
- proof outputs 继续是 assurance-only consumer，不反向成为 authority；`LiproProtocolFacade` 与 `Coordinator` 的单一正式主链未被破坏。
- platform thin setup shells、token persistence 与 config-entry adapters 已继续 inward 收敛到 shared boot seam。

### 15. Phase 20 Remaining Boundary Family Completion 已完成

- `rest.list-envelope.v1`、`rest.schedule-json.v1`、`mqtt.topic.v1`、`mqtt.message-envelope.v1` 已全部进入 registry-backed boundary / replay / fixture / authority 主链。
- inventory / fixtures / manifests / meta guards 已不再把这些 families 记为 partial 或长期 de-scope folklore。
- governance / authority continuity 已回写，remaining-family closeout 不再依赖 helper-level implicit behavior。

### 16. Phase 21 Replay Coverage / Exception Taxonomy 收口已完成

- replay harness、evidence pack 与 replay report 现在对 remaining families 提供显式 assurance coverage，而不是只靠隐式遍历命中。
- shared failure taxonomy 已冻结到 `core/telemetry/models.py`；`failure_category`、`failure_origin`、`handling_policy`、`error_type` 与 `failure_summary` 成为统一 contract。
- protocol/runtime/control 关键 broad-catch seam 已区分 typed arbitration 与 cancellation passthrough；catch-all 不再被默许为默认策略。

### 17. Phase 22 Observability Surface Convergence 已完成

- diagnostics / system health / developer / support / evidence consumers 已统一消费 shared `failure_summary` vocabulary。
- `failure_entries` 聚合、developer report merge 路径与 exporter-backed telemetry sink 已共享同一失败语言，不再各说各话。
- verification matrix / file ownership / residual disposition 与 meta guards 已把 `OBS-03` 固化为长期治理真源。

### 18. Phase 23 Governance / Contributor Docs / Release Evidence 收口已完成

- `PROJECT / ROADMAP / REQUIREMENTS / STATE / baseline / review ledgers` 已与 `Phase 21-22` 的长期真相对齐，不再维持“已规划未执行”的漂移叙事。
- README / README_zh / CONTRIBUTING / SUPPORT / troubleshooting / maintainer runbook / issue & PR templates 现统一引用同一 support/security/troubleshooting/release evidence 故事线。
- `V1_2_EVIDENCE_INDEX.md` 已成为 maintainer / release / milestone closeout 共用的 pull-only evidence pointer；workflow 继续复用现有 CI gate，而不是另建第二套门禁故事。

### 19. Phase 24 最终里程碑审计 / 归档就绪 / v1.3 交接准备已完成

- final repo audit 已对 remaining items 给出 close / retain / defer disposition；active residual 现只保留显式登记的长期 advisory naming family，不再携带 replay/boundary coverage 悬空债务。
- `v1.2-MILESTONE-AUDIT.md`、`V1_2_EVIDENCE_INDEX.md`、`MILESTONES.md` 与 `v1.3-HANDOFF.md` 已形成 archive-ready / handoff-ready closeout bundle。
- `v1.2` 当前达到 archive-ready / `v1.3` handoff-ready 状态；下一轮维护者可直接从 handoff asset 启动，而无需依赖对话历史。

## Architectural Stance

本 milestone 继续遵守 `v1.0` 的北极星哲学，并对“先进性”做出更克制、但更正确的裁决：

### 1. 不为“先进”引入错误复杂度

明确不把以下内容作为默认正确答案：
- 全局 DI 容器
- 全局事件总线
- 重型 observability stack（Prometheus / OpenTelemetry）
- 全域 schema 框架替换

### 2. 先进性来自“更强正式边界”而非“更多基础设施”

本 milestone 的先进化重点是：
- boundary schema / decoder formalization
- executable architecture policy
- single telemetry exporter truth
- deterministic replay evidence
- AI-debug-ready evidence pack

### 3. HA-only 裁决

本仓库当前只服务 Home Assistant，不追求跨平台 SDK 抽象层。
因此新增能力都必须服务于：
- HA runtime 正式主链
- HA diagnostics / system health / services
- repo-local assurance / verification / AI debug tooling

## North Star 2.0 (AI Debug Ready, HA-only)

在 v1.1 / Phase 8 的裁决下，本仓库新增以下硬性原则：

1. **AI Debug Ready**：exporter / replay / evidence 产物必须结构化、稳定、可版本化、可回放。
2. **HA-only**：不为跨平台预留重型抽象层。
3. **Pull-first observability**：telemetry exporter 与 evidence pack 以 pull 为主，sources 可以维护有界摘要，但不建设事件总线。
4. **Pseudonymous-by-default**：允许 `entry_ref` / `device_ref` 这类报告内稳定、跨报告不可关联的伪匿名引用；真实标识、凭证等价物严禁进入正式输出。
5. **Real timestamps allowed**：真实时间戳允许用于 AI 调试与回放对齐，但仍受 redaction / cardinality / authority 约束。

## Success Definition

当当前里程碑完成时，应能同时回答以下问题：

- 一条 REST/MQTT 输入是由谁 decode、谁拥有 schema authority、由哪个 fixture 证明？
- 哪些架构回退会被 CI / meta guards 自动拦截？
- 当前 runtime/protocol 的关键运维信号，是否已通过单一 exporter 输出？
- 某个协议问题，能否通过 deterministic replay 在本地与 CI 复现？
- AI / 维护者是否能从统一 evidence pack 获得可调试、可追溯、已脱敏的证据？

## Scope

### In Scope

1. **Protocol boundary formalization**
   - schema/decoder family
   - authority / fixture / drift detection

2. **Executable architecture policy**
   - phase/root/surface/authority guards
   - fail-fast local/CI checks

3. **Runtime telemetry exporter**
   - 统一 exporter contracts / sinks / redaction / cardinality
   - diagnostics / system health / developer/CI 共用 truth

4. **Protocol replay harness**
   - deterministic replay corpus + driver
   - canonical / drift / telemetry assertions

5. **AI Debug evidence pack**
   - 从 exporter / replay / governance 真源 pull 证据
   - 输出 AI 可消费、结构化、脱敏的 pack

### Out of Scope

- 跨平台 SDK 适配层
- 全局事件总线 / 全局 DI 容器
- 与里程碑目标无直接关系的大规模换栈
- 为 replay / telemetry / evidence 再造第二套 production 实现

## Constraints

### Technical Constraints

- 必须保持 HA integration 的正式主链不被 replay/evidence 反客为主
- replay / evidence 只能作为 assurance/tooling layer
- 所有新增 public surface 都必须登记到治理真源
- 任何 residual/compat 必须显式记录 owner / phase / delete gate

### Product Constraints

- 不破坏现有可工作的 HA 集成主行为
- 新增能力必须可验证、可回滚、可阶段性交付
- 任何“为了 AI 调试”增加的数据，都必须先通过脱敏与 authority 仲裁

## Target Topology (v1.1 Extension)

1. **Protocol Plane**
   - `core/protocol/boundary/*`
   - `LiproProtocolFacade`
   - authority fixtures / decoders / contracts / replay evidence

2. **Runtime Plane**
   - `Coordinator`（runtime home = `custom_components/lipro/coordinator_entry.py`）
   - 正式 runtime services / orchestration / read-only runtime access

3. **Control Plane**
   - diagnostics / system health / services / runtime access / redaction
   - formal auth/session consumers（`AuthSessionSnapshot` / use-case results）

4. **Assurance Plane**
   - architecture guards / scripts / meta tests
   - telemetry exporter truth
   - replay harness
   - AI debug evidence pack exporter

5. **Governance Layer**
   - `.planning/baseline/*`
   - `.planning/reviews/*`
   - roadmap / requirements / state / phase summaries

## Derived Requirements To Enforce

v1.1 进入执行期后，新增演进必须额外满足：

- **边界 schema 只是 collaborator，不是新 root**
- **telemetry exporter 只是 observer，不得获得编排权**
- **replay harness 属于 assurance plane，不得复制生产主链**
- **AI evidence pack 属于 tooling export，不得变成第二 diagnostics / runtime root**
- **新依赖若引入，只允许局部落在 boundary plane，且必须有 authority / delete gate / rollback story**

## Phase 7.3-10 Arbitration

为避免 `07.3-08` 职责冲突，锁定以下仲裁：

- **`07.3` owns telemetry truth**
  - exporter contracts、redaction、cardinality、timestamp / pseudo-id compatibility 在此锁定；
  - 后续 phase 只能消费，不得私改字段语义。

- **`07.4` owns replay truth**
  - replay manifests、deterministic driver、replay assertions、run summary 在此锁定；
  - 不得改写 boundary authority 或 exporter truth。

- **`07.5` owns governance closeout**
  - 矩阵、owner、delete gate、evidence index、summary 在此锁定；
  - 不得实现 evidence pack exporter。

- **`08` owns AI debug packaging**
  - 只 pull `07.3/07.4/07.5` 正式输出；
  - 不得反向定义 telemetry / replay / governance 真源。

- **`09` owns residual surface closure**
  - formal public surface、compat seam、read-only runtime access 与 outlet-power primitive 在此锁定；
  - 不得重新把 live mutable runtime surface 或 child-defined contract 洗白成正式路径。

- **`10` owns API drift isolation / core-boundary prep**
  - high-drift boundary contracts、`AuthSessionSnapshot`、`core/__init__.py` 去 runtime-root 叙事在此锁定；
  - 未来宿主只能消费 formal boundary/auth/device nucleus，不得反向抽出 HA runtime 形成 second root。

## Execution Doctrine

### Planning Standard

- phase 先对齐 north-star authority，再开始落计划
- 每个 phase 先定 public surface / authority / verification，再写实现
- 先裁决，再迁移；先收口边界，再扩展能力

### Quality Standard

- 每条新主链都必须可观测、可验证、可回放
- 测试不只证明“能跑”，还要证明“没偏航”
- 文档、治理台账、验证证据与代码必须同轮同步

### Governance Standard

- 活跃真源只承认 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` → `.planning/*` → code/tests
- 任何 residual/compat 必须登记 owner、phase、delete gate
- milestone 切换前必须完成归档，不允许新旧里程碑共用一份活跃 roadmap truth

## Primary Sources

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/PROJECT.md`
3. `.planning/ROADMAP.md`
4. `.planning/REQUIREMENTS.md`
5. `.planning/STATE.md`
6. `.planning/baseline/*.md` 与 `.planning/baseline/GOVERNANCE_REGISTRY.json`
7. `.planning/reviews/*.md`
8. `docs/developer_architecture.md`
9. `AGENTS.md`
10. `CLAUDE.md`
11. `.planning/MILESTONES.md` 与 `.planning/milestones/*.md` 等历史归档证据

## Current Execution Workspace Inputs

- `.planning/reviews/V1_6_EVIDENCE_INDEX.md`
- `.planning/v1.6-MILESTONE-AUDIT.md`
- `.planning/milestones/v1.6-ROADMAP.md`
- `.planning/milestones/v1.6-REQUIREMENTS.md`
- `.planning/phases/45-hotspot-decomposition-and-typed-failure-semantics/45-VERIFICATION.md`
- `.planning/phases/45-hotspot-decomposition-and-typed-failure-semantics/45-SUMMARY.md`
- `.planning/reviews/V1_5_EVIDENCE_INDEX.md`
- `.planning/v1.5-MILESTONE-AUDIT.md`
- `.planning/milestones/v1.5-ROADMAP.md`
- `.planning/milestones/v1.5-REQUIREMENTS.md`
- `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-VALIDATION.md`
- `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-VERIFICATION.md`
- `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-SUMMARY.md`
- `.planning/v1.4-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_4_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.4-ROADMAP.md`
- `.planning/milestones/v1.4-REQUIREMENTS.md`

- 当前 handoff / archive 输入以 `v1.6` audit + archive bundle 为最新 shipped baseline；`.planning/phases/41-full-spectrum-architecture-code-quality-and-open-source-audit/41-REMEDIATION-ROADMAP.md` 保留为 `v1.6 / Phase 42 -> 45` 的历史路由来源。phase 目录资产仍默认是执行证据，只有被 `ROADMAP.md`、baseline docs、review ledgers 或 milestone audit 显式提升时，才成为长期治理真源。

*Last updated: 2026-03-22 after completing Phase 56 neutral-backoff closeout and promoting the current v1.9 truth*
