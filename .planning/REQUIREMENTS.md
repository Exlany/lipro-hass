# Requirements: Lipro-HASS v1.40

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
  version: v1.40
  name: Request Policy Ownership, Entity De-Reflection & Fan Truth Hardening
  status: active / phase 134 complete; closeout-ready (2026-04-02)
  phase: '134'
  phase_title: request-policy ownership, entity de-reflection, and fan truth hardening
  phase_dir: 134-request-policy-ownership-entity-de-reflection-and-fan-truth-hardening
  route_mode: v1.40 active milestone route / starting from latest archived baseline = v1.39
latest_archived:
  version: v1.39
  name: Governance Recovery, Runtime Consistency & Public Contract Correction
  status: archived / evidence-ready (2026-04-02)
  phase: '133'
  phase_title: governance recovery, runtime consistency, and public contract correction
  phase_dir: 133-governance-recovery-runtime-consistency-and-public-contract-correction
  audit_path: .planning/v1.39-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_39_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.38
  name: Governance Story Compression, Archive Segregation & Public Entry Simplification
  evidence_path: .planning/reviews/V1_38_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.40 active milestone route / starting from latest archived baseline = v1.39
  default_next_command: $gsd-complete-milestone v1.40
  latest_archived_evidence_pointer: .planning/reviews/V1_39_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->
## Current Milestone (v1.40)

**Milestone Goal:** 基于 `v1.39` latest archived baseline，把 RequestPolicy pacing ownership、entity projection de-reflection 与 fan preset truth 收束到同一条 active milestone 主链，并把 docs/guards/tests 同步推进到 closeout-ready。
**Milestone status:** `active / phase 134 complete; closeout-ready (2026-04-02)`
**Current route mode:** `v1.40 active milestone route / starting from latest archived baseline = v1.39`
**Starting baseline:** `.planning/v1.39-MILESTONE-AUDIT.md, .planning/reviews/V1_39_EVIDENCE_INDEX.md, .planning/milestones/v1.39-ROADMAP.md, .planning/milestones/v1.39-REQUIREMENTS.md`
**Requirements basket:** `GOV-90, ARC-43, HOT-62, HOT-63, QLT-56, TST-54`
**Latest archived baseline:** `v1.39`
**Archive pointer:** `.planning/reviews/V1_39_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.39-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-complete-milestone v1.40`
**Current phase handoff:** `Phase 134 已完成 3/3 plans 与 focused verification/validation；默认下一步是 milestone closeout。`

### Governance Ownership
- [x] **GOV-90**: `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 与 `GOVERNANCE_REGISTRY.json` 必须共同承认 `v1.40 active milestone route / starting from latest archived baseline = v1.39`，并把 `Phase 134` 作为唯一 active phase、`$gsd-complete-milestone v1.40` 作为默认下一步。

### RequestPolicy / Entity Architecture
- [x] **ARC-43**: `custom_components/lipro/core/api/request_policy.py` 必须把 pacing caches / busy counters / target locks 收回单一实例 owner；`request_policy_support.py` 只保留 support helpers，不再让 mutable pacing state 以 parallel dict 参数形式四处流动。
- [x] **HOT-62**: `custom_components/lipro/entities/descriptors.py`、`custom_components/lipro/light.py` 与 `custom_components/lipro/binary_sensor.py` 必须移除 dotted-path/getattr 反射，改为显式 resolver / state-reader projection。
- [x] **HOT-63**: `custom_components/lipro/fan.py` 的 unknown `fanMode` 不能再 fallback 成 `cycle`；preset / supported_features / behavior tests 必须维持 truthful 一致投影。

### Quality / Verification
- [x] **QLT-56**: developer architecture、maintainer runbook、public-surface meta guards 与 phase assets 必须同步描述新的 owner/projection truth，避免 route/docs/guards 各讲一套。
- [x] **TST-54**: focused `pytest`/meta/ruff lane 必须覆盖 RequestPolicy ownership、entity de-reflection、fan truth 与 `v1.40` 当前治理路由。

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| GOV-90 | Phase 134 | Complete |
| ARC-43 | Phase 134 | Complete |
| HOT-62 | Phase 134 | Complete |
| HOT-63 | Phase 134 | Complete |
| QLT-56 | Phase 134 | Complete |
| TST-54 | Phase 134 | Complete |

## Coverage

- v1.40 requirements: 6 total
- Current mapped: 6
- Current complete: 6
- Current pending: 0


## Historical Traceability Appendix

为保持 archived continuity guards 与历史 requirement mapping 的单一叙事，保留以下已归档 traceability 锚点：

| Requirement | Phase | Status |
|-------------|-------|--------|
| HOT-14 | Phase 60 | Complete |
| TST-12 | Phase 60 | Complete |
| GOV-44 | Phase 60 | Complete |

## Latest Archived Milestone (v1.39)

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
