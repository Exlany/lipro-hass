# 43-03 Summary

- Completed on `2026-03-20`.
- Demoted `custom_components/lipro/services/device_lookup.py` to a service-facing device-id resolver only, removing runtime device/coordinator ownership from the `services/` layer.
- Moved the formal device/coordinator bridge into `custom_components/lipro/control/service_router_support.py`, where control now combines service-call target resolution with `RuntimeAccess` lookup and owns the translated `device_not_found` failure path.
- Added focused guard coverage so `tests/core/test_control_plane.py` verifies the one-way service→control→runtime bridge, `tests/services/test_services_registry.py` locks the router-bound getter to the control plane, and `tests/services/test_device_lookup.py` now covers only service-facing target resolution.
- Verified with `uv run pytest tests/services/test_device_lookup.py tests/services/test_services_registry.py tests/core/test_control_plane.py tests/core/test_init_service_handlers_device_resolution.py -q` (`29 passed`).
