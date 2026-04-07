# Phase 61: Formal-home slimming for large-but-correct production modules - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning
**Source:** `Phase 58` remediation route + `Phase 60` closeout + current hotspot census

<domain>
## Phase Boundary

本 phase 是一次 **production formal-home inward slimming**，不是命名清扫或 public discoverability 整理。

1. 只处理已经 architecturally-correct、但仍偏厚的正式 home：`anonymous_share`、diagnostics service family、OTA candidate 与 `select`；
2. 所有改动都必须沿既有正式边界 inward split，不新增 public root、compat shell、second helper story 或 second formal home；
3. 任何结构切分都必须同步交付 focused family regressions / maintainability evidence，证明收益是 failure-localization 与 typed seam clarity，而不是纯文件搬运；
4. `*_support.py` / `*_surface.py` 的命名诚实化与 public docs/discoverability 清理留给 `Phase 62`，本 phase 只在必要范围内为后续命名收口创造更清晰的内部边界。

</domain>

<decisions>
## Locked Decisions

- 当前最高优先级 hotspot：
  - `custom_components/lipro/core/anonymous_share/manager.py`
  - `custom_components/lipro/core/anonymous_share/share_client.py`
  - `custom_components/lipro/services/diagnostics/helpers.py`
  - `custom_components/lipro/services/diagnostics/handlers.py`
  - `custom_components/lipro/core/ota/candidate.py`
  - `custom_components/lipro/select.py`
- outward home 必须继续稳定：
  - `AnonymousShareManager` 仍以 `custom_components/lipro/core/anonymous_share/manager.py` 为正式 home；
  - `ShareWorkerClient` 仍以 `custom_components/lipro/core/anonymous_share/share_client.py` 为正式 home；
  - diagnostics 的稳定 public import surface 继续是 `custom_components/lipro/services/diagnostics/__init__.py`；
  - OTA candidate 真源继续是 `custom_components/lipro/core/ota/candidate.py`；
  - Home Assistant select platform root 继续是 `custom_components/lipro/select.py`。
- split 只允许 inward：新文件必须是同 family 内的 collaborator / projection / normalization helper，不得让控制面、平台面或测试重新依赖新的私有 root。
- 新 seam 必须保持 typed contract、诚实 ownership 与 boundary clarity；禁止回流原始动态 dict truth、宽布尔失败、helper-owned second story。

### Claude's Discretion
- 可把 submission / token refresh / diagnostics polling / OTA arbitration / select gear projection 拆成更窄的内部协作者，只要 outward homes 与 public imports 稳定。
- 可同步补 focused tests、薄化 mega test 文件，前提是 runnable topology 更清晰且 guard intent 不丢失。
- 若某个 hotspot 已有 `*_support.py`，本 phase 可以继续 inward split，但不在此阶段做全仓命名重定向。

</decisions>

<canonical_refs>
## Canonical References

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-REMEDIATION-ROADMAP.md`
- `.planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/60-SUMMARY.md`
- `.planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/60-VERIFICATION.md`
- `custom_components/lipro/core/anonymous_share/manager.py`
- `custom_components/lipro/core/anonymous_share/share_client.py`
- `custom_components/lipro/core/anonymous_share/manager_support.py`
- `custom_components/lipro/core/anonymous_share/share_client_support.py`
- `custom_components/lipro/services/diagnostics/__init__.py`
- `custom_components/lipro/services/diagnostics/helpers.py`
- `custom_components/lipro/services/diagnostics/handlers.py`
- `custom_components/lipro/services/diagnostics/helper_support.py`
- `custom_components/lipro/core/ota/candidate.py`
- `custom_components/lipro/core/ota/manifest.py`
- `custom_components/lipro/entities/firmware_update.py`
- `custom_components/lipro/select.py`
- `tests/core/anonymous_share/test_manager_recording.py`
- `tests/core/anonymous_share/test_manager_submission.py`
- `tests/services/test_services_diagnostics.py`
- `tests/core/ota/test_ota_candidate.py`
- `tests/platforms/test_select_behavior.py`
- `tests/platforms/test_select_models.py`

## Hotspot Observations

- `manager.py` 仍同时承担 scope facade、state delegation、recording entrypoint、aggregate orchestration 与 submit lifecycle；虽然 formal home 正确，但责任密度仍偏高。
- `share_client.py` 同时承载 token refresh、HTTP response parsing、rate-limit/backoff、payload fallback 与 legacy bool compatibility；typed contract 已存在，但 submit flow 仍偏厚。
- diagnostics family 已建立 `__init__.py` stable public surface 与 `helper_support.py`，但 `helpers.py` / `handlers.py` 仍混合 parameter coercion、developer-feedback projection、capability fan-out、bounded polling 与 sensor-history handlers。
- `candidate.py` 把 install confirmation、update-availability、inline-certification、manifest-certification 与 projection 全放在一处，已正确但不够 focused。
- `select.py` 同时承载 platform setup、mapped property selects、gear projection / validation / command application，仍可继续 inward split。

</canonical_refs>

<execution_shape>
## Recommended Execution Shape

- `61-01`：优先切薄 `anonymous_share` manager/share client family，提炼 submit/token/reporting collaborator；
- `61-02`：切薄 diagnostics service family，形成更诚实的 developer-feedback / optional-capability / polling seams；
- `61-03`：切薄 OTA candidate arbitration / certification / install-policy helpers，同时保持 `candidate.py` outward home；
- `61-04`：切薄 `select` platform 内部模型与 gear projection，并同步 focused tests / maintainability evidence / phase guard。

</execution_shape>
