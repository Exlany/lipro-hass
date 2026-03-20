# 43-02 Summary

- Completed on `2026-03-20`.
- Moved device-registry listener ownership, Lipro device-entry resolution, and pending reload-task management out of `custom_components/lipro/services/maintenance.py` into `custom_components/lipro/runtime_infra.py`, so maintenance stays a thin Home Assistant service adapter.
- Preserved the formal lifecycle wiring by keeping `setup_device_registry_listener()` in `runtime_infra` as the control/runtime collaboration home, while updating focused control-plane and maintenance tests to patch the new boundary and verify listener behavior.
- Verified with `uv run pytest tests/services/test_maintenance.py tests/core/test_control_plane.py tests/core/test_init.py tests/core/test_init_service_handlers.py -q` (`60 passed`).
- Note: `tests/core/test_init_entry_forwarding.py` is referenced by the plan but is absent in the current tree, so the focused verification set used the existing init/control coverage instead.
