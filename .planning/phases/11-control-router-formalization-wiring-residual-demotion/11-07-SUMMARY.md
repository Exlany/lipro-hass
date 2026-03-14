---
phase: 11-control-router-formalization-wiring-residual-demotion
plan: "07"
status: completed
completed: 2026-03-14
requirements:
  - ENT-02
---

# Summary 11-07

## Outcome

- `custom_components/lipro/entities/firmware_update.py` 已收窄为 HA update projection / user interaction / minimal orchestration。
- `custom_components/lipro/core/ota/candidate.py` 已承载 candidate projection、install evaluation 与 confirmation-window policy；`rows_cache.py` / `row_selector.py` 固定 shared cache 与 row arbitration truth。
- entity 主链已移除 remote advisory 参与 certification 的路径，OTA 真相不再由平台层私有 helper 定义。

## Verification

- 见 `11-VERIFICATION.md` 的 Phase 11 closeout suite。
- 关键切片：`tests/platforms/test_update.py`、`tests/platforms/test_firmware_update_entity_edges.py`、`tests/core/ota/test_firmware_manifest.py`、`tests/core/test_diagnostics.py`。

## Governance Notes

- `firmware_update.py` 不再是 OTA policy mega-file；后续 OTA 演进必须继续围绕 `core/ota/*` formal helper cluster 收口。
