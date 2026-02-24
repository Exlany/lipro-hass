# Test Suite Enhancement Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Comprehensively enhance the test suite to cover coordinator core logic, entity lifecycle, auth manager edge cases, and anonymous share — filling all gaps identified in the test review.

**Architecture:** Add a real `LiproDataUpdateCoordinator` fixture (mock hass + client + auth_manager), rewrite coordinator tests to call actual methods, add entity base class tests, enhance platform entity tests with real entity instantiation, and add missing module tests.

**Tech Stack:** pytest, pytest-asyncio, pytest-homeassistant-custom-component, unittest.mock

---

### Task 1: Add Coordinator Fixture to conftest.py

**Files:**
- Modify: `tests/conftest.py`

**What:** Add a `mock_hass`, `mock_auth_manager`, `mock_lipro_api_client`, and `real_coordinator` fixture that creates a real `LiproDataUpdateCoordinator` instance with mocked dependencies.

**Step 1: Add fixtures to conftest.py**

```python
# After existing fixtures, add:

@pytest.fixture
def mock_hass():
    """Create a minimal mock HomeAssistant instance."""
    hass = MagicMock()
    hass.config.config_dir = "/tmp/test_config"
    hass.data = {}
    hass.async_create_task = MagicMock(side_effect=lambda coro: asyncio.ensure_future(coro))
    return hass

@pytest.fixture
def mock_auth_manager():
    """Create a mock LiproAuthManager."""
    auth = AsyncMock()
    auth.ensure_valid_token = AsyncMock()
    auth.is_authenticated = True
    return auth

@pytest.fixture
def mock_lipro_api_client():
    """Create a mock LiproClient with common API responses."""
    client = AsyncMock()
    client.get_devices = AsyncMock(return_value={"devices": []})
    client.query_device_status = AsyncMock(return_value=[])
    client.query_mesh_group_status = AsyncMock(return_value=[])
    client.query_connect_status = AsyncMock(return_value={})
    client.get_mqtt_config = AsyncMock(return_value={})
    client.get_product_configs = AsyncMock(return_value=[])
    client.send_command = AsyncMock(return_value={"pushSuccess": True})
    client.send_group_command = AsyncMock(return_value={"pushSuccess": True})
    client.fetch_outlet_power_info = AsyncMock(return_value={})
    client.close = AsyncMock()
    client.access_token = "test_token"
    client.refresh_token = "test_refresh"
    client.user_id = 10001
    client.phone_id = "test_phone_id"
    return client
```

**Step 2: Run existing tests to verify no regressions**

Run: `pytest tests/ -v --tb=short -q`
Expected: All existing tests still pass

**Step 3: Commit**

```bash
git add tests/conftest.py
git commit -m "test: add coordinator-level mock fixtures to conftest.py"
```

---

### Task 2: Rewrite test_coordinator.py — Real Coordinator Unit Tests

**Files:**
- Rewrite: `tests/test_coordinator.py`

**What:** Replace the current tests (which only test Python dicts/sets) with tests that actually instantiate `LiproDataUpdateCoordinator` and call its methods. Focus on: device management, entity registration, debounce protection filtering, MQTT message handling, and command sending.

**Key test classes to write:**

1. `TestCoordinatorDeviceManagement` — `get_device()`, `get_device_by_id()`, `devices` property
2. `TestCoordinatorEntityRegistration` — `register_entity()`, `unregister_entity()`, duplicate guard
3. `TestCoordinatorDebounceFiltering` — `_filter_protected_properties()`, `_get_protected_keys_for_device()`
4. `TestCoordinatorMqttMessageHandling` — `_on_mqtt_message()` with dedup, unknown device, cache cleanup
5. `TestCoordinatorSendCommand` — `async_send_command()` for device vs group, auth error handling
6. `TestCoordinatorMqttPollingInterval` — `_on_mqtt_connect()`, `_on_mqtt_disconnect()` interval changes
7. `TestCoordinatorApplyPropertiesUpdate` — `_apply_properties_update()` with/without protection

**Step 1: Write the new test_coordinator.py**

The tests should use `mock_hass`, `mock_lipro_api_client`, `mock_auth_manager` fixtures and create a real coordinator:

```python
@pytest.fixture
def coordinator(mock_hass, mock_lipro_api_client, mock_auth_manager):
    """Create a real coordinator with mocked dependencies."""
    # ... create MockConfigEntry, instantiate LiproDataUpdateCoordinator
```

Each test should call actual coordinator methods and assert on real behavior.

**Step 2: Run tests**

Run: `pytest tests/test_coordinator.py -v --tb=short`
Expected: All new tests pass

**Step 3: Commit**

```bash
git add tests/test_coordinator.py
git commit -m "test: rewrite coordinator tests to call actual methods"
```

---

### Task 3: Rewrite test_coordinator_integration.py — Full Update Flow

**Files:**
- Rewrite: `tests/test_coordinator_integration.py`

**What:** Test the coordinator's `_async_update_data()` flow end-to-end with mocked API responses. Cover: device fetching with pagination, status updates, error handling (auth/connection/api errors), MQTT setup trigger, stale device removal, product config loading.

**Key test classes:**

1. `TestCoordinatorUpdateFlow` — `_async_update_data()` happy path, device fetch + status update
2. `TestCoordinatorFetchDevices` — pagination, gateway filtering, group/device ID collection
3. `TestCoordinatorErrorHandling` — `LiproAuthError` → `ConfigEntryAuthFailed`, `LiproConnectionError` → `UpdateFailed`
4. `TestCoordinatorProductConfigs` — `_load_product_configs()` color temp range application
5. `TestCoordinatorShutdown` — `async_shutdown()` resource cleanup
6. `TestCoordinatorRefreshDevices` — `async_refresh_devices()` force refresh flag

**Step 1: Write the new test_coordinator_integration.py**

```python
class TestCoordinatorUpdateFlow:
    @pytest.mark.asyncio
    async def test_first_update_fetches_devices(self, coordinator, mock_lipro_api_client):
        """Test first update fetches device list."""
        mock_lipro_api_client.get_devices.return_value = {
            "devices": [{"deviceNumber": 1, "serial": "03ab...", ...}]
        }
        # Call _async_update_data and verify devices populated
```

**Step 2: Run tests**

Run: `pytest tests/test_coordinator_integration.py -v --tb=short`

**Step 3: Commit**

```bash
git add tests/test_coordinator_integration.py
git commit -m "test: add coordinator integration tests for update flow"
```

---

### Task 4: Add LiproEntity Base Class Tests

**Files:**
- Create: `tests/test_entity_base.py`

**What:** Test `LiproEntity` lifecycle, debounce protection, command sending, and device info generation. This is currently untested.

**Key test classes:**

1. `TestLiproEntityInit` — unique_id generation (with/without suffix), device_info construction
2. `TestLiproEntityLifecycle` — `async_added_to_hass()` registers, `async_will_remove_from_hass()` unregisters + cancels debouncer
3. `TestLiproEntitySendCommand` — optimistic state, unavailable skip, failure triggers refresh
4. `TestLiproEntityDebounce` — `async_send_command_debounced()`, protection window, `get_protected_keys()`, `is_debouncing`
5. `TestLiproEntityAvailability` — coordinator success + device available

**Step 1: Write test_entity_base.py**

```python
class TestLiproEntityInit:
    def test_unique_id_without_suffix(self, mock_coordinator, make_device):
        device = make_device("light")
        from custom_components.lipro.light import LiproLight
        entity = LiproLight(mock_coordinator, device)
        assert entity.unique_id == device.unique_id

    def test_unique_id_with_suffix(self, mock_coordinator, make_device):
        device = make_device("fanLight")
        from custom_components.lipro.light import LiproLight
        entity = LiproLight(mock_coordinator, device)
        assert entity.unique_id == f"{device.unique_id}_light"
```

**Step 2: Run tests**

Run: `pytest tests/test_entity_base.py -v --tb=short`

**Step 3: Commit**

```bash
git add tests/test_entity_base.py
git commit -m "test: add LiproEntity base class lifecycle and debounce tests"
```

---

### Task 5: Enhance Platform Entity Tests

**Files:**
- Modify: `tests/test_light.py` — add state_attributes, color_mode tests
- Modify: `tests/test_cover.py` — add set_position command, direction optimistic update
- Modify: `tests/test_switch.py` — add feature switch command tests (fade, sleep_aid, etc.)
- Modify: `tests/test_climate.py` — add async_set_hvac_mode, async_set_preset_mode tests
- Modify: `tests/test_binary_sensor.py` — add connectivity sensor availability override test
- Modify: `tests/test_sensor.py` — add WiFi signal sensor, energy edge cases
- Modify: `tests/test_select.py` — add async_select_option tests

**What:** Each platform test file currently tests device model properties (duplicating test_device.py). Add tests that instantiate the actual entity class and verify HA-facing behavior: state attributes, command methods, entity features.

**Pattern for each platform:**

```python
class TestLiproXxxEntityCommands:
    @pytest.mark.asyncio
    async def test_command_method(self, mock_coordinator, make_device):
        device = make_device("xxx", properties={...})
        mock_coordinator.get_device = MagicMock(return_value=device)
        entity = LiproXxx(mock_coordinator, device)
        entity.async_write_ha_state = MagicMock()
        await entity.async_xxx()
        mock_coordinator.async_send_command.assert_called_once_with(...)
```

**Specific additions per platform:**

- **light.py**: `test_turn_on_with_color_temp`, `test_supported_color_modes_dynamic`, `test_brightness_ha_scale_conversion`
- **cover.py**: `test_set_position_debounced`, `test_set_position_direction_optimistic`, `test_is_opening_closing`
- **switch.py**: `test_fade_switch_turn_on/off`, `test_sleep_aid_switch`, `test_outlet_vs_switch_detection`
- **climate.py**: `test_set_hvac_mode_heat`, `test_set_hvac_mode_off`, `test_set_preset_mode`
- **binary_sensor.py**: `test_connectivity_sensor_available_when_offline`
- **sensor.py**: `test_wifi_signal_sensor`, `test_energy_safe_value_edge_cases`
- **select.py**: `test_select_wind_direction`, `test_select_gear_preset`

**Step 1: Add tests to each file**
**Step 2: Run tests per file**
**Step 3: Commit**

```bash
git add tests/test_light.py tests/test_cover.py tests/test_switch.py tests/test_climate.py tests/test_binary_sensor.py tests/test_sensor.py tests/test_select.py
git commit -m "test: enhance platform entity tests with command and state attribute coverage"
```

---

### Task 6: Add AnonymousShareManager Tests

**Files:**
- Create: `tests/test_anonymous_share.py`

**What:** Test the privacy-preserving anonymous share system. Focus on: sanitization (sensitive data detection), device recording, error recording, report building, and submit logic.

**Key test classes:**

1. `TestSanitization` — `_sanitize_value()`, `_sanitize_string()`, `_looks_sensitive()` with MAC/IP/token/device ID patterns
2. `TestDeviceRecording` — `record_device()`, `record_devices()`, deduplication
3. `TestErrorRecording` — `record_api_error()`, `record_parse_error()`, max pending limit
4. `TestReportBuilding` — `build_report()` structure, privacy guarantees
5. `TestSubmitLogic` — `submit_if_needed()` interval check, `submit_report()` HTTP mock

**Step 1: Write test_anonymous_share.py**

```python
class TestSanitization:
    def test_mac_address_detected(self):
        from custom_components.lipro.core.anonymous_share import AnonymousShareManager
        manager = AnonymousShareManager.__new__(AnonymousShareManager)
        assert manager._looks_sensitive("5C:CD:7C:XX:XX:XX") is True

    def test_ip_address_detected(self):
        ...

    def test_device_id_detected(self):
        ...

    def test_normal_value_not_sensitive(self):
        ...
```

**Step 2: Run tests**

Run: `pytest tests/test_anonymous_share.py -v --tb=short`

**Step 3: Commit**

```bash
git add tests/test_anonymous_share.py
git commit -m "test: add anonymous share manager sanitization and reporting tests"
```

---

### Task 7: Enhance Auth Manager Tests

**Files:**
- Modify: `tests/test_auth.py`

**What:** Add missing edge cases: network timeout during refresh, concurrent ensure_valid_token calls, re-login fallback when refresh fails with non-expired error, credential storage with already-hashed password.

**Specific additions:**

1. `test_refresh_token_non_expired_error_triggers_relogin` — auth error with non-20002 code falls back to re-login
2. `test_ensure_valid_token_concurrent_calls` — two concurrent calls, only one refresh
3. `test_refresh_token_no_credentials_raises` — refresh token expired + no stored credentials
4. `test_login_resets_adaptive_expiry` — after adaptive reduction, login resets to default

**Step 1: Add tests to test_auth.py**
**Step 2: Run tests**

Run: `pytest tests/test_auth.py -v --tb=short`

**Step 3: Commit**

```bash
git add tests/test_auth.py
git commit -m "test: add auth manager edge case tests for refresh fallback and concurrency"
```

---

### Task 8: Run Full Test Suite and Verify

**Step 1: Run all tests**

Run: `pytest tests/ -v --tb=short --cov=custom_components/lipro --cov-report=term-missing`

**Step 2: Verify no regressions, check coverage improvement**

**Step 3: Final commit if any cleanup needed**
