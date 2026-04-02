# Phase 139 Context

## Goal

在不改变 `LiproRestFacade` 与 `rest_port.py` formal-home 身份的前提下，继续做一次 inward-only second-pass slimming：

- `rest_port.py` 下沉 bound adapter family 到 sibling bindings module
- `rest_facade.py` 下沉 transport/auth/mapping private mechanics 到 sibling internal module
- 修复 schedule `group_id` 在 protocol/rest/surface 链上的 forwarding 漂移
- 把 current-route selector、verification baseline、developer/runbook docs 与 phase assets 一并切到 `v1.43 active route`

## Inputs

- `.planning/reviews/V1_41_REMEDIATION_CHARTER.md`
- `.planning/phases/138-runtime-contract-decoupling-support-guard-and-docs-alignment/138-SUMMARY.md`
- `custom_components/lipro/core/api/rest_facade.py`
- `custom_components/lipro/core/api/rest_facade_endpoint_methods.py`
- `custom_components/lipro/core/api/endpoint_surface.py`
- `custom_components/lipro/core/protocol/rest_port.py`
- `custom_components/lipro/core/protocol/protocol_facade_rest_methods.py`

## Exit Truth

- `rest_facade.py` 与 `rest_port.py` line budgets 明显收窄，但 canonical formal-home 身份不变
- `rest_facade_internal_methods.py` 与 `rest_port_bindings.py` 仅承担 inward split mechanics，不长出第二 root
- schedule `group_id` forwarding truth machine-checkable
- `.planning` / docs / tests / file-matrix / verification baseline 共同承认 `Phase 139 complete / Phase 140 planning-ready`
