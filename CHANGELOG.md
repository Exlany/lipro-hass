# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-02-08

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
