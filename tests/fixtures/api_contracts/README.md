# API Contract Matrix

## Purpose

This directory stores golden fixtures for high-drift protocol-boundary contracts.

These fixtures do **not** describe the whole vendor API. They intentionally lock
only high-value, high-drift boundary contracts that must fail in the protocol
plane before drift can leak into runtime / control / HA adapter code.

## Current Matrix

| Endpoint | Transport Path | Fixture | Owning Test |
|---|---|---|---|
| `get_mqtt_config` | `PATH_GET_MQTT_CONFIG` | `get_mqtt_config.direct.json`, `get_mqtt_config.wrapped.json` | `tests/core/api/test_protocol_contract_matrix.py` |
| `get_device_list` | `LiproProtocolFacade.get_device_list` compat seam | `get_device_list.direct.json`, `get_device_list.compat.json` | `tests/core/api/test_protocol_contract_matrix.py` |
| `query_device_status` | `PATH_QUERY_DEVICE_STATUS` | `query_device_status.mixed.json` | `tests/core/api/test_protocol_contract_matrix.py` |
| `query_mesh_group_status` | `PATH_QUERY_MESH_GROUP_STATUS` | `query_mesh_group_status.topology.json` | `tests/core/api/test_protocol_contract_matrix.py` |
| `get_city` | `PATH_GET_CITY` | `get_city.success.json` | `tests/core/api/test_protocol_contract_matrix.py` |
| `query_user_cloud` | `PATH_QUERY_USER_CLOUD` | `query_user_cloud.success.json` | `tests/core/api/test_protocol_contract_matrix.py` |

## Canonicalization Rule

- `get_mqtt_config` direct and wrapped fixtures describe the same canonical payload; the wrapped sample only adds a transport envelope.
- `get_device_list` direct and compat fixtures describe the same canonical catalog page; pagination truth is normalized as `has_more` before runtime consumption.
- `query_device_status` canonical output is a list of normalized `{deviceId, properties}` rows; alias IDs and flat property payloads are absorbed at the boundary.
- `query_mesh_group_status` canonical output is a list of normalized topology rows with canonical `groupId`, `gatewayDeviceId`, and member device IDs.
- `get_city` and `query_user_cloud` remain thin validated mapping contracts and are intentionally not duplicated elsewhere.

## Why These Fixtures Exist

1. They cover the API shapes most likely to drift independently of runtime logic.
2. They make API drift hit protocol tests first instead of forcing Home Assistant refactors.
3. They document the future-host rule: CLI / other platforms may only reuse formal boundary contracts, not raw vendor payloads.
