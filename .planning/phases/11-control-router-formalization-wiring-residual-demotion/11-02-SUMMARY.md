---
phase: 11-control-router-formalization-wiring-residual-demotion
plan: "02"
status: completed
completed: 2026-03-14
requirements:
  - CTRL-01
  - CTRL-02
---

# Summary 11-02

## Outcome

- `custom_components/lipro/services/wiring.py` 已降为显式 compat re-export shell，不再承载 primary orchestration。
- 仓库内 service/control tests 已迁移到 `custom_components.lipro.control.service_router` 正式 patch/import seam。
- legacy wiring 的 delete gate 已收紧为“remaining downstream imports 清零后可删”。

## Verification

- 见 `11-VERIFICATION.md` 的 Phase 11 closeout suite。
- 关键切片：`tests/core/test_init.py`、`tests/services/test_service_resilience.py`、`tests/services/test_services_registry.py`。

## Governance Notes

- 测试已不再驱动生产架构回流；`services/wiring.py` 只保留显式 compat 责任。
