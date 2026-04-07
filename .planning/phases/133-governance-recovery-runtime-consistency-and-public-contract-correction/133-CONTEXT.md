# Phase 133: Governance recovery, runtime consistency, and public contract correction - Context

**Gathered:** 2026-04-02
**Status:** Reconstructed for governance continuity / closeout-ready
**Milestone:** `v1.39 Governance Recovery, Runtime Consistency & Public Contract Correction`
**Current route:** `v1.39 active milestone route / starting from latest archived baseline = v1.38`
**Requirements basket:** `GOV-89`, `ARC-42`, `HOT-61`, `DOC-18`, `QLT-55`, `TST-53`
**Default next command:** `$gsd-complete-milestone v1.39`

<domain>
## Phase Boundary

本 phase 只做四件已经被 north-star 与 active governance truth 同时允许的事：

1. 恢复 `v1.39` active milestone route 的单一真源，使 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`、registry、review ledgers 与 phase assets 对齐；
2. 在既有正式 home 内修补 runtime consistency 漂移，不让 coordinator/runtime/control 的 sanctioned hotspot 继续以 vague debt 形式漂浮；
3. 校正 developer/public contract wording、preset semantics、quality-scale 与 service-facing docs，使对外叙事重新回到真实实现；
4. 完成 governance closeout resync，让 `FILE_MATRIX`、testing map、promoted assets、historical archived chronology 与 active handoff 故事保持同一条主线。

本 phase 不是新一轮 repo-wide hotspot burn-down，也不是授权建立第二条 execution story；它的职责是把当前真相压回单一正式主链。
</domain>

<decisions>
## Locked Decisions

### Governance route recovery
- `v1.39` 必须是唯一 current active milestone，且 `Phase 133` 是唯一 active phase。
- current route truth 固定为 `v1.39 active milestone route / starting from latest archived baseline = v1.38`。
- `$gsd-next` 的等价结论必须收敛到 `$gsd-complete-milestone v1.39`，不得保留 archived-only 或 execute-again 的旧故事。

### Runtime consistency repair
- 修复只能落在既有正式 home：`firmware_manifest.py`、`control/runtime_access.py`、`control/developer_router_support.py`、platform adapters 等。
- 不得为修补 runtime inconsistency 新增 compat root、反射式 backdoor、或第二条 runtime access story。
- diagnostics / developer report / runtime single-read contract 必须以 inward convergence 收口，而不是扩大 helper folklore。

### Public contract correction
- climate/fan preset、service wording、quality scale、README / troubleshooting 文字必须服从当前真实实现，而不是延续过时文案。
- public/docs contract correction 必须同步 tests，避免出现“实现一套、文档一套、守卫再讲第三套”的 drift。

### Governance closeout
- phase outputs 采用四计划单 phase 结构：governance bootstrap、runtime consistency、public contract correction、governance closeout/resync。
- historical archived chronology、promoted phase assets、testing-map counts 与 requirement traceability 必须共同承认 `Phase 133 complete; closeout-ready`。
- phase assets 默认仍是执行资产；只有被 governance 主链显式引用的内容才算长期证据。

### Claude's Discretion
- 具体文案以“更诚实、更接近 formal home、更少 folklore”为裁决标准。
- verification 以 focused runtime/public-contract lane + governance/meta lane 为最小充分验证集。
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / governance truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 终态裁决与禁止项
- `AGENTS.md` — authority order、formal homes、phase asset identity
- `.planning/PROJECT.md` — `v1.39` current milestone truth
- `.planning/ROADMAP.md` — `Phase 133` 正式路线与 closeout-ready handoff
- `.planning/REQUIREMENTS.md` — `GOV-89 / ARC-42 / HOT-61 / DOC-18 / QLT-55 / TST-53` 真源
- `.planning/STATE.md` — active route、progress 与 next-step truth
- `.planning/MILESTONES.md` — current milestone 与 archived chronology 投影
- `.planning/baseline/GOVERNANCE_REGISTRY.json` — governance registry truth
- `.planning/reviews/FILE_MATRIX.md` — file inventory / promoted phase coverage
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` — promoted phase asset allowlist

### Production files in scope
- `custom_components/lipro/firmware_manifest.py` — firmware advisory malformed fallback 与 local trust-root 收口
- `custom_components/lipro/control/runtime_access.py` — runtime single-read / typed access truth
- `custom_components/lipro/control/developer_router_support.py` — developer report single-resolve / wording contract
- `custom_components/lipro/climate.py` — preset behavior / public platform contract
- `custom_components/lipro/fan.py` — capability wording / public platform contract
- `custom_components/lipro/services.yaml` — service wording truth
- `custom_components/lipro/quality_scale.yaml` — quality-scale capability truth
- `README.md`
- `README_zh.md`
- `docs/TROUBLESHOOTING.md`

### Verification surfaces
- `tests/core/ota/test_firmware_manifest.py`
- `tests/core/test_runtime_access.py`
- `tests/core/test_control_plane.py`
- `tests/platforms/test_climate.py`
- `tests/platforms/test_fan_entity_behavior.py`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_governance_route_handoff_smoke.py`
- `tests/meta/governance_followup_route_current_milestones.py`
</canonical_refs>

<specifics>
## Specific Ideas

- Phase 133 的正式执行拆分固定为 `133-01` governance bootstrap、`133-02` runtime consistency、`133-03` public contract correction、`133-04` governance closeout / resync。
- focused proof 分成两组：
  - runtime/public-contract lane
  - governance/meta lane
- 为 continuity guards 保留历史 appendix 是允许的，但必须明确标记为 archived traceability，而不是把旧 milestone 重新激活。
</specifics>

<deferred>
## Deferred Ideas

- 不在本 phase 中承诺消灭所有更深层 sanctioned hotspot；本 phase 只关闭已经被 `v1.39` 正式收编的问题。
- 不在本 phase 中重开新的 repo-wide master audit 或新 milestone 规划。
- 不把 `.planning/phases/**` 的全部执行痕迹升级为长期治理真源。
</deferred>

---
*Phase: 133-governance-recovery-runtime-consistency-and-public-contract-correction*
*Context reconstructed: 2026-04-02 for governance continuity*
