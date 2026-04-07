---
phase: 11-control-router-formalization-wiring-residual-demotion
plan: "01"
status: completed
completed: 2026-03-14
requirements:
  - CTRL-01
  - CTRL-02
---

# Summary 11-01

## Outcome

- `custom_components/lipro/control/service_router.py` 已承载真实 HA service callback 实现，并直接组合 `services/*` 叶子协作者。
- `custom_components/lipro/services/registrations.py` 继续绑定 formal router handlers，服务 schema、supports_response 与响应结构保持稳定。
- control-plane formal home 与 implementation home 已经合一，不再由 legacy wiring 反向定义实现归属。

## Verification

- 见 `11-VERIFICATION.md` 的 Phase 11 closeout suite。
- 关键切片：`tests/core/test_init.py`、`tests/services/test_services_registry.py`、`tests/meta/test_public_surface_guards.py`。

## Governance Notes

- `control/service_router.py` 现为正式 service callback home；后续不得再把主实现放回 `services/wiring.py`。
