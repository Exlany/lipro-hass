# Lipro 智能家居 Home Assistant 集成

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/Exlany/lipro-hass?style=flat-square)](https://github.com/Exlany/lipro-hass/releases)
[![License](https://img.shields.io/github/license/Exlany/lipro-hass?style=flat-square)](LICENSE)

[English](README.md) | 中文 | [更新日志](CHANGELOG.md)

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
- 🏗️ 现代化组合式架构设计（已于 2026-03 完成重构）

## 支持的平台和实体

| 平台 | 实体类型 | 功能 |
|------|----------|------|
| Light | 灯光 | 开关、亮度、色温 |
| Cover | 窗帘 | 开关、位置、停止 |
| Switch | 开关/插座 | 开关 |
| Fan | 风扇 | 开关、风速、模式 |
| Climate | 浴霸 | 开关、模式 |
| Binary Sensor | 传感器 | 连接状态、人体感应、门窗状态、光照、电池 |
| Sensor | 传感器 | 功率、用电量、电量、WiFi 信号 |
| Select | 选择器 | 风向、浴霸灯、色温预设 |
| Update | 固件 | 固件更新 |

## 服务

- `lipro.send_command` - 发送原始命令到设备
- `lipro.get_schedules` - 获取按周重复的定时任务；星期使用 `1=周一` 到 `7=周日`。mesh group 的读取以 BLE/gateway-member 候选为准。对已测 mesh BLE schedule，标准 `schedule/get.do` 可能返回空成功，不能假定为可靠读回退
- `lipro.add_schedule` - 添加按周重复的定时任务；当前不暴露绝对日期定时模式。mesh group 仅通过 BLE/gateway-member 候选写入，因为实测标准 `schedule/addOrUpdate.do` 不是可靠回退链路
- `lipro.delete_schedules` - 按 ID 删除定时任务；mesh group 仅通过 BLE/gateway-member 候选删除，因为实测标准 `schedule/delete.do` 可能回成功但并未删除目标任务
- `lipro.submit_anonymous_share` - 手动提交匿名分享报告
- `lipro.get_anonymous_share_report` - 预览匿名分享报告
- `lipro.get_developer_report` - 导出本地调试用脱敏报告；保留 `iotName` 等供应商诊断标识与本地标签，方便识别正在测试的设备（全部条目或指定 entry_id）
- `lipro.submit_developer_feedback` - 一键提交开发者诊断反馈；上传保留 `iotName`，但会匿名化设备/房间/面板/红外资产名称等用户自定义标签（全部条目或指定 entry_id）
- `lipro.query_command_result` - 按消息序列号查询云端上报的命令状态（开发者能力）
- `lipro.get_city` - 按已验证的空对象 payload 契约查询云端城市元数据（开发者能力）
- `lipro.query_user_cloud` - 按已验证的原始空 body 契约（`-d ''`）查询用户云端元数据；实测响应可能只有顶层 `data`，没有 `code` 包装（开发者能力）
- `lipro.fetch_body_sensor_history` - 拉取人体传感器历史载荷用于调试（开发者能力）
- `lipro.fetch_door_sensor_history` - 拉取门窗传感器历史载荷用于调试（开发者能力）
- `lipro.refresh_devices` - 强制刷新设备列表（全部条目或指定 entry_id）

固件验证清单：
- 已认证固件版本：`custom_components/lipro/firmware_support_manifest.json`
- OTA 更新实体会展示可用固件（未认证固件可能需要二次确认）

## 数据更新机制

本集成使用**混合模式**获取设备状态：

- **MQTT 实时推送**：设备状态变化时立即推送
- **MQTT Topic 形态**：订阅主题使用 `Topic_Device_State/{bizId}/{deviceId}`，其中 `bizId` 使用裸值（会先去掉持久化标识中的 `lip_` 前缀）
- **MQTT 配置载荷**：`get_mqtt_config` 可直接返回顶层 `accessKey` / `secretKey`，无需额外的 `data` 包装
- **轮询兜底**：默认 30 秒轮询，确保状态同步
- **可配置范围**：10-300 秒
- **批量查询兜底**：云端状态查询会自动分批；当批次因设备级错误（离线/未连接/无权限等）失败时，会拆分为更小批次重试，直至单设备查询
- **乐观更新**：操作后立即更新 UI，无需等待推送
- **防抖保护**：滑块操作时防止数据覆盖本地状态
- **指数退避**：MQTT 断连时自动重连，避免服务器过载

## 安装

最低支持的 Home Assistant 版本：`2026.3.1`（唯一版本真源：`pyproject.toml`）。

私有仓库 / fork 说明：CI 会跳过 HACS validation，因为 HACS 只支持公开 GitHub 仓库。

### HACS（推荐）

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Exlany&repository=lipro-hass&category=integration)

1. 点击上方按钮，或在 HACS 中添加自定义仓库
2. 搜索 "Lipro" 并安装
3. 重启 Home Assistant
4. 添加集成：设置 → 设备与服务 → 添加集成 → Lipro

### 脚本安装（通过 SSH / Terminal & SSH 插件）

```shell
wget -O - https://raw.githubusercontent.com/Exlany/lipro-hass/main/install.sh | ARCHIVE_TAG=latest bash -

# 安装指定版本（tag/branch，例如 v1.0.0）
# 提示：为获得可复现安装，建议同时把 install.sh 也固定到相同 tag。
wget -O - https://raw.githubusercontent.com/Exlany/lipro-hass/v1.0.0/install.sh | ARCHIVE_TAG=v1.0.0 bash -

# 安装开发版（请显式指定 main）
wget -O - https://raw.githubusercontent.com/Exlany/lipro-hass/main/install.sh | ARCHIVE_TAG=main bash -

# 使用镜像加速（高风险：仅在你完全信任镜像域时使用，并建议固定到 tag）
wget -O - https://raw.githubusercontent.com/Exlany/lipro-hass/main/install.sh | LIPRO_ALLOW_MIRROR=1 HUB_DOMAIN=ghfast.top ARCHIVE_TAG=v1.0.0 bash -
```

说明：`ARCHIVE_TAG` 用于指定安装版本（tag/branch）。`latest` 会解析为 GitHub Releases 的最新版本；如解析失败安装脚本会报错退出。建议固定到具体 tag（例如 `v1.0.0`）以获得可复现安装；如需开发版请显式使用 `ARCHIVE_TAG=main`。

说明：`HUB_DOMAIN` 仅影响脚本内请求 Release 信息与源码压缩包的域名，不会改变 `install.sh` 本身的下载地址（仍为 `raw.githubusercontent.com`）。

### shell_command 服务

1. 将以下内容添加到 `configuration.yaml`：
    ```yaml
    shell_command:
      update_lipro: |-
        wget -O - https://raw.githubusercontent.com/Exlany/lipro-hass/main/install.sh | ARCHIVE_TAG=latest bash -
    ```
2. 重启 Home Assistant
3. 在开发者工具中调用 `service: shell_command.update_lipro`
4. 再次重启 Home Assistant

### 手动安装

1. 从 [Releases](https://github.com/Exlany/lipro-hass/releases) 下载最新版本
2. 将 `custom_components/lipro` 文件夹复制到 `config/custom_components/` 目录
3. 重启 Home Assistant

## 配置

添加集成时，需要输入您的 Lipro 账号信息：

- **手机号**：注册 Lipro 的手机号
- **密码**：Lipro 账号密码
- **记住密码**：会在本地存储密码的 MD5 哈希值，用于 refresh token 过期时自动重新登录。关闭可减少本地泄露面，但后续可能需要手动重新认证。

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


## 官方 Blueprint

可直接导入的 Home Assistant 自动化蓝图：

- 人体感应开灯（检测到人体后开灯，无人后延时关灯）：  
  [![导入人体感应开灯 Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://github.com/Exlany/lipro-hass/blob/main/blueprints/automation/lipro/motion_light.yaml)
- 设备离线告警（实体持续离线时发送通知）：  
  [![导入设备离线告警 Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://github.com/Exlany/lipro-hass/blob/main/blueprints/automation/lipro/device_offline_alert.yaml)

手动导入：

1. 将仓库中的 `blueprints/automation/lipro/` 文件复制到 Home Assistant 的 `config/blueprints/automation/lipro/`。
2. 进入 设置 → 自动化与场景 → 蓝图，基于已导入蓝图创建自动化。

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

### 固件升级

固件升级通过 Home Assistant 的 `update` 实体提供（设置 → 设备与服务 → Lipro → 设备 → 实体）。

## 选项

在集成选项中可以配置：

- **更新间隔**：设备状态轮询间隔（默认 30 秒，范围 10-300 秒）
- **启用 MQTT 实时更新**：使用 MQTT 推送状态（推荐）
- **启用功率监测**：查询插座功率数据
- **匿名分享设备信息**：开启后可帮助完善设备支持
- **匿名分享错误报告**：开启后可帮助更快定位问题
- **高级选项**：
  - **功率查询间隔**：插座功率查询频率（默认 300 秒 / 约 5 分钟，范围 30-300 秒）
  - **请求超时**：API 请求超时时间（10-60 秒）
  - **调试模式（诊断）**：采集运行诊断（mesh 拓扑 + 命令轨迹）。更详细日志请通过 Home Assistant 的日志配置开启。
  - **关灯时调亮度/色温自动开灯**：关灯状态下调节亮度/色温也会自动开灯（如需保持 Lipro 行为可关闭）
  - **强制用云端房间覆盖 HA 区域**：始终以云端房间覆盖 HA 区域（谨慎）
  - **检查命令结果状态**：默认开启（推荐）。发送命令后基于 `msgSn` 轮询云端命令结果状态，用于辅助判断控制闭环；不等同于送达确认或设备已执行
  - **设备过滤（家庭/型号/WiFi SSID/设备 ID）**：off/include/exclude + 列表，支持逗号/分号/换行分隔，匹配大小写不敏感

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

6. **关灯时亮度滑杆提示（Tip）**
   - 默认行为可配置：开启“关灯时调亮度/色温自动开灯”后，关灯时调节亮度/色温会自动开灯
   - 如需保持 Lipro 原生行为（不自动开灯），请关闭该选项

## 故障排除

规范排障入口：`docs/TROUBLESHOOTING.md`。

### 快速检查

#### 认证失败

- 先确认手机号、密码在 Lipro 官方 App 中仍可正常使用。
- 若密码已变更，请使用重新配置/更新凭据，不要直接删除集成。
- 若 reauth 反复失败，请附上 diagnostics 与脱敏后的 developer report。
- 若可获取，请同时附上 diagnostics / system health / developer report 导出的 `failure_summary` / `failure_entries`。

#### 设备不可用 / 未显示

- 确认设备已在 Lipro App 中存在。
- 新增硬件后可重新加载集成，或执行 `lipro.refresh_devices`。
- 网关设备只承担桥接角色，不会直接创建 Home Assistant 实体。

#### 状态更新延迟 / MQTT 漂移

- MQTT 推送是 best effort，轮询仍是最终兜底。
- 如有需要，可在选项中降低轮询间隔（最小 10 秒）。
- 若状态持续漂移，请说明问题更像云端轮询、MQTT 推送，还是实体投影异常。
- 若相关路径已暴露 `failure_summary` 或聚合后的 `failure_entries`，也请一并附上。

### 诊断与安全分享

1. 进入 设置 → 设备与服务 → Lipro。
2. 点击三个点菜单 → 下载诊断信息。
3. 诊断信息已自动脱敏，可安全分享。

脱敏范围包含账号凭据/Token（`phone`, `password`, `access_token`, `refresh_token`）、云端/设备标识（`userId`/`bizId`, `serial`/`deviceId`/`iotDeviceId`）以及网络标识（WiFi SSID/MAC/IP）。

如需更深层调试，可先在本地预览或上报以下载荷：
- `lipro.get_developer_report` - 本地调试报告；保留 `iotName` 等供应商诊断标识与本地标签，便于识别实测设备
- `lipro.submit_developer_feedback` - 上传契约；保留 `iotName`，但会匿名化设备/房间/面板/红外资产名称等用户自定义标签
- 若可获取，请把 `failure_summary` / `failure_entries` 与 diagnostics 一并提供，便于维护者快速判型
- `lipro.get_anonymous_share_report` - 脱敏匿名分享报告

另见：`SUPPORT.md`（问题分流）、`SECURITY.md`（私密漏洞披露）与 `docs/MAINTAINER_RELEASE_RUNBOOK.md`（维护者发版问题）。

## 免责声明

本集成通过逆向工程 Lipro 云端 API 实现，非官方支持。使用风险自负。

## 贡献

- 缺陷报告与 Pull Request：先阅读 `CONTRIBUTING.md`，并使用 GitHub Issue / PR 模板
- 使用问题与想法讨论：先查看 `SUPPORT.md`，优先走 GitHub Discussions
- 安全问题：遵循 `SECURITY.md`，优先使用私密披露流程
- 社区行为约定：`CODE_OF_CONDUCT.md`

## 文档入口

- `docs/README.md` - 文档总索引与历史归档说明
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` - 目标架构与权威基线
- `docs/developer_architecture.md` - 当前代码布局与 runtime/control/protocol 主链说明
- `docs/TROUBLESHOOTING.md` - 规范排障与诊断入口
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` - 维护者发版 / 打包 / 标签流程
- `docs/adr/README.md` - 长期架构决策与取舍记录
- `CONTRIBUTING.md` - 贡献流程、CI 契约与评审预期
- `SUPPORT.md` - 支持路由、分流预期与提问方式
- `SECURITY.md` - 私密漏洞披露策略
- `CODE_OF_CONDUCT.md` - 社区行为约定
- `custom_components/lipro/quality_scale.yaml` - Home Assistant 质量等级映射
- `.devcontainer.json` - 可复现的开发容器配置
- `AGENTS.md` - 仓库统一执行契约
- `CLAUDE.md` - Claude Code 兼容入口，始终以 `AGENTS.md` 为准

## 许可证

MIT License

---

**如果这个项目对您有帮助，请给个 ⭐ Star！**
