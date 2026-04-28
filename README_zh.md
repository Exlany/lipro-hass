# Lipro 智能家居 Home Assistant 集成

[![CI](https://github.com/Exlany/lipro-hass/actions/workflows/ci.yml/badge.svg)](https://github.com/Exlany/lipro-hass/actions/workflows/ci.yml)
[![CodeQL](https://github.com/Exlany/lipro-hass/actions/workflows/codeql.yml/badge.svg)](https://github.com/Exlany/lipro-hass/actions/workflows/codeql.yml)
[![License](https://img.shields.io/github/license/Exlany/lipro-hass?style=flat-square)](LICENSE)

[English](README.md) | 中文 | [更新日志](CHANGELOG.md)

`lipro-hass` 用于在 Home Assistant 中接入 Lipro 设备，支持灯光、窗帘、风扇、插座、传感器等常见设备，并通过 Lipro 云端完成控制与状态同步。

最低支持的 Home Assistant 版本：`2026.3.1`

## ✨ 这是什么

- 自动同步 Lipro App 中的设备
- MQTT 实时更新，轮询兜底
- 支持灯光、窗帘、开关、风扇、浴霸、传感器和固件升级
- 自带常用自动化 Blueprint
- 支持导出诊断信息，便于排障

## 🔌 支持的平台

| 平台 | 主要能力 |
| --- | --- |
| `light` | 开关、亮度、色温 |
| `cover` | 开关、停止、位置 |
| `switch` | 开关 |
| `fan` | 开关、风速、预设 |
| `climate` | 浴霸控制 |
| `binary_sensor` | 人体、门窗、连接状态、低电量 |
| `sensor` | 功率、电量、Wi-Fi 信号等 |
| `select` | 风向等预设选项 |
| `update` | 固件升级实体 |

## 🚀 安装

推荐通过 HACS 自定义仓库安装。

1. 打开 HACS。
2. 进入 `Integrations`。
3. 添加自定义仓库：
   `https://github.com/Exlany/lipro-hass`
4. 搜索 `Lipro Smart Home` 并安装。
5. 重启 Home Assistant。

一键安装（推荐，默认自动安装最新稳定版本）：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Exlany/lipro-hass/main/install.sh)
```

如果系统没有 `curl`，可用：

```bash
wget -qO- https://raw.githubusercontent.com/Exlany/lipro-hass/main/install.sh | bash
```

手动安装：

1. 从 GitHub Releases 下载最新版本压缩包。
2. 解压压缩包。
3. 将 `custom_components/lipro` 复制到 Home Assistant 的 `config/custom_components/` 目录。
4. 重启 Home Assistant。

如需固定版本，可指定 release tag：

```bash
ARCHIVE_TAG=vX.Y.Z bash <(curl -fsSL https://raw.githubusercontent.com/Exlany/lipro-hass/main/install.sh)
```

## ⚙️ 配置

重启后：

可直接点击下面按钮发起集成配置：

[![在你的 Home Assistant 中开始配置 Lipro](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=lipro)

1. 打开 `设置` -> `设备与服务`
2. 点击 `添加集成`
3. 搜索 `Lipro`
4. 输入 Lipro 账号手机号和密码

如果后续修改了密码，请优先使用集成中的“重新配置”，不要直接删除集成。

## 🧩 常见使用

### 📘 Blueprint

- 人体感应开灯：
  [![导入人体感应开灯 Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Exlany/lipro-hass/main/blueprints/automation/lipro/motion_light.yaml)
- 设备离线告警：
  [![导入设备离线告警 Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Exlany/lipro-hass/main/blueprints/automation/lipro/device_offline_alert.yaml)

手动导入路径：

- 将 `blueprints/automation/lipro/` 中的文件复制到 `config/blueprints/automation/lipro/`

### 🛠️ 常用服务

- `lipro.refresh_devices`：在 Lipro App 中新增或删除设备后刷新设备列表
- `lipro.get_schedules`：查看按周重复的定时任务
- `lipro.add_schedule`：新增按周重复的定时任务
- `lipro.delete_schedules`：按 ID 删除定时任务

## 🧪 选项

在集成选项中可以调整：

- 更新间隔
- MQTT 实时更新
- 支持插座的功率监测
- 匿名设备/错误分享
- 功率查询间隔
- 请求超时
- 调试模式
- 关灯时调亮度或色温自动开灯
- 云端房间同步到 Home Assistant 区域
- 按家庭/型号/Wi-Fi SSID/设备 ID 过滤设备

## 🩺 故障排查

先看 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)。

快速检查：

- 设备没出现：先确认设备已在 Lipro App 中，再执行 `lipro.refresh_devices`
- 登录失败：确认手机号和密码在 Lipro App 中仍可正常使用
- 状态更新慢：保持 MQTT 开启，必要时适当缩短轮询间隔

本集成导出的 Home Assistant 诊断信息默认会做脱敏，常规支持场景下可以安全分享。

## ⚠️ 已知限制

- 本集成通过 Lipro 云端 API 工作，不支持本地控制
- 设备必须先在 Lipro App 中完成配对
- 网关设备不会单独生成 Home Assistant 实体
- 高频操作可能触发云端限流
- 不同型号的能力会有差异

## 💬 反馈

- 使用问题或缺陷反馈：[SUPPORT.md](SUPPORT.md)
- 安全问题：[SECURITY.md](SECURITY.md)
- 开发文档入口：[docs/README.md](docs/README.md)

## 📄 免责声明

本项目基于对 Lipro 云端 API 的逆向分析实现，并非 Lipro 官方产品。
