"""Coordinator service layer - API stability facade (Stable Interface Pattern).

This layer provides stable API boundaries between Entity and Runtime layers,
implementing the Dependency Inversion Principle from Clean Architecture.

Value: Isolates Entity layer from Runtime implementation changes.
Pattern: Thin proxy / Stable Facade (intentional design, not technical debt).

Services:
- CoordinatorCommandService: Command dispatch facade
- CoordinatorDeviceRefreshService: Device refresh facade
- CoordinatorMqttService: MQTT connection facade
- CoordinatorStateService: State access facade
"""

from .command_service import CoordinatorCommandService
from .device_refresh_service import CoordinatorDeviceRefreshService
from .mqtt_service import CoordinatorMqttService
from .state_service import CoordinatorStateService

__all__ = [
    "CoordinatorCommandService",
    "CoordinatorDeviceRefreshService",
    "CoordinatorMqttService",
    "CoordinatorStateService",
]
