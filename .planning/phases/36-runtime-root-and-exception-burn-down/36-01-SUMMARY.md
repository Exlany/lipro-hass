# 36-01 Summary

## Outcome

- `CoordinatorPollingService` 已正式承接 snapshot refresh / status polling / outlet power polling orchestration。
- `Coordinator` 保留 public entrypoints 与 root-owned wiring，但 polling cluster 已成为 thin wrapper。

## Validation

- `uv run pytest -q tests/core/test_coordinator.py tests/integration/test_mqtt_coordinator_integration.py tests/meta/test_public_surface_guards.py`
