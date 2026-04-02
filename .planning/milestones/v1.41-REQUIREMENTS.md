# Requirements: Lipro-HASS v1.41

<!-- governance-route-contract:start -->
```yaml
contract_version: 1
contract_name: governance-route
projection_targets:
- .planning/PROJECT.md
- .planning/ROADMAP.md
- .planning/REQUIREMENTS.md
- .planning/STATE.md
- .planning/MILESTONES.md
active_milestone:
  version: v1.41
  name: Terminal Residual Audit, Remediation Charter & Maintainability Hardening
  status: active / phase 136 complete; closeout-ready (2026-04-02)
  phase: '136'
  phase_title: repo-wide terminal residual audit, hygiene fixes, and remediation charter
  phase_dir: 136-repo-wide-terminal-residual-audit-and-remediation-charter
latest_archived:
  version: v1.40
  name: Request Policy Ownership, Entity De-Reflection & Fan Truth Hardening
  status: archived / evidence-ready (2026-04-02)
  phase: '135'
  phase_title: runtime-access projection split, auth reason typing, and dispatch route
    hardening
  phase_dir: 135-runtime-access-auth-and-dispatch-contract-hardening
  audit_path: .planning/v1.40-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_40_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.39
  name: Governance Recovery, Runtime Consistency & Public Contract Correction
  evidence_path: .planning/reviews/V1_39_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.41 active milestone route / starting from latest archived baseline
    = v1.40
  default_next_command: $gsd-complete-milestone v1.41
  latest_archived_evidence_pointer: .planning/reviews/V1_40_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->
## Current Milestone (v1.41)

**Milestone Goal:** 基于 `v1.40` latest archived baseline，完成一次不遗漏 Python/docs/config/governance 的 repo-wide terminal residual audit，形成 remediation charter，并通过首批 hygiene fixes 验证审查结论与生产代码收口保持一致。
**Milestone status:** `active / phase 136 complete; closeout-ready (2026-04-02)`
**Current route mode:** `v1.41 active milestone route / starting from latest archived baseline = v1.40`
**Starting baseline:** `.planning/v1.40-MILESTONE-AUDIT.md, .planning/reviews/V1_40_EVIDENCE_INDEX.md, .planning/milestones/v1.40-ROADMAP.md, .planning/milestones/v1.40-REQUIREMENTS.md`
**Requirements basket:** `AUD-08, GOV-91, DOC-19, ARC-45, QLT-58, TST-56`
**Latest archived baseline:** `v1.40`
**Archive pointer:** `.planning/reviews/V1_40_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.40-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-complete-milestone v1.41`
**Current phase handoff:** `Phase 136 的 audit / charter / hygiene-fix / governance-sync 三条执行轨均已完成；下一步为 $gsd-complete-milestone v1.41。`

### Terminal Audit & Governance
- [x] **AUD-08**: 必须形成 repo-wide terminal audit verdict home，覆盖 Python hotspot、命名、边界、日志安全、类型残留、目录/治理/开源 readiness，并给出 severity / rationale / remediation。 
- [x] **GOV-91**: `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`、`GOVERNANCE_REGISTRY.json`、`VERIFICATION_MATRIX.md`、developer/runbook route note 与 current-route guards 必须共同承认 `v1.41 active milestone route / starting from latest archived baseline = v1.40`，并把 `Phase 136` 作为唯一 active phase。

### Architecture & Quality
- [x] **DOC-19**: `V1_41_TERMINAL_AUDIT_REPORT.md` 与 `V1_41_REMEDIATION_CHARTER.md` 必须成为单一 pullable 审阅真源，不再依赖零散对话记忆或 phase summary 拼接。
- [x] **ARC-45**: 审查必须明确列出 formal-home hotspot decomposition 的优先级与边界，包括 mega-facade、auth manager、device facade 与 stringly command 语义的后续处理路线。
- [x] **QLT-58**: 本轮必须至少消除一类已识别策略漂移；当前要求统一 vendor MD5 compatibility helper，并把部分原始异常日志收回到 `safe_error_placeholder`。
- [x] **TST-56**: focused governance/meta guards 与 targeted unit tests 必须承认 `v1.41` / `Phase 136` current route，并验证本轮 hygiene fixes 没有破坏既有 outward contract。

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUD-08 | Phase 136 | Complete |
| GOV-91 | Phase 136 | Complete |
| DOC-19 | Phase 136 | Complete |
| ARC-45 | Phase 136 | Complete |
| QLT-58 | Phase 136 | Complete |
| TST-56 | Phase 136 | Complete |

## Coverage

- v1.41 requirements: 6 total
- Current mapped: 6
- Current complete: 6
- Current pending: 0

## Latest Archived Milestone (v1.40)

**Milestone Goal:** 基于 `v1.39` latest archived baseline，先完成 RequestPolicy pacing ownership、entity projection de-reflection 与 fan preset truth 收口，再把 `runtime_access.py`、`auth_service.py` 与 `dispatch.py` 的剩余 sanctioned hotspot 继续压回 typed / thin / support-split 主链。 
**Milestone status:** `archived / evidence-ready (2026-04-02)`
**Current route mode:** `no active milestone route / latest archived baseline = v1.40`
**Starting baseline:** `.planning/v1.39-MILESTONE-AUDIT.md, .planning/reviews/V1_39_EVIDENCE_INDEX.md, .planning/milestones/v1.39-ROADMAP.md, .planning/milestones/v1.39-REQUIREMENTS.md`
**Requirements basket:** `GOV-90, ARC-43, HOT-62, HOT-63, QLT-56, TST-54, ARC-44, HOT-64, HOT-65, HOT-66, QLT-57, TST-55`
**Latest archived baseline:** `v1.40`
**Archive pointer:** `.planning/reviews/V1_40_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.40-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Current phase handoff:** `Milestone closeout complete；Phase 134 -> 135 的 requirement coverage、summary / verification / validation / audit / evidence index 已冻结为 latest archived baseline truth。`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.40`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.39`

### Governance Ownership
- [x] **GOV-90**: `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 与 `GOVERNANCE_REGISTRY.json` 必须共同承认 `v1.40 active milestone route / starting from latest archived baseline = v1.39`，并把 `Phase 134 -> 135` 作为当前 active milestone 范围、`$gsd-complete-milestone v1.40` 作为默认下一步。

### RequestPolicy / Entity Architecture
- [x] **ARC-43**: `custom_components/lipro/core/api/request_policy.py` 必须把 pacing caches / busy counters / target locks 收回单一实例 owner；`request_policy_support.py` 只保留 support helpers，不再让 mutable pacing state 以 parallel dict 参数形式四处流动。
- [x] **HOT-62**: `custom_components/lipro/entities/descriptors.py`、`custom_components/lipro/light.py` 与 `custom_components/lipro/binary_sensor.py` 必须移除 dotted-path/getattr 反射，改为显式 resolver / state-reader projection。
- [x] **HOT-63**: `custom_components/lipro/fan.py` 的 unknown `fanMode` 不能再 fallback 成 `cycle`；preset / supported_features / behavior tests 必须维持 truthful 一致投影。

### Runtime Hotspot Final Hardening
- [x] **ARC-44**: `custom_components/lipro/control/runtime_access.py` 必须继续薄化为 outward import home；runtime snapshot / diagnostics projection coercion 必须委托给 support surface，而不是继续在 import home 中膨胀。
- [x] **HOT-64**: `custom_components/lipro/runtime_types.py`、`custom_components/lipro/core/coordinator/services/auth_service.py` 与 `custom_components/lipro/services/execution.py` 必须围绕单一 typed reauth reason contract 协作。
- [x] **HOT-65**: `custom_components/lipro/core/command/dispatch.py` 的 route contract 必须采用 enum-backed canonical form，不再以裸字符串作为唯一正式表达。
- [x] **HOT-66**: sender / runtime command orchestration 必须承认新的 dispatch route canonical form，避免 stringly route 在下游继续漂移。

### Quality / Verification
- [x] **QLT-56**: developer architecture、maintainer runbook、public-surface meta guards 与 phase assets 必须同步描述 Phase 134 的 owner/projection truth，避免 route/docs/guards 各讲一套。
- [x] **TST-54**: focused `pytest`/meta/ruff lane 必须覆盖 RequestPolicy ownership、entity de-reflection、fan truth 与 `v1.40` 当前治理路由。
- [x] **QLT-57**: Phase 135 完成后，`runtime_access` support split、typed reauth reason 与 enum-backed route 必须有 focused architecture guard 防回流。
- [x] **TST-55**: focused `pytest`/meta/ruff lane 必须覆盖 runtime_access/auth_service/dispatch 以及 reopened `v1.40` current-route truth。

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| GOV-90 | Phase 134 | Complete |
| ARC-43 | Phase 134 | Complete |
| HOT-62 | Phase 134 | Complete |
| HOT-63 | Phase 134 | Complete |
| QLT-56 | Phase 134 | Complete |
| TST-54 | Phase 134 | Complete |
| ARC-44 | Phase 135 | Complete |
| HOT-64 | Phase 135 | Complete |
| HOT-65 | Phase 135 | Complete |
| HOT-66 | Phase 135 | Complete |
| QLT-57 | Phase 135 | Complete |
| TST-55 | Phase 135 | Complete |

## Coverage

- v1.40 requirements: 12 total
- Current mapped: 12
- Current complete: 12
- Current pending: 0

## Historical Traceability Appendix

为保持 archived continuity guards 与历史 requirement mapping 的单一叙事，保留以下已归档 traceability 锚点：

| Requirement | Phase | Status |
|-------------|-------|--------|
| HOT-14 | Phase 60 | Complete |
| TST-12 | Phase 60 | Complete |
| GOV-44 | Phase 60 | Complete |

## Previous Archived Milestone (v1.39)

**Milestone Goal:** 基于 `v1.38` latest archived baseline，先恢复 current governance lane 的 route/source-path/projection 一致性，再为 runtime consistency 与 public contract correction 建立单一执行入口，不再把 sanctioned hotspot 混写进 docs-only closeout。
**Milestone status:** `archived / evidence-ready (2026-04-02)`
**Current route mode:** `no active milestone route / latest archived baseline = v1.39`
**Starting baseline:** `.planning/v1.38-MILESTONE-AUDIT.md, .planning/reviews/V1_38_EVIDENCE_INDEX.md, .planning/milestones/v1.38-ROADMAP.md, .planning/milestones/v1.38-REQUIREMENTS.md`
**Requirements basket:** `GOV-89, ARC-42, HOT-61, DOC-18, QLT-55, TST-53`
**Latest archived baseline:** `v1.39`
**Archive pointer:** `.planning/reviews/V1_39_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.39-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Current phase handoff:** `Milestone closeout complete；Phase 133 的 requirement coverage、summary / verification / validation / audit / evidence index 已冻结为 latest archived baseline truth。`

## Previous Archived Milestone (v1.38)


**Milestone Goal:** 基于 `v1.37` latest archived baseline，压缩 current selector / archive boundary / docs-first governance story，把 route-marker / promoted-asset / handoff smoke 的重复断言压回 shared helper 与单一 canonical source。
**Milestone status:** `archived / evidence-ready (2026-04-02)`
**Current route mode:** `no active milestone route / latest archived baseline = v1.38`
**Starting baseline:** `.planning/v1.37-MILESTONE-AUDIT.md, .planning/reviews/V1_37_EVIDENCE_INDEX.md, .planning/milestones/v1.37-ROADMAP.md, .planning/milestones/v1.37-REQUIREMENTS.md`
**Requirements basket:** `AUD-07, GOV-88, DOC-17, OSS-19, QLT-54, TST-52`
**Latest archived baseline:** `v1.38`
**Archive pointer:** `.planning/reviews/V1_38_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.38-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Current phase handoff:** `Milestone closeout complete；Phase 132 的 requirement coverage、summary / verification / validation / audit / evidence index 已冻结为 archived baseline truth。`

## Historical Archived Milestone (v1.37)

**Milestone Goal:** 基于 `v1.36` latest archived baseline，先完成一次不遗漏 Python/docs/config/governance 切面的 repo-wide terminal audit，再把首批 repo-internal hotspots（REST fallback / runtime-command / firmware-update）继续 inward decomposition，最后把 open-source continuity / private fallback reality 诚实固化为治理决策边界与最终审阅报告。
**Milestone status:** `archived / evidence-ready (2026-04-01)`
**Current route mode:** `no active milestone route / latest archived baseline = v1.37`
**Starting baseline:** `.planning/v1.36-MILESTONE-AUDIT.md, .planning/reviews/V1_36_EVIDENCE_INDEX.md, .planning/milestones/v1.36-ROADMAP.md, .planning/milestones/v1.36-REQUIREMENTS.md`
**Requirements basket:** `AUD-06, ARC-40, HOT-59, TST-50, QLT-52, ARC-41, HOT-60, TST-51, GOV-87, DOC-16, OSS-18, QLT-53`
**Latest archived baseline:** `v1.37`
**Archive pointer:** `.planning/reviews/V1_37_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.37-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Current phase handoff:** `Milestone closeout complete；Phase 129 -> 131 的 requirement coverage、summary / verification / audit / evidence index 已冻结为 archived evidence frozen。`

## Historical Archived Milestone (v1.35)
