---
phase: 11-control-router-formalization-wiring-residual-demotion
plan: "06"
status: completed
completed: 2026-03-14
requirements:
  - ENT-01
---

# Summary 11-06

## Outcome

- `custom_components/lipro/helpers/platform.py` 已成为 supplemental switch/select/update 暴露规则的共享真源。
- `custom_components/lipro/switch.py` 已移除基于 `hasattr()` 的弱判定；`custom_components/lipro/select.py` 对 unknown enum 改为显式可观测处理，并把 gear 写侧切回 formal refresh seam。
- `custom_components/lipro/update.py` 已复用统一 firmware-update eligibility，平台层重复事实被清理。

## Verification

- 见 `11-VERIFICATION.md` 的 Phase 11 closeout suite。
- 关键切片：`tests/platforms/test_switch.py`、`tests/platforms/test_select.py`、`tests/platforms/test_platform_entities_behavior.py`、`tests/platforms/test_update.py`。

## Governance Notes

- 平台建模规则已收口到单一 helper truth；unknown-enum 与 supplemental entity 不再各平台各自裁决。
