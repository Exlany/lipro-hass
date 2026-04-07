# Phase 138 Context

## Goal

在 `Phase 137` 已完成 sanctioned hotspot burn-down 的前提下，继续收口 closeout review 暴露的 remaining structural debt：

- `runtime_types.py` 对 `services/contracts.py` 的反向依赖
- connect-status richer outcome 在 outward chain 被重新压平成 `{}`
- `service_router_support.py` 名称与 formal bridge 身份之间的 discoverability 张力
- live docs 与 pull-only archive appendix 的叙事分工
- current-route selector family 对 `Phase 138` 的一致承认

## Inputs

- `.planning/reviews/V1_41_REMEDIATION_CHARTER.md`
- `.planning/phases/137-hotspot-burn-down-command-observability-and-governance-compression/137-SUMMARY.md`
- `.planning/phases/137-hotspot-burn-down-command-observability-and-governance-compression/137-VERIFICATION.md`
- `custom_components/lipro/runtime_types.py`
- `custom_components/lipro/services/contracts.py`
- `custom_components/lipro/control/service_router_support.py`
- `docs/README.md`
- `docs/developer_architecture.md`

## Exit Truth

- runtime/service shared typed contract 有独立 formal home
- connect-status outcome 在 `status_service -> endpoint_surface -> rest_port -> protocol facade` 调用链中保持显式 typed result
- service-router bridge 的 inward / non-public-root 语义 machine-checkable
- route selector family 与 docs/baselines 同步到 `Phase 138 complete`
