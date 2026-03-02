# Optimization TODO (Completed)

- [x] Tighten service input validation for diagnostics endpoints (`msg_sn`, `sensor_device_id`, `mesh_type`).
- [x] Harden entity target resolution to reject ambiguous multi-entity service calls.
- [x] Improve `get_city` service resiliency by falling back to subsequent coordinators.
- [x] Add regression tests for the above changes.
