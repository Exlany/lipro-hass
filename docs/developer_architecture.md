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

- `__init__.py`: Integration setup, service wiring, platform forwarding.
- `config_flow.py`: UI config flow.
- `core/`: Internal clients + domain helpers (see below).
- `entities/`: Entity base classes / shared entity behavior.
- `helpers/`: Small shared helpers (coerce/debounce/platform helpers).
- `services/`: Home Assistant service handlers.
- `services/registry.py`: Declarative Home Assistant service registration helpers.
- `services/contracts.py`: Service constants + voluptuous schemas (contract-only module).
- `const/`: Constants (API paths, config keys, device mappings).

## `core/` layout / `core/` 子包结构

`custom_components/lipro/core/`:

- `api/`: REST API client + endpoint helpers/codecs (status/schedule/diagnostics/...).
- `api/api_response_safety.py`: Response code normalization + sensitive log masking rules.
- `api/request_policy.py`: Retry-After parsing, rate-limit wait policy, CHANGE_STATE pacing helpers.
- `mqtt/`: Aliyun MQTT client, topic/payload parsing, setup/backoff/runtime.
- `device/`: `LiproDevice` model + refresh/index/group/outlet/registry-sync helpers.
- `auth/`: Token refresh and authentication manager.
- `anonymous_share/`: Optional redacted telemetry/reporting (opt-in).
- `command/`: Command routing/trace/result helpers used by the coordinator.
- `runtime/`: Adaptive decision helpers used by the coordinator.
- `utils/`: Redaction/log safety/background tasks/developer report.
- `ota_utils/`: OTA parsing helpers (kept as a package to preserve import path).
- `coordinator/`: The orchestration hub (`DataUpdateCoordinator`) that binds HA runtime to core logic (see `coordinator/coordinator.py`).

## Dependency direction / 依赖方向

- HA-facing layers (`services/`, platform modules like `light.py`, etc.) depend on `core/`.
- Subpackages under `core/` should avoid importing Home Assistant modules.
- `core/coordinator/coordinator.py` is the exception: it integrates HA runtime APIs with the core packages.

## Public API surface / 公共入口

Prefer importing from:

- `custom_components.lipro.core` (facade exports used by the integration entrypoints)
- `custom_components.lipro.core.api` / `custom_components.lipro.core.mqtt` / `custom_components.lipro.core.device`

Internal helpers live in subpackages (`core/api/*`, `core/command/*`, `core/coordinator/runtime/*`, ...).

## Import migration map / 导入迁移对照

This refactor moved leaf modules into subpackages. Common mappings:

| Old import path | New import path |
| --- | --- |
| `custom_components.lipro.core.api_status_service` | `custom_components.lipro.core.api.api_status_service` |
| `custom_components.lipro.core.api_command_service` | `custom_components.lipro.core.api.api_command_service` |
| `custom_components.lipro.core.api_schedule_service` | `custom_components.lipro.core.api.api_schedule_service` |
| `custom_components.lipro.core.request_codec` | `custom_components.lipro.core.api.request_codec` |
| `custom_components.lipro.core.schedule_codec` | `custom_components.lipro.core.api.schedule_codec` |
| `custom_components.lipro.core.schedule_endpoint` | `custom_components.lipro.core.api.schedule_endpoint` |
| `custom_components.lipro.core.mqtt_setup` | `custom_components.lipro.core.mqtt.mqtt_setup` |
| `custom_components.lipro.core.mqtt_message` | `custom_components.lipro.core.mqtt.mqtt_message` |
| `custom_components.lipro.core.mqtt_lifecycle` | `custom_components.lipro.core.mqtt.mqtt_lifecycle` |
| `custom_components.lipro.core.command_dispatch` | `custom_components.lipro.core.command.command_dispatch` |
| `custom_components.lipro.core.command_result` | `custom_components.lipro.core.command.command_result` |
| `custom_components.lipro.core.command_trace` | `custom_components.lipro.core.command.command_trace` |
| `custom_components.lipro.core.device_refresh` | `custom_components.lipro.core.device.device_refresh` |
| `custom_components.lipro.core.device_identity_index` | `custom_components.lipro.core.device.device_identity_index` |
| `custom_components.lipro.core.group_status` | `custom_components.lipro.core.device.group_status` |
| `custom_components.lipro.core.outlet_power` | `custom_components.lipro.core.device.outlet_power` |
| `custom_components.lipro.core.room_sync_runtime` | `custom_components.lipro.core.coordinator.runtime.room_sync_runtime` |
| `custom_components.lipro.core.coordinator_runtime` | `custom_components.lipro.core.coordinator.runtime.coordinator_runtime` |
| `custom_components.lipro.core.developer_report` | `custom_components.lipro.core.utils.developer_report` |
| `custom_components.lipro.core.background_task_manager` | `custom_components.lipro.core.utils.background_task_manager` |

## Testing after refactor / 重构后测试

Recommended checks (same as CI):

- `uv run ruff check .`
- `uv run pytest -q`
