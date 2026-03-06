# Developer Architecture / 开发者架构概览

This document describes the internal package layout of the Lipro Home Assistant
integration. It is intended for contributors and people maintaining forks.

本文档描述 Lipro Home Assistant 集成的内部代码结构，面向贡献者与维护分支的开发者。

## Goals / 目标

- Keep end-user behavior stable (entities, services, config flow).
- Reduce cognitive load: `custom_components/lipro/core/` is no longer a flat list of dozens of modules.
- Make boundaries explicit so future changes stay maintainable.

## Top-level layout / 顶层结构

`custom_components/lipro/`:

- `__init__.py`: Integration setup, platform forwarding, and thin orchestration.
- `entry_auth.py`: Config-entry authentication setup, token persistence, and runtime-data cleanup helpers.
- `entry_options.py`: Config-entry option snapshot helpers and reload-loop protection.
- `runtime_infra.py`: Shared runtime infrastructure setup for services and the device-registry listener.
- `config_flow.py`: UI config flow.
- `core/`: Internal clients + domain helpers (see below).
- `entities/`: Entity base classes / shared entity behavior.
- `helpers/`: Home Assistant-facing platform setup helpers (entity builders/factories).
- `services/`: Home Assistant service handlers.
- `services/wiring.py`: Home Assistant-specific dependency wiring for service handlers.
- `services/registrations.py`: Static service registration table mapping names/schemas to handlers.
- `services/registry.py`: Declarative Home Assistant service registration helpers.
- `services/contracts.py`: Service constants + voluptuous schemas (contract-only module).
- `const/`: Constants (API paths, config keys, device mappings).

## `core/` layout / `core/` 子包结构

`custom_components/lipro/core/`:

- `api/`: REST API client + endpoint helpers/codecs (status/schedule/diagnostics/...).
- `api/response_safety.py`: Response code normalization + sensitive log masking rules.
- `api/request_policy.py`: Retry-After parsing, rate-limit wait policy, CHANGE_STATE pacing helpers.
- `mqtt/`: Aliyun MQTT client, topic/payload parsing, setup + backoff helpers.
- `device/`: `LiproDevice` model + identity index / group status helpers.
- `auth/`: Token refresh and authentication manager.
- `ota/`: OTA candidate selection + payload/manifest normalization + certified firmware lookup helpers.
- `anonymous_share/`: Optional redacted telemetry/reporting (opt-in).
- `command/`: Command routing/trace/result helpers used by the coordinator.
- `utils/`: Shared, non-HA utilities (redaction/log safety/background tasks/debounce/developer report).
- `coordinator/`: The orchestration hub (`DataUpdateCoordinator`) that binds HA runtime to core logic (see `coordinator/coordinator.py`).
  - `coordinator/runtime/`: Adaptive decision helpers used by the coordinator.
  - `coordinator/mqtt/`: Coordinator-side MQTT lifecycle + reconcile/poll policy.

## Dependency direction / 依赖方向

- HA-facing layers (`services/`, platform modules like `light.py`, etc.) depend on `core/`.
- Subpackages under `core/` should avoid importing Home Assistant modules.
- `core/coordinator/coordinator.py` is the exception: it integrates HA runtime APIs with the core packages.

## Public API surface / 公共入口

Prefer importing from:

- `custom_components.lipro.core` (facade exports used by the integration entrypoints)
- `custom_components.lipro.core.api` / `custom_components.lipro.core.mqtt` / `custom_components.lipro.core.device`

Internal helpers live in subpackages (`core/api/*`, `core/command/*`, `core/coordinator/runtime/*`, ...).

## Key modules / 关键模块速查

Frequently-touched modules (as of the current tree):

- API client entrypoint: `custom_components.lipro.core.api.client`
- API request pacing & retry helpers: `custom_components.lipro.core.api.request_policy`
- API response safety (masking + code normalization): `custom_components.lipro.core.api.response_safety`
- Coordinator (HA `DataUpdateCoordinator` binding): `custom_components.lipro.core.coordinator.coordinator`
- Coordinator runtime policy helpers: `custom_components.lipro.core.coordinator.runtime.*`
- MQTT client: `custom_components.lipro.core.mqtt.client`
- Command helpers: `custom_components.lipro.core.command.dispatch` / `trace` / `result`
- Device model: `custom_components.lipro.core.device.device`

## Testing after refactor / 重构后测试

Recommended checks (same or stricter than CI):

- `./scripts/lint`
- `uv run pytest tests/ -v --cov=custom_components/lipro --cov-fail-under=95 --cov-report=xml --cov-report=term-missing`
