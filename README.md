# Lipro Smart Home for Home Assistant

[![CI](https://github.com/Exlany/lipro-hass/actions/workflows/ci.yml/badge.svg)](https://github.com/Exlany/lipro-hass/actions/workflows/ci.yml)
[![CodeQL](https://github.com/Exlany/lipro-hass/actions/workflows/codeql.yml/badge.svg)](https://github.com/Exlany/lipro-hass/actions/workflows/codeql.yml)
[![License](https://img.shields.io/github/license/Exlany/lipro-hass?style=flat-square)](LICENSE)

[中文说明](README_zh.md) | English | [Changelog](CHANGELOG.md)

`lipro-hass` lets Home Assistant control Lipro lights, curtains, fans, outlets, sensors, and other supported devices through the Lipro cloud service.

Minimum supported Home Assistant version: `2026.3.1`

## ✨ What You Get

- Automatic device sync from the Lipro app
- MQTT real-time updates with polling fallback
- Support for lights, covers, switches, fans, bathroom heaters, sensors, and firmware updates
- Blueprint examples for common automations
- Diagnostics export for troubleshooting

## 🔌 Supported Platforms

| Platform | Main use |
| --- | --- |
| `light` | on/off, brightness, color temperature |
| `cover` | open/close, stop, position |
| `switch` | on/off |
| `fan` | on/off, speed, preset |
| `climate` | bathroom heater controls |
| `binary_sensor` | motion, door/window, connectivity, low battery |
| `sensor` | power, energy, battery, Wi-Fi signal |
| `select` | preset-style options such as wind direction |
| `update` | firmware update entities |

## 🚀 Installation

Recommended: install through HACS as a custom repository.

1. Open HACS.
2. Go to `Integrations`.
3. Add this repository as a custom repository:
   `https://github.com/Exlany/lipro-hass`
4. Search for `Lipro Smart Home` and install it.
5. Restart Home Assistant.

One-click installer (recommended, auto latest release):

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Exlany/lipro-hass/main/install.sh)
```

If `curl` is unavailable:

```bash
wget -qO- https://raw.githubusercontent.com/Exlany/lipro-hass/main/install.sh | bash
```

Manual installation:

1. Download the latest release zip from GitHub Releases.
2. Extract it.
3. Copy `custom_components/lipro` into your Home Assistant `config/custom_components/` directory.
4. Restart Home Assistant.

For a reproducible install, pin a release tag:

```bash
ARCHIVE_TAG=vX.Y.Z bash <(curl -fsSL https://raw.githubusercontent.com/Exlany/lipro-hass/main/install.sh)
```

## ⚙️ Configuration

After restart:

Click to start the integration flow directly:

[![Open your Home Assistant instance and start setting up Lipro](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=lipro)

1. Open `Settings` -> `Devices & Services`.
2. Click `Add Integration`.
3. Search for `Lipro`.
4. Enter your Lipro account phone number and password.

If you change your password later, use `Reconfigure` on the integration instead of deleting it.

## 🧩 Common Usage

### 📘 Blueprints

- Motion light:
  [![Import Motion Light Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Exlany/lipro-hass/main/blueprints/automation/lipro/motion_light.yaml)
- Device offline alert:
  [![Import Device Offline Alert Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Exlany/lipro-hass/main/blueprints/automation/lipro/device_offline_alert.yaml)

Manual import path:

- Copy files from `blueprints/automation/lipro/`
- Paste them into `config/blueprints/automation/lipro/`

### 🛠️ Useful Services

- `lipro.refresh_devices`: refresh the device list after adding or removing devices in the Lipro app
- `lipro.get_schedules`: view weekly schedules
- `lipro.add_schedule`: add a weekly schedule
- `lipro.delete_schedules`: delete schedules by ID

## 🧪 Options

You can change these in the integration options:

- Update interval
- MQTT real-time updates
- Power monitoring for supported outlets
- Anonymous device/error sharing
- Power query interval
- Request timeout
- Debug mode for diagnostics
- Auto turn on when adjusting brightness/color temperature while off
- Cloud room to Home Assistant area sync
- Device filtering by home/model/Wi-Fi SSID/device ID

## 🩺 Troubleshooting

Start with [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

Quick checks:

- Device not showing up: confirm it already exists in the Lipro app, then run `lipro.refresh_devices`
- Login failed: confirm the same phone number and password still work in the Lipro app
- State updates are slow: keep MQTT enabled and reduce the polling interval if needed

Home Assistant diagnostics for this integration are redacted and safe to share in normal support cases.

## ⚠️ Known Limitations

- This integration uses the Lipro cloud API; local control is not supported
- Devices must already be paired in the Lipro app
- Gateway devices do not create standalone Home Assistant entities
- Frequent operations may hit cloud-side rate limits
- Some device capabilities vary by model

## 💬 Feedback

- Usage questions and bug reports: [SUPPORT.md](SUPPORT.md)
- Security issues: [SECURITY.md](SECURITY.md)
- Developer documentation: [docs/README.md](docs/README.md)

## 📄 Disclaimer

This project is based on reverse engineering of the Lipro cloud API and is not an official Lipro product.
