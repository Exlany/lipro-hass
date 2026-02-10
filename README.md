# Lipro Smart Home for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/Exlany/lipro-hass?style=flat-square)](https://github.com/Exlany/lipro-hass/releases)
[![License](https://img.shields.io/github/license/Exlany/lipro-hass?style=flat-square)](LICENSE)

[中文文档](README_zh.md) | English

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

## Supported Platforms & Entities

| Platform | Entity Type | Functions |
|----------|-------------|-----------|
| Light | Lights | On/Off, Brightness, Color Temperature |
| Cover | Curtains | Open/Close, Position, Stop |
| Switch | Switches/Outlets | On/Off |
| Fan | Fans | On/Off, Speed, Preset Mode |
| Climate | Bathroom Heater | On/Off, Preset Mode |
| Binary Sensor | Sensors | Motion, Door, Light, Battery |

## Services

- `lipro.send_command` - Send raw command to device

## Data Update Mechanism

This integration uses a **hybrid mode** to fetch device status:

- **MQTT Real-time Push**: Instant push when device state changes
- **Polling Fallback**: Default 30s polling to ensure state sync
- **Configurable Range**: 10-300 seconds
- **Optimistic Updates**: UI updates immediately after action
- **Debounce Protection**: Prevents data from overwriting local state during slider operations
- **Exponential Backoff**: Auto-reconnect on MQTT disconnect, prevents server overload

## Installation

### HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Exlany&repository=lipro-hass&category=integration)

1. Click the button above, or add custom repository in HACS
2. Search for "Lipro" and install
3. Restart Home Assistant
4. Add integration: Settings → Devices & Services → Add Integration → Lipro

### Manual Installation

1. Download the latest `lipro` folder
2. Copy to `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

When adding the integration, enter your Lipro account credentials:

- **Phone**: Phone number registered with Lipro
- **Password**: Lipro account password

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

## Options

Available options in integration settings:

- **Update Interval**: Device status polling interval (default 30 seconds, range 10-300 seconds)

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

## Troubleshooting

### Authentication Failed

- Ensure phone number and password are correct
- Check if Lipro official app can login normally
- If password changed, use reconfigure to update

### Device Unavailable

- Check if device is online
- Try operating device in Lipro App
- Reload the integration
- Check network connection

### State Update Delay

- This is normal for cloud polling integrations
- You can reduce update interval in options (minimum 10 seconds)
- Optimistic update happens immediately after action

### Device Not Showing

- Ensure device is paired in Lipro App
- Reload integration to sync new devices
- Check logs for error messages

### Diagnostics

To submit an issue report, please download diagnostics:

1. Go to Settings → Devices & Services → Lipro
2. Click three-dot menu → Download diagnostics
3. Diagnostics are automatically redacted, safe to share

## Disclaimer

This integration is implemented by reverse engineering the Lipro cloud API and is not officially supported. Use at your own risk.

## Contributing

Pull Requests and Issues are welcome!

## License

MIT License

---

**If this project helps you, please give it a ⭐ Star!**
