# API Contract Matrix

## Purpose

This directory stores the first golden fixtures for the north-star protocol plane.

These fixtures do **not** describe the whole vendor API. They intentionally lock only
high-value, high-drift boundary contracts that will be used as regression anchors for
future `API Client` de-mixin refactors.

## Initial Matrix

| Endpoint | Transport Path | Fixture | Owning Test |
|---|---|---|---|
| `get_mqtt_config` | `PATH_GET_MQTT_CONFIG` | `get_mqtt_config.direct.json`, `get_mqtt_config.wrapped.json` | `tests/core/api/test_protocol_contract_matrix.py` |
| `get_city` | `PATH_GET_CITY` | `get_city.success.json` | `tests/core/api/test_protocol_contract_matrix.py` |
| `query_user_cloud` | `PATH_QUERY_USER_CLOUD` | `query_user_cloud.success.json` | `tests/core/api/test_protocol_contract_matrix.py` |

## Canonicalization Rule

- `get_mqtt_config` direct and wrapped fixtures describe the same canonical payload; the wrapped sample only adds a transport envelope
- `get_mqtt_config` canonical output is a mapping containing at least `accessKey` and `secretKey`
- `get_city` canonical output is the validated mapping returned by the endpoint helper
- `query_user_cloud` canonical output is the validated mapping returned by the endpoint helper

## Why These Three First

1. They sit on protocol boundaries likely to drift independently of runtime logic
2. They are useful before large `API Client` façade refactors
3. They give a minimal but real golden-fixture starting point instead of only example snapshots
