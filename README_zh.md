# Lipro 智能家居 Home Assistant 集成

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/Exlany/lipro-hass?style=flat-square)](https://github.com/Exlany/lipro-hass/releases)
[![License](https://img.shields.io/github/license/Exlany/lipro-hass?style=flat-square)](LICENSE)

[English](README.md) | 中文

Home Assistant 集成，用于控制 Lipro 智能家居设备。

## 功能特性

- 🔌 支持多种 Lipro 设备类型
- 🔄 云端设备自动同步
- 📡 MQTT 实时推送，状态秒级更新
- ⚡ 乐观状态更新，响应迅速
- 🎚️ 滑块防抖，避免 API 过载
- 🔁 指数退避重连，稳定可靠
- 🌐 中英文双语支持
- 🔧 诊断支持，便于故障排查

## 支持的平台和实体

| 平台 | 实体类型 | 功能 |
|------|----------|------|
| Light | 灯光 | 开关、亮度、色温 |
| Cover | 窗帘 | 开关、位置、停止 |
| Switch | 开关/插座 | 开关 |
| Fan | 风扇 | 开关、风速、模式 |
| Climate | 浴霸 | 开关、模式 |
| Binary Sensor | 传感器 | 人体感应、门窗状态、光照、电池 |

## 服务

- `lipro.send_command` - 发送原始命令到设备

## 数据更新机制

本集成使用**混合模式**获取设备状态：

- **MQTT 实时推送**：设备状态变化时立即推送
- **轮询兜底**：默认 30 秒轮询，确保状态同步
- **可配置范围**：10-300 秒
- **乐观更新**：操作后立即更新 UI，无需等待推送
- **防抖保护**：滑块操作时防止数据覆盖本地状态
- **指数退避**：MQTT 断连时自动重连，避免服务器过载

## 安装

### HACS（推荐）

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Exlany&repository=lipro-hass&category=integration)

1. 点击上方按钮，或在 HACS 中添加自定义仓库
2. 搜索 "Lipro" 并安装
3. 重启 Home Assistant
4. 添加集成：设置 → 设备与服务 → 添加集成 → Lipro

### 手动安装

1. 下载最新版本的 `lipro` 文件夹
2. 复制到 `config/custom_components/` 目录
3. 重启 Home Assistant

## 配置

添加集成时，需要输入您的 Lipro 账号信息：

- **手机号**：注册 Lipro 的手机号
- **密码**：Lipro 账号密码

### 重新配置

如需修改账号信息，可以在集成页面点击"配置"进行重新配置。

## 已测试设备

| 设备类型 | 型号 | 状态 |
|----------|------|------|
| LED 灯带 | - | ✅ 已测试 |
| 吸顶灯 | - | ✅ 已测试 |
| 风扇灯 | - | ✅ 已测试 |
| 窗帘电机 | - | ✅ 已测试 |
| 智能面板 | - | ✅ 已测试 |
| 智能插座 | - | ✅ 已测试 |
| 浴霸 | - | ✅ 已测试 |
| 人体传感器 M1 | - | ✅ 已测试 |
| 门窗传感器 D1 | - | ✅ 已测试 |
| 台灯 | - | ⚠️ 待测试 |
| 网关 | - | ❌ 不支持 |

> 💡 **欢迎反馈！** 如果您有其他 Lipro 设备，请在 [Issues](https://github.com/Exlany/lipro-hass/issues) 中反馈，帮助我们完善支持列表。

## 使用场景

### 场景 1：自动化灯光

```yaml
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

### 场景 2：人体感应联动

```yaml
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

### 场景 3：窗帘定时控制

```yaml
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

### 场景 4：浴霸预热

```yaml
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

## 高级功能

### 发送原始命令

集成提供了 `lipro.send_command` 服务，允许高级用户发送原始命令：

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

### 可用命令

| 命令 | 说明 |
|------|------|
| POWER_ON | 开启设备 |
| POWER_OFF | 关闭设备 |
| CHANGE_STATE | 修改状态 |
| CURTAIN_OPEN | 打开窗帘 |
| CURTAIN_CLOSE | 关闭窗帘 |
| CURTAIN_STOP | 停止窗帘 |

## 选项

在集成选项中可以配置：

- **更新间隔**：设备状态轮询间隔（默认 30 秒，范围 10-300 秒）

## 已知限制

1. **仅支持云端控制**
   - 本集成通过 Lipro 云端 API 控制设备，不支持本地控制

2. **无本地发现**
   - 设备必须先在 Lipro App 中配对，本集成无法发现新设备

3. **网关不支持**
   - 网关设备仅作为桥接器，不会创建实体

4. **API 限制**
   - 频繁操作可能触发 API 限流

5. **传感器电池**
   - 传感器仅提供低电量警告，不提供具体电量百分比

## 故障排除

### 认证失败

- 确保手机号和密码正确
- 检查 Lipro 官方 App 是否能正常登录
- 如果密码已更改，使用重新配置功能更新密码

### 设备不可用

- 检查设备是否在线
- 尝试在 Lipro App 中操作设备
- 重新加载集成
- 检查网络连接

### 状态更新延迟

- 这是云端轮询集成的正常现象
- 可以在选项中减少更新间隔（最小 10 秒）
- 操作后会立即进行乐观更新

### 设备未显示

- 确保设备已在 Lipro App 中配对
- 重新加载集成以同步新设备
- 检查日志中是否有错误信息

### 诊断信息

如需提交问题报告，请下载诊断信息：

1. 进入 设置 → 设备与服务 → Lipro
2. 点击三个点菜单 → 下载诊断信息
3. 诊断信息已自动脱敏，可安全分享

## 免责声明

本集成通过逆向工程 Lipro 云端 API 实现，非官方支持。使用风险自负。

## 贡献

欢迎提交 Pull Request 和 Issue！

## 许可证

MIT License

---

**如果这个项目对您有帮助，请给个 ⭐ Star！**
