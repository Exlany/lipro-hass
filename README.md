# Lipro Smart Home for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/Exlany/lipro-hass?style=flat-square)](https://github.com/Exlany/lipro-hass/releases)
[![License](https://img.shields.io/github/license/Exlany/lipro-hass?style=flat-square)](LICENSE)

Home Assistant 集成，用于控制 Lipro 智能家居设备。

Home Assistant integration for controlling Lipro Smart Home devices.

## 功能特性 / Features

- 🔌 支持多种 Lipro 设备类型 / Support for multiple Lipro device types
- 🔄 云端设备自动同步 / Automatic cloud device synchronization
- 📡 MQTT 实时推送，状态秒级更新 / MQTT real-time push, instant state updates
- ⚡ 乐观状态更新，响应迅速 / Optimistic state updates for fast response
- 🎚️ 滑块防抖，避免 API 过载 / Slider debouncing to prevent API flooding
- 🔁 指数退避重连，稳定可靠 / Exponential backoff reconnection for stability
- 🌐 中英文双语支持 / Bilingual support (Chinese & English)
- 🔧 诊断支持，便于故障排查 / Diagnostics support for troubleshooting

## 支持的功能 / Supported Functions

### 平台和实体 / Platforms & Entities

| 平台 / Platform | 实体类型 / Entity Type | 功能 / Functions |
|----------------|----------------------|------------------|
| Light | 灯光 | 开关、亮度、色温 / On/Off, Brightness, Color Temperature |
| Cover | 窗帘 | 开关、位置、停止 / Open/Close, Position, Stop |
| Switch | 开关/插座 | 开关 / On/Off |
| Fan | 风扇 | 开关、风速、模式 / On/Off, Speed, Preset Mode |
| Climate | 浴霸 | 开关、模式 / On/Off, Preset Mode |
| Binary Sensor | 传感器 | 人体感应、门窗状态、光照、电池 / Motion, Door, Light, Battery |

### 服务 / Services

- `lipro.send_command` - 发送原始命令到设备 / Send raw command to device

## 数据更新机制 / Data Update Mechanism

本集成使用**混合模式**获取设备状态：

This integration uses a **hybrid mode** to fetch device status:

- **MQTT 实时推送 / MQTT Real-time Push**: 设备状态变化时立即推送 / Instant push when device state changes
- **轮询兜底 / Polling Fallback**: 默认 30 秒轮询，确保状态同步 / Default 30s polling to ensure state sync
- **可配置范围 / Configurable Range**: 10-300 秒 / 10-300 seconds
- **乐观更新 / Optimistic Updates**: 操作后立即更新 UI，无需等待推送 / UI updates immediately after action
- **防抖保护 / Debounce Protection**: 滑块操作时防止数据覆盖本地状态 / Prevents data from overwriting local state during slider operations
- **指数退避 / Exponential Backoff**: MQTT 断连时自动重连，避免服务器过载 / Auto-reconnect on MQTT disconnect, prevents server overload

## 安装 / Installation

### HACS (推荐 / Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Exlany&repository=lipro-hass&category=integration)

1. 点击上方按钮，或在 HACS 中添加自定义仓库

   Click the button above, or add custom repository in HACS

2. 搜索 "Lipro" 并安装

   Search for "Lipro" and install

3. 重启 Home Assistant

   Restart Home Assistant

4. 添加集成：设置 → 设备与服务 → 添加集成 → Lipro

   Add integration: Settings → Devices & Services → Add Integration → Lipro

### 手动安装 / Manual Installation

1. 下载最新版本的 `lipro` 文件夹

   Download the latest `lipro` folder

2. 复制到 `config/custom_components/` 目录

   Copy to `config/custom_components/` directory

3. 重启 Home Assistant

   Restart Home Assistant

## 配置 / Configuration

添加集成时，需要输入您的 Lipro 账号信息：

When adding the integration, enter your Lipro account credentials:

- **手机号 / Phone**: 注册 Lipro 的手机号 / Phone number registered with Lipro
- **密码 / Password**: Lipro 账号密码 / Lipro account password

### 重新配置 / Reconfiguration

如需修改账号信息，可以在集成页面点击"配置"进行重新配置。

To modify account information, click "Configure" on the integration page to reconfigure.

## 已测试设备 / Tested Devices

| 设备类型 / Device Type | 型号 / Model | 状态 / Status |
|----------------------|-------------|---------------|
| LED 灯带 / LED Strip | - | ✅ 已测试 / Tested |
| 吸顶灯 / Ceiling Lamp | - | ✅ 已测试 / Tested |
| 风扇灯 / Fan Light | - | ✅ 已测试 / Tested |
| 窗帘电机 / Curtain Motor | - | ✅ 已测试 / Tested |
| 智能面板 / Smart Panel | - | ✅ 已测试 / Tested |
| 智能插座 / Smart Outlet | - | ✅ 已测试 / Tested |
| 浴霸 / Bathroom Heater | - | ✅ 已测试 / Tested |
| 人体传感器 M1 / Motion Sensor M1 | - | ✅ 已测试 / Tested |
| 门窗传感器 D1 / Door Sensor D1 | - | ✅ 已测试 / Tested |
| 台灯 / Desk Lamp | - | ⚠️ 待测试 / Untested |
| 网关 / Gateway | - | ❌ 不支持 / Not Supported |

> 💡 **欢迎反馈！** 如果您有其他 Lipro 设备，请在 [Issues](https://github.com/Exlany/lipro-hass/issues) 中反馈，帮助我们完善支持列表。
>
> 💡 **Feedback Welcome!** If you have other Lipro devices, please report in [Issues](https://github.com/Exlany/lipro-hass/issues) to help us improve device support.

## 使用场景 / Use Cases

### 场景 1：自动化灯光 / Scenario 1: Automated Lighting

```yaml
# 日落时自动开灯 / Turn on lights at sunset
automation:
  - alias: "日落开灯"
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

### 场景 2：人体感应联动 / Scenario 2: Motion-Activated Lighting

```yaml
# 检测到人体时开灯 / Turn on light when motion detected
automation:
  - alias: "人体感应开灯"
    trigger:
      - platform: state
        entity_id: binary_sensor.hallway_motion
        to: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.hallway_light
```

### 场景 3：窗帘定时控制 / Scenario 3: Scheduled Curtain Control

```yaml
# 早上自动开窗帘 / Open curtains in the morning
automation:
  - alias: "早起开窗帘"
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

### 场景 4：浴霸预热 / Scenario 4: Bathroom Heater Preheat

```yaml
# 洗澡前预热浴霸 / Preheat bathroom heater before shower
automation:
  - alias: "浴霸预热"
    trigger:
      - platform: time
        at: "21:00:00"
    action:
      - service: climate.turn_on
        target:
          entity_id: climate.bathroom_heater
      - service: climate.set_preset_mode
        target:
          entity_id: climate.bathroom_heater
        data:
          preset_mode: "default"
```

## 高级功能 / Advanced Features

### 发送原始命令 / Send Raw Command

集成提供了 `lipro.send_command` 服务，允许高级用户发送原始命令：

The integration provides a `lipro.send_command` service for advanced users to send raw commands:

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

### 可用命令 / Available Commands

| 命令 / Command | 说明 / Description |
|---------------|-------------------|
| POWER_ON | 开启设备 / Turn on device |
| POWER_OFF | 关闭设备 / Turn off device |
| CHANGE_STATE | 修改状态 / Change state |
| CURTAIN_OPEN | 打开窗帘 / Open curtain |
| CURTAIN_CLOSE | 关闭窗帘 / Close curtain |
| CURTAIN_STOP | 停止窗帘 / Stop curtain |

## 选项 / Options

在集成选项中可以配置：

Available options in integration settings:

- **更新间隔 / Update Interval**: 设备状态轮询间隔（默认 30 秒，范围 10-300 秒）

  Device status polling interval (default 30 seconds, range 10-300 seconds)

## 已知限制 / Known Limitations

1. **仅支持云端控制 / Cloud Control Only**
   - 本集成通过 Lipro 云端 API 控制设备，不支持本地控制
   - This integration controls devices via Lipro cloud API, local control is not supported

2. **无本地发现 / No Local Discovery**
   - 设备必须先在 Lipro App 中配对，本集成无法发现新设备
   - Devices must be paired in Lipro App first, this integration cannot discover new devices

3. **网关不支持 / Gateway Not Supported**
   - 网关设备仅作为桥接器，不会创建实体
   - Gateway devices only act as bridges, no entities will be created

4. **API 限制 / API Limitations**
   - 频繁操作可能触发 API 限流
   - Frequent operations may trigger API rate limiting

5. **传感器电池 / Sensor Battery**
   - 传感器仅提供低电量警告，不提供具体电量百分比
   - Sensors only provide low battery warning, not specific battery percentage

## 故障排除 / Troubleshooting

### 认证失败 / Authentication Failed

- 确保手机号和密码正确 / Ensure phone number and password are correct
- 检查 Lipro 官方 App 是否能正常登录 / Check if Lipro official app can login normally
- 如果密码已更改，使用重新配置功能更新密码 / If password changed, use reconfigure to update

### 设备不可用 / Device Unavailable

- 检查设备是否在线 / Check if device is online
- 尝试在 Lipro App 中操作设备 / Try operating device in Lipro App
- 重新加载集成 / Reload the integration
- 检查网络连接 / Check network connection

### 状态更新延迟 / State Update Delay

- 这是云端轮询集成的正常现象 / This is normal for cloud polling integrations
- 可以在选项中减少更新间隔（最小 10 秒）/ You can reduce update interval in options (minimum 10 seconds)
- 操作后会立即进行乐观更新 / Optimistic update happens immediately after action

### 设备未显示 / Device Not Showing

- 确保设备已在 Lipro App 中配对 / Ensure device is paired in Lipro App
- 重新加载集成以同步新设备 / Reload integration to sync new devices
- 检查日志中是否有错误信息 / Check logs for error messages

### 诊断信息 / Diagnostics

如需提交问题报告，请下载诊断信息：

To submit an issue report, please download diagnostics:

1. 进入 设置 → 设备与服务 → Lipro / Go to Settings → Devices & Services → Lipro
2. 点击三个点菜单 → 下载诊断信息 / Click three-dot menu → Download diagnostics
3. 诊断信息已自动脱敏，可安全分享 / Diagnostics are automatically redacted, safe to share

## 免责声明 / Disclaimer

本集成通过逆向工程 Lipro 云端 API 实现，非官方支持。使用风险自负。

This integration is implemented by reverse engineering the Lipro cloud API and is not officially supported. Use at your own risk.

## 贡献 / Contributing

欢迎提交 Pull Request 和 Issue！

Pull Requests and Issues are welcome!

## 许可证 / License

MIT License

---

**如果这个项目对您有帮助，请给个 ⭐ Star！**

**If this project helps you, please give it a ⭐ Star!**
