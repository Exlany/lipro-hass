# Lipro Smart Home for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/Exlany/lipro-hass?style=flat-square)](https://github.com/Exlany/lipro-hass/releases)
[![License](https://img.shields.io/github/license/Exlany/lipro-hass?style=flat-square)](LICENSE)

[中文文档](README_zh.md) | English | [更新日志](CHANGELOG.md)

Home Assistant integration for controlling Lipro Smart Home devices.

## Features

- 🔌 Support for multiple Lipro device types
- 🔄 Automatic cloud device synchronization
- 📡 MQTT real-time push, instant state updates
- ⚡ Optimistic state updates for fast response
- 🎚️ Slider debouncing to prevent API flooding
- 🔁 Exponential backoff reconnection for stability
- 🌐 Bilingual support (Chinese & English)
- 🔧 Diagnostics support for troubleshooting
- 🏗️ Modern architecture with composition-based design (refactored 2026-03)

## Supported Platforms & Entities

| Platform | Entity Type | Functions |
|----------|-------------|-----------|
| Light | Lights | On/Off, Brightness, Color Temperature |
| Cover | Curtains | Open/Close, Position, Stop |
| Switch | Switches/Outlets | On/Off |
| Fan | Fans | On/Off, Speed, Preset Mode |
| Climate | Bathroom Heater | On/Off, Preset Mode |
| Binary Sensor | Sensors | Connectivity, Motion, Door/Window, Light Level, Battery |
| Sensor | Sensors | Power, Energy, Battery, WiFi Signal |
| Select | Selects | Wind Direction, Heater Light, Color Temp Preset |
| Update | Firmware | Firmware updates |

## Services

- `lipro.send_command` - Send raw command to device
- `lipro.get_schedules` - Get recurring weekly schedules; weekdays use `1=Monday` to `7=Sunday`. For mesh groups, reads use BLE/gateway-member candidates as the source of truth. On tested mesh BLE schedules, standard `schedule/get.do` may return empty success, so do not assume a reliable read fallback
- `lipro.add_schedule` - Add a recurring weekly schedule; no absolute-date schedule mode is exposed. Mesh groups write through BLE/gateway-member candidates only, because tested standard `schedule/addOrUpdate.do` is not a reliable fallback
- `lipro.delete_schedules` - Delete schedules by IDs; mesh groups delete through BLE/gateway-member candidates only, because tested standard `schedule/delete.do` may report success without deleting the target schedule
- `lipro.submit_anonymous_share` - Submit anonymous share report manually
- `lipro.get_anonymous_share_report` - Preview anonymous share report
- `lipro.get_developer_report` - Export a redacted local debugging report; keeps vendor diagnosis identifiers such as `iotName` plus local labels to identify the device under test (all entries or one `entry_id`)
- `lipro.submit_developer_feedback` - One-click submit developer diagnostics; upload keeps `iotName` but anonymizes user-defined labels such as device/room/panel/IR names (all entries or one `entry_id`)
- `lipro.query_command_result` - Query cloud-reported command status by message serial number with bounded polling (developer capability)
- `lipro.get_city` - Query cloud city metadata using the verified empty-object payload contract (developer capability)
- `lipro.query_user_cloud` - Query user cloud metadata using the verified raw empty-body contract (`-d ''`); tested responses may contain only top-level `data` without a `code` wrapper (developer capability)
- `lipro.fetch_body_sensor_history` - Fetch body sensor history payload for debugging (developer capability)
- `lipro.fetch_door_sensor_history` - Fetch door sensor history payload for debugging (developer capability)
- `lipro.refresh_devices` - Force a full device list refresh (all entries or one `entry_id`)

Firmware validation list:
- Certified firmware versions: `custom_components/lipro/firmware_support_manifest.json`
- OTA update entities show available firmware (uncertified firmware may require confirmation)

## Data Update Mechanism

This integration uses a **hybrid mode** to fetch device status:

- **MQTT Real-time Push**: Instant push when device state changes
- **MQTT Topic Format**: Subscriptions use `Topic_Device_State/{bizId}/{deviceId}` with the bare `bizId` (any stored `lip_` prefix is removed before subscribing)
- **MQTT Config Payload**: `get_mqtt_config` may return top-level `accessKey` / `secretKey`, and the integration consumes that direct payload without requiring a wrapped `data` object
- **Polling Fallback**: Default 30s polling to ensure state sync
- **Configurable Range**: 10-300 seconds
- **Batch Query Fallback**: Cloud status requests are chunked; when a batch fails with device-level errors (offline/not connected/etc.), the integration retries with smaller batches down to per-device queries
- **Optimistic Updates**: UI updates immediately after action
- **Debounce Protection**: Prevents data from overwriting local state during slider operations
- **Exponential Backoff**: Auto-reconnect on MQTT disconnect, prevents server overload

## Installation

Minimum supported Home Assistant version: `2026.3.1` (canonical source: `pyproject.toml`).

Private repository / fork note: CI skips HACS validation because HACS only supports public GitHub repositories.

### HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Exlany&repository=lipro-hass&category=integration)

1. Click the button above, or add custom repository in HACS
2. Search for "Lipro" and install
3. Restart Home Assistant
4. Add integration: Settings → Devices & Services → Add Integration → Lipro

### Shell (Verified Release Assets)

```shell
# Download these release assets from GitHub Releases first:
#   - install.sh
#   - lipro-hass-v1.0.0.zip
#   - SHA256SUMS

# Optional local verification (the installer also verifies with Python/hashlib)
sha256sum -c SHA256SUMS --ignore-missing

# Supported shell install path
bash ./install.sh --archive-file ./lipro-hass-v1.0.0.zip --checksum-file ./SHA256SUMS
```

Note: the supported shell installer path now starts from downloaded GitHub Release assets. The installer verifies the archive checksum itself and fails closed when the zip or `SHA256SUMS` is missing or mismatched.

### Advanced Preview Path (Unsupported)

```shell
# Explicitly opt into the bleeding-edge branch
ARCHIVE_TAG=main bash ./install.sh

# Mirror + preview path (DANGEROUS; only if you trust the mirror)
ARCHIVE_TAG=main LIPRO_ALLOW_MIRROR=1 HUB_DOMAIN=ghfast.top bash ./install.sh
```

Note: `ARCHIVE_TAG=main`, branch fallback, and mirror installs are preview / unsupported paths for maintainers and advanced testers. Prefer verified release assets for production installs.

### Release Asset Trust

- Stable install trust starts from verified GitHub Release assets plus `SHA256SUMS`.
- Current release identity evidence also publishes an `SBOM` and GitHub artifact `attestation` / `provenance`, verifiable with `gh attestation verify`.
- This is release identity / provenance evidence, not artifact signing.
- `signing` and GitHub `code scanning` remain explicit deferred roadmap items, not current hard gates.

### shell_command Service

1. Download `install.sh`, `lipro-hass-v1.0.0.zip`, and `SHA256SUMS` into a stable local directory first (for example `/config/lipro-release/`).
2. Add the following to your `configuration.yaml`:
    ```yaml
    shell_command:
      update_lipro: >-
        bash /config/lipro-release/install.sh
        --archive-file /config/lipro-release/lipro-hass-v1.0.0.zip
        --checksum-file /config/lipro-release/SHA256SUMS
    ```
3. Restart Home Assistant
4. Call `service: shell_command.update_lipro` in Developer Tools
5. Restart Home Assistant again

### Manual Installation

1. Download `lipro-hass-v1.0.0.zip` from [Releases](https://github.com/Exlany/lipro-hass/releases)
2. Verify it against `SHA256SUMS`
3. Extract the archive and copy `custom_components/lipro` to your `config/custom_components/` directory
4. Restart Home Assistant

## Configuration

When adding the integration, enter your Lipro account credentials:

- **Phone**: Phone number registered with Lipro
- **Password**: Lipro account password
- **Remember password**: Store the password MD5 hash locally to allow automatic re-login when refresh tokens expire. Disable to reduce local exposure; you may need to re-authenticate later.

### Reconfiguration

To modify account information, click "Configure" on the integration page to reconfigure.

## Tested Devices

| Device Type | Model | Status |
|-------------|-------|--------|
| LED Strip | - | ✅ Tested |
| Ceiling Lamp | - | ✅ Tested |
| Fan Light | - | ✅ Tested |
| Curtain Motor | - | ✅ Tested |
| Smart Panel | - | ✅ Tested |
| Smart Outlet | - | ✅ Tested |
| Bathroom Heater | - | ✅ Tested |
| Motion Sensor M1 | - | ✅ Tested |
| Door Sensor D1 | - | ✅ Tested |
| Desk Lamp | - | ⚠️ Untested |
| Gateway | - | ❌ Not Supported |

> 💡 **Feedback Welcome!** If you have other Lipro devices, please report in [Issues](https://github.com/Exlany/lipro-hass/issues) to help us improve device support.

## Use Cases

### Scenario 1: Automated Lighting

```yaml
automation:
  - alias: "Turn on lights at sunset"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: light.turn_on
        target:
          entity_id: light.living_room_ceiling
        data:
          brightness_pct: 80
          color_temp_kelvin: 4000
```

### Scenario 2: Motion-Activated Lighting

```yaml
automation:
  - alias: "Motion activated light"
    trigger:
      - platform: state
        entity_id: binary_sensor.hallway_motion
        to: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.hallway_light
```

### Scenario 3: Scheduled Curtain Control

```yaml
automation:
  - alias: "Open curtains in the morning"
    trigger:
      - platform: time
        at: "07:30:00"
    condition:
      - condition: state
        entity_id: binary_sensor.workday
        state: "on"
    action:
      - service: cover.open_cover
        target:
          entity_id: cover.bedroom_curtain
```

## Official Blueprints

Importable Home Assistant blueprints:

- Motion light (turn on at motion, turn off after no-motion delay):  
  [![Import Motion Light Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://github.com/Exlany/lipro-hass/blob/main/blueprints/automation/lipro/motion_light.yaml)
- Device offline alert (notify when entities stay unavailable):  
  [![Import Device Offline Alert Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://github.com/Exlany/lipro-hass/blob/main/blueprints/automation/lipro/device_offline_alert.yaml)

Manual import:

1. Copy files under `blueprints/automation/lipro/` into your Home Assistant config path `config/blueprints/automation/lipro/`.
2. Go to Settings → Automations & Scenes → Blueprints and create automations from imported blueprints.

## Advanced Features

### Send Raw Command

The integration provides a `lipro.send_command` service for advanced users:

```yaml
service: lipro.send_command
target:
  entity_id: light.living_room_light
data:
  command: CHANGE_STATE
  properties:
    - key: brightness
      value: "80"
```

### Available Commands

| Command | Description |
|---------|-------------|
| POWER_ON | Turn on device |
| POWER_OFF | Turn off device |
| CHANGE_STATE | Change state |
| CURTAIN_OPEN | Open curtain |
| CURTAIN_CLOSE | Close curtain |
| CURTAIN_STOP | Stop curtain |

### Firmware Update

Firmware updates are exposed as Home Assistant `update` entities (Settings → Devices & Services → Lipro → device → Entities).

## Options

Available options in integration settings:

- **Update Interval**: Device status polling interval (default 30 seconds, range 10-300 seconds)
- **Enable MQTT Real-time Updates**: Use MQTT push updates (recommended)
- **Enable Power Monitoring**: Query outlet power metrics
- **Anonymous Share Device Info**: Opt-in device capability sharing
- **Anonymous Share Error Reports**: Opt-in anonymized error reports
- **Advanced Options**:
  - **Power Query Interval**: Outlet power query frequency (default 300 seconds / ~5 minutes, range 30-300 seconds)
  - **Request Timeout**: API request timeout (10-60 seconds)
  - **Debug Mode (Diagnostics)**: Capture runtime diagnostics (mesh topology + command traces). For verbose logs, configure Home Assistant logger settings.
  - **Auto Turn On When Adjusting While Off**: When enabled, adjusting brightness/color temperature while off will also turn on the light (disable to keep Lipro behavior)
  - **Force Cloud Room → HA Area**: Always overwrite Home Assistant area with cloud room assignment (use with caution)
  - **Check Command Result Status**: Default on (recommended). Poll cloud-reported command result status by `msgSn` after sending commands for a safer control loop. This does not guarantee delivery or device execution
  - **Device Filtering (home/model/WiFi SSID/device ID)**: `off/include/exclude` + list (supports comma/semicolon/newline separators; matching is case-insensitive)

## Known Limitations

1. **Cloud Control Only**
   - This integration controls devices via Lipro cloud API, local control is not supported

2. **No Local Discovery**
   - Devices must be paired in Lipro App first, this integration cannot discover new devices

3. **Gateway Not Supported**
   - Gateway devices only act as bridges, no entities will be created

4. **API Limitations**
   - Frequent operations may trigger API rate limiting

5. **Sensor Battery**
   - Sensors only provide low battery warning, not specific battery percentage

6. **Brightness Slider While Off (Tip)**
   - Default behavior is configurable. When **Auto Turn On When Adjusting While Off** is enabled, adjusting brightness/color temperature while off will also turn on the light
   - Disable it to keep Lipro behavior (adjustments do not turn on)

## Troubleshooting

Canonical troubleshooting guide: `docs/TROUBLESHOOTING.md`.

### Quick Checks

#### Authentication Failed

- Ensure the phone number and password still work in the Lipro app.
- If the password changed, use reconfigure/update credentials instead of deleting the integration.
- For repeated reauth failures, start with diagnostics; add a redacted developer report only when diagnostics still do not explain the failure or when a maintainer asks for deeper debugging.
- If available, also include `failure_summary` / `failure_entries` from diagnostics, system health, or developer-report exports.

#### Device Unavailable / Not Showing

- Confirm the device already exists in the Lipro app.
- Reload the integration or run `lipro.refresh_devices` after adding hardware.
- Gateway devices only act as bridges and do not create Home Assistant entities by themselves.

#### State Update Delay / MQTT Drift

- MQTT push is best effort; polling remains the safety net.
- Reduce the polling interval in options if needed (minimum 10 seconds).
- When drift persists, mention whether the issue is cloud polling, MQTT push, or entity projection.
- If the affected path exposes `failure_summary` or aggregated `failure_entries`, include those fields in the report as well.

### Diagnostics & Safe Sharing

1. Go to Settings → Devices & Services → Lipro.
2. Click the three-dot menu → Download diagnostics.
3. Diagnostics are automatically redacted and safe to share.

Redaction includes account credentials/tokens (`phone`, `password`, `access_token`, `refresh_token`), cloud/device identifiers (`userId`/`bizId`, `serial`/`deviceId`/`iotDeviceId`), and network identifiers (WiFi SSID/MAC/IP).

If diagnostics are not enough, or a maintainer asks for deeper debugging, you can preview or submit the opt-in payloads first:
- `lipro.get_developer_report` - local debugging report; keeps vendor diagnosis identifiers such as `iotName` plus local labels so you can recognize the device under test
- `lipro.submit_developer_feedback` - upload contract; keeps `iotName` but anonymizes user-defined labels such as device/room/panel/IR names before upload
- When available, include `failure_summary` / `failure_entries` alongside diagnostics so maintainers can classify the failure path faster
- `lipro.get_anonymous_share_report` - sanitized anonymous-share payload

See also: `SUPPORT.md` for routing, `SECURITY.md` for private vulnerability disclosure, and `docs/MAINTAINER_RELEASE_RUNBOOK.md` for maintainer-only release issues.

## Disclaimer

This integration is implemented by reverse engineering the Lipro cloud API and is not officially supported. Use at your own risk.

## Support Model

- Stable support targets: the latest tagged release and the matching HACS install
- Preview paths (`ARCHIVE_TAG=main`, branch fallback, mirror installs): best effort only
- Triage and release custody follow a single-maintainer model; if the maintainer is unavailable, release promises freeze rather than silently bypassing gates or implying a hidden backup maintainer
- Deep-doc continuity follows the same story: `SUPPORT.md`, `SECURITY.md`, `docs/TROUBLESHOOTING.md`, and `docs/MAINTAINER_RELEASE_RUNBOOK.md` must stay aligned on custody / freeze truth

## Contributing

- Bug reports and pull requests: start with `CONTRIBUTING.md` and the GitHub issue / PR templates
- Usage questions and idea discussion: start with `SUPPORT.md` and GitHub Discussions
- Security issues: follow `SECURITY.md` and use private disclosure first
- Community expectations: `CODE_OF_CONDUCT.md`

## Documentation

- `docs/README.md` - canonical documentation map and archive guide
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` - target architecture and authority baseline
- `docs/developer_architecture.md` - current package layout and runtime/control/protocol flow
- `docs/TROUBLESHOOTING.md` - canonical troubleshooting and diagnostics path
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` - maintainer release/tag/package workflow
- `docs/adr/README.md` - long-lived architecture decisions and trade-offs
- `CONTRIBUTING.md` - contributor workflow, CI contract, and review expectations
- `SUPPORT.md` - support routing, triage expectations, and question handling
- `SECURITY.md` - private vulnerability disclosure policy
- `CODE_OF_CONDUCT.md` - community behavior expectations
- `custom_components/lipro/quality_scale.yaml` - Home Assistant quality-scale mapping
- `.devcontainer.json` - reproducible development container settings
- `AGENTS.md` - canonical cross-agent repository contract
- `CLAUDE.md` - Claude Code compatibility entry, always defers to `AGENTS.md`

## License

MIT License

---

**If this project helps you, please give it a ⭐ Star!**
