---
phase: 35
slug: protocol-hotspot-final-slimming
status: passed
updated: 2026-03-18
---

# Phase 35 Summary

## Outcome

- `35-01`: `LiproRestFacade` 现通过 `ClientRequestGateway` 与 `ClientEndpointSurface` inward 收口 request / endpoint ballast。
- `35-02`: `LiproProtocolFacade` 现通过 `rest_port.py` 与 `mqtt_facade.py` 组合 child façades，protocol root body 继续变薄。
- `35-03`: protocol/API regression、public-surface guards 与 planning/governance truth 已同步收口到 slimmer protocol layout。

## Validation

- `uv run pytest -q tests/core/api/test_api_command_surface.py tests/core/api/test_api_transport_and_schedule.py tests/core/api/test_auth_recovery_telemetry.py tests/core/api/test_protocol_contract_matrix.py tests/meta/test_public_surface_guards.py`
- `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_governance*.py tests/meta/test_version_sync.py tests/meta/test_public_surface_guards.py`
- `uv run ruff check .`
