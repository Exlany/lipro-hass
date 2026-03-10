# Type Safety and MQTT Connection Improvements Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve type safety by reducing `Any` usage and add MQTT connection validation with timeout protection.

**Architecture:** Define TypedDict structures for API responses and add connection state verification with timeout handling in MQTT setup flow.

**Tech Stack:** Python 3.13, typing.TypedDict, asyncio.timeout, Home Assistant

---

## Chunk 1: Type Safety Improvements

### Task 1: Define API Response TypedDicts

**Files:**
- Create: `custom_components/lipro/core/api/types.py`
- Modify: `custom_components/lipro/core/api/client_base.py`

**Context:** Currently API methods return `Any`, making runtime type errors hard to track. We'll define TypedDict structures for common API responses.

- [ ] **Step 1: Create types module with base response structures**

Create `custom_components/lipro/core/api/types.py`:

```python
"""Type definitions for API responses."""

from __future__ import annotations

from typing import Any, TypedDict


class ApiResponse(TypedDict, total=False):
    """Base API response structure."""

    code: int
    msg: str
    data: Any


class LoginResponse(TypedDict):
    """Login API response data."""

    access_token: str
    refresh_token: str
    expires_in: int
    user_id: str


class DeviceListItem(TypedDict, total=False):
    """Device list item structure."""

    serial: str
    deviceId: str
    iotDeviceId: str
    name: str
    deviceType: int
    online: bool
    properties: dict[str, Any]


class DeviceListResponse(TypedDict):
    """Device list API response data."""

    devices: list[DeviceListItem]
    total: int


class DeviceStatusItem(TypedDict, total=False):
    """Device status item structure."""

    iotId: str
    properties: dict[str, Any]


class MqttConfigResponse(TypedDict, total=False):
    """MQTT config API response data."""

    accessKey: str
    secretKey: str
    endpoint: str
    port: int


__all__ = [
    "ApiResponse",
    "LoginResponse",
    "DeviceListItem",
    "DeviceListResponse",
    "DeviceStatusItem",
    "MqttConfigResponse",
]
```

- [ ] **Step 2: Verify module compiles**

Run: `python3 -m py_compile custom_components/lipro/core/api/types.py`
Expected: No output (success)

- [ ] **Step 3: Commit type definitions**

```bash
git add custom_components/lipro/core/api/types.py
git commit -m "feat(api): add TypedDict definitions for API responses"
```

---

### Task 2: Update Auth Service Type Annotations

**Files:**
- Modify: `custom_components/lipro/core/api/auth_service.py`
- Import: `custom_components/lipro/core/api/types.py`

- [ ] **Step 1: Update login method return type**

In `custom_components/lipro/core/api/auth_service.py`, find the `login` method and update:

```python
from .types import ApiResponse, LoginResponse

async def login(
    self, phone: str, password_hash: str, *, password_is_hashed: bool = False
) -> LoginResponse:
    """Login to Lipro cloud.

    Returns:
        LoginResponse with access_token, refresh_token, expires_in, user_id
    """
    # ... existing implementation
    response: ApiResponse = await self._client.request(...)
    return response["data"]  # type: ignore[return-value]
```

- [ ] **Step 2: Update refresh_token method return type**

```python
async def refresh_token(self, refresh_token: str) -> LoginResponse:
    """Refresh access token.

    Returns:
        LoginResponse with new tokens
    """
    # ... existing implementation
    response: ApiResponse = await self._client.request(...)
    return response["data"]  # type: ignore[return-value]
```

- [ ] **Step 3: Verify compilation**

Run: `python3 -m py_compile custom_components/lipro/core/api/auth_service.py`
Expected: No output (success)

- [ ] **Step 4: Run type checker**

Run: `mypy custom_components/lipro/core/api/auth_service.py --no-error-summary 2>&1 | head -20`
Expected: Fewer `Any` warnings

- [ ] **Step 5: Commit auth service improvements**

```bash
git add custom_components/lipro/core/api/auth_service.py
git commit -m "refactor(api): improve type safety in auth service"
```

---

### Task 3: Update Device Endpoints Type Annotations

**Files:**
- Modify: `custom_components/lipro/core/api/endpoints/devices.py`
- Import: `custom_components/lipro/core/api/types.py`

- [ ] **Step 1: Update get_device_list return type**

```python
from ..types import ApiResponse, DeviceListResponse

async def get_device_list(
    self, page: int = 1, page_size: int = 100
) -> DeviceListResponse:
    """Get device list from cloud.

    Returns:
        DeviceListResponse with devices list and total count
    """
    # ... existing implementation
    response: ApiResponse = await self._client.request(...)
    return response["data"]  # type: ignore[return-value]
```

- [ ] **Step 2: Update query_device_status return type**

```python
from ..types import DeviceStatusItem

async def query_device_status(
    self, device_ids: list[str]
) -> list[DeviceStatusItem]:
    """Query device status batch.

    Returns:
        List of device status items
    """
    # ... existing implementation
    response: ApiResponse = await self._client.request(...)
    return response["data"]  # type: ignore[return-value]
```

- [ ] **Step 3: Verify compilation**

Run: `python3 -m py_compile custom_components/lipro/core/api/endpoints/devices.py`
Expected: No output (success)

- [ ] **Step 4: Commit device endpoints improvements**

```bash
git add custom_components/lipro/core/api/endpoints/devices.py
git commit -m "refactor(api): improve type safety in device endpoints"
```

---

### Task 4: Update Status Service Type Annotations

**Files:**
- Modify: `custom_components/lipro/core/api/status_service.py`
- Import: `custom_components/lipro/core/api/types.py`

- [ ] **Step 1: Update query_device_status return type**

```python
from .types import DeviceStatusItem

async def query_device_status(
    self, device_ids: list[str]
) -> list[DeviceStatusItem]:
    """Query device status from cloud API.

    Returns:
        List of device status items with iotId and properties
    """
    # ... existing implementation
```

- [ ] **Step 2: Verify compilation**

Run: `python3 -m py_compile custom_components/lipro/core/api/status_service.py`
Expected: No output (success)

- [ ] **Step 3: Commit status service improvements**

```bash
git add custom_components/lipro/core/api/status_service.py
git commit -m "refactor(api): improve type safety in status service"
```

---

## Chunk 2: MQTT Connection Improvements

### Task 5: Add MQTT Connection Validation

**Files:**
- Modify: `custom_components/lipro/core/coordinator/coordinator.py` (async_setup_mqtt method)
- Modify: `custom_components/lipro/core/mqtt/client.py` (if connect method exists)

**Context:** Currently MQTT connection has no timeout protection and no state verification, which can cause startup to hang.

- [ ] **Step 1: Add timeout to MQTT setup in coordinator**

In `custom_components/lipro/core/coordinator/coordinator.py`, find `async_setup_mqtt` method:

```python
async def async_setup_mqtt(self) -> bool:
    """Set up MQTT client for real-time updates.

    Returns:
        True if setup succeeded, False otherwise
    """
    if self.config_entry is None:
        _LOGGER.error("Cannot setup MQTT: config_entry is None")
        return False

    try:
        # Get encrypted MQTT credentials from API (with timeout)
        async with asyncio.timeout(10):
            mqtt_config = await self.client.get_mqtt_config()
            if not mqtt_config:
                _LOGGER.warning("No MQTT config available")
                return False

        # Decrypt credentials
        access_key = decrypt_mqtt_credential(mqtt_config.get("accessKey", ""))
        secret_key = decrypt_mqtt_credential(mqtt_config.get("secretKey", ""))

        if not access_key or not secret_key:
            _LOGGER.warning("Invalid MQTT credentials")
            return False

        # ... rest of setup

        # Start MQTT connection with timeout
        async with asyncio.timeout(15):
            await self._mqtt_runtime.connect(device_ids=device_ids, biz_id=biz_id)

        # Verify connection state
        if not self._mqtt_runtime.is_connected:
            _LOGGER.warning("MQTT connection failed to establish")
            return False

        _LOGGER.info("MQTT setup completed successfully")
        return True

    except TimeoutError:
        _LOGGER.error("MQTT setup timeout")
        return False
    except Exception as err:
        # Re-raise system exceptions
        if isinstance(err, (asyncio.CancelledError, KeyboardInterrupt, SystemExit)):
            raise
        _LOGGER.warning("Failed to setup MQTT: %s", err)
        return False
```

- [ ] **Step 2: Verify compilation**

Run: `python3 -m py_compile custom_components/lipro/core/coordinator/coordinator.py`
Expected: No output (success)

- [ ] **Step 3: Test timeout behavior (manual verification)**

Expected behavior:
- If MQTT config fetch takes >10s, timeout and return False
- If MQTT connect takes >15s, timeout and return False
- If connection succeeds but is_connected is False, return False

- [ ] **Step 4: Commit MQTT connection improvements**

```bash
git add custom_components/lipro/core/coordinator/coordinator.py
git commit -m "fix(mqtt): add timeout protection and connection state verification"
```

---

### Task 6: Add MQTT Runtime Connection State Property

**Files:**
- Verify: `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py`

**Context:** Verify that `is_connected` property exists and works correctly.

- [ ] **Step 1: Check if is_connected property exists**

Run: `grep -n "def is_connected" custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py`
Expected: Should find the property definition

- [ ] **Step 2: If property exists, verify it returns correct state**

Read the property implementation and verify it checks `_connection_manager.is_connected`

- [ ] **Step 3: If property doesn't exist, add it**

```python
@property
def is_connected(self) -> bool:
    """Return current MQTT connection state."""
    return self._connection_manager.is_connected
```

- [ ] **Step 4: Verify compilation**

Run: `python3 -m py_compile custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py`
Expected: No output (success)

- [ ] **Step 5: Commit if changes were made**

```bash
git add custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py
git commit -m "feat(mqtt): ensure is_connected property exists"
```

---

## Chunk 3: Documentation and Verification

### Task 7: Update CODE_QUALITY_REVIEW.md

**Files:**
- Modify: `CODE_QUALITY_REVIEW.md`

- [ ] **Step 1: Mark type safety issue as resolved**

Update the "Top 5 最严重问题" section to move type safety to "已修复问题":

```markdown
### 5. ✓ **类型安全改进** (已修复)
**原问题**: 过度使用 `Any` 类型
**修复**:
- 定义 TypedDict 结构（ApiResponse, LoginResponse, DeviceListResponse 等）
- 更新 auth_service, endpoints/devices, status_service 的类型注解
- 减少运行时类型错误风险
```

- [ ] **Step 2: Mark MQTT connection issue as resolved**

```markdown
### 6. ✓ **MQTT 连接验证** (已修复)
**原问题**: 连接失败时无超时保护，无连接状态验证
**修复**:
- 添加 10 秒超时保护（获取 MQTT 配置）
- 添加 15 秒超时保护（建立连接）
- 添加连接状态验证（is_connected 检查）
```

- [ ] **Step 3: Update quality scores**

Update the overall scores:

```markdown
│  可靠性 (Reliability)                     █████████░  8.5/10 │
│  安全性 (Security)                        ███████░░░  6.8/10 │
│  可维护性 (Maintainability)               ████████░░  8.5/10 │
├─────────────────────────────────────────────────────────────┤
│  综合评分                                 ████████░░  8.3/10  │
│  等级评定                                 A- (优秀)           │
```

- [ ] **Step 4: Commit documentation updates**

```bash
git add CODE_QUALITY_REVIEW.md
git commit -m "docs: update quality review with type safety and MQTT improvements"
```

---

### Task 8: Run Full Test Suite

**Files:**
- None (verification only)

- [ ] **Step 1: Run type checker on modified files**

Run: `mypy custom_components/lipro/core/api/ --no-error-summary 2>&1 | grep -E "error|warning" | wc -l`
Expected: Reduced error/warning count compared to before

- [ ] **Step 2: Run unit tests**

Run: `pytest tests/ -v --tb=short 2>&1 | tail -20`
Expected: All tests pass

- [ ] **Step 3: Verify no syntax errors**

Run: `python3 -m py_compile custom_components/lipro/**/*.py 2>&1 | head -10`
Expected: No errors

- [ ] **Step 4: Document test results**

Create summary of test results for final commit message.

---

## Execution Notes

**Parallel Execution Strategy:**
- Chunk 1 (Type Safety) and Chunk 2 (MQTT) are independent
- Can be executed by separate subagents in parallel
- Chunk 3 (Documentation) depends on both and must run last

**Review Checkpoints:**
- After Task 4: Review type annotations for consistency
- After Task 6: Test MQTT connection behavior manually
- After Task 8: Final verification before completion

**Rollback Strategy:**
- Each task has atomic commits
- If issues found, revert specific commits
- Type changes are additive (won't break existing code)

---

## Success Criteria

- [ ] All TypedDict definitions compile without errors
- [ ] Type checker shows reduced `Any` usage warnings
- [ ] MQTT setup has timeout protection (10s + 15s)
- [ ] MQTT connection state is verified before returning success
- [ ] All existing tests pass
- [ ] Documentation updated to reflect improvements
- [ ] Quality score improved to 8.3/10 (A-)

---

**Plan Status:** Ready for execution
**Estimated Time:** 45-60 minutes with parallel subagents
**Risk Level:** Low (additive changes, atomic commits)
