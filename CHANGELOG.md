# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- One-click installation script for custom component setup.
- Device diagnostics reporting and stronger diagnostics redaction test coverage.

### Changed

- Migrated project dependency metadata to `pyproject.toml` and added `uv.lock`.
- Consolidated CI type-checking into lint workflow to reduce redundant setup.
- Refactored coordinator update/command workflows for better maintainability.
- Refactored anonymous share capability detection logic with clearer rule-based mapping.
- Refactored shared sensor entity setup and applied broad type-safety/code-quality cleanup.
- Refactored coordinator room-sync and stale-device registry operations into
  `core/device/device_registry_sync.py` to keep `coordinator.py` focused on orchestration.
- Refactored device identity indexing to use strict registration APIs and removed
  legacy direct-mutation compatibility paths.
- Removed `core.api` legacy compatibility aliases in favor of canonical
  submodule symbols (`api_response_safety` / `request_policy`).
- Removed `login_with_hash` compatibility entry points; config flow now uses
  `login(..., password_is_hashed=True)` directly.
- Refactored platform modules to import helper submodules directly and removed
  `helpers` package-level compatibility re-exports.
- Removed root-module legacy service contract re-exports; canonical source is
  now `services/contracts.py`.

### Fixed

- Improved authentication issue lifecycle handling (repair notifications and reauth flow).
- Prevented anonymous-share crash paths and improved refresh stability.
- Redacted `wifiSsid` and related sensitive fields in diagnostics/anonymous share payloads.
- Hardened property parsing against malformed API items.
- Restored `PROP_FAN_ONOFF` export and cleaned import-order issues.
- Corrected brightness rounding and motion sensor capability detection behavior.
- Fixed aiodns/pycares compatibility by refining dependency constraints.
- Added missing light platform icons and corrected command/device-id examples.
- Fixed forced room-area sync to converge user-modified areas even when cloud room names are unchanged.
- Fixed stale-device reconciliation to use unfiltered cloud serials and cold-start registry bootstrap, preventing filter-induced false removals.
- Hardened bool-like coercion debug logs to avoid recording raw unexpected values.
- Hardened sensitive-data redaction for international phone values and numeric
  `user_id`/`biz_id` fields, and masked reauth phone placeholders in UI.
- Reduced redundant full-batch retries in status fallback flow to cut repeated
  API calls under retriable batch-failure paths.

## [1.0.0] - 2026-02-08

### Added

- Initial release of Lipro Smart Home integration for Home Assistant
- Cloud API integration with MQTT real-time push updates
- Supported device types:
  - Light (灯光): on/off, brightness, color temperature
  - Cover (窗帘): open/close, position, stop
  - Switch (开关/插座): on/off
  - Fan (风扇): on/off, speed, preset mode
  - Climate (浴霸): on/off, preset mode
  - Binary Sensor (传感器): motion, door/window, light, battery
- Config flow with phone number and password authentication
- Options flow for configuring update interval (10-300 seconds)
- Re-authentication and reconfigure flows
- Optimistic state updates for instant UI feedback
- Slider debouncing to prevent API flooding
- MQTT exponential backoff reconnection
- Custom service `lipro.send_command` for advanced users
- Bilingual support (Chinese & English)
- Diagnostics support with sensitive data masking
