# Lipro 智能家居 Home Assistant 集成

[![CI](https://github.com/Exlany/lipro-hass/actions/workflows/ci.yml/badge.svg)](https://github.com/Exlany/lipro-hass/actions/workflows/ci.yml)
[![CodeQL](https://github.com/Exlany/lipro-hass/actions/workflows/codeql.yml/badge.svg)](https://github.com/Exlany/lipro-hass/actions/workflows/codeql.yml)
[![License](https://img.shields.io/github/license/Exlany/lipro-hass?style=flat-square)](LICENSE)

[English](README.md) | 中文 | [更新日志](CHANGELOG.md)

Home Assistant 集成，用于控制 Lipro 智能家居设备。

发布信任信号：阻断式 CI + 架构/治理守卫、CodeQL、SBOM/attestation/cosign 发布链，以及清晰的安全/支持快路径。

文档快速入口：先看 `docs/README.md`，再按 canonical docs-first route 进入 `CONTRIBUTING.md`、`docs/TROUBLESHOOTING.md`、`SUPPORT.md` 与 `SECURITY.md`。

访问模式说明：当前仓库仍是 private-access。下文提到的 HACS / GitHub Releases / GitHub Issues / GitHub Discussions / GitHub Security Advisory 路径，只有在你已经具备仓库访问权限，或未来存在保持同一契约的 public mirror 时才成立。

## 从这里开始

| 角色 | 首先查看 | 用途 |
| --- | --- | --- |
| 用户 / 评估者 | `docs/README.md` | canonical docs map、双语边界，以及安装 / 排障 / 支持入口总览 |
| 贡献者 | `CONTRIBUTING.md` | 开发环境、CI 契约、PR 约定与贡献流程 |
| 架构改动贡献者 | `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md` | 允许改动的家族边界、禁止越界项、证据回写位置与定向验证建议 |
| 支持 / 缺陷反馈者 | `docs/TROUBLESHOOTING.md` → `SUPPORT.md` | diagnostics-first 排障与公开分流 |
| 安全报告者 | `SECURITY.md` | 私密披露路径与安全支持契约 |
| 维护者 | `docs/MAINTAINER_RELEASE_RUNBOOK.md` | 仅维护者使用的发版 / rehearsal / custody 附录，不属于 public first hop |

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
- `lipro.submit_anonymous_share` - 手动提交已脱敏/伪匿名的分享报告
- `lipro.get_anonymous_share_report` - 预览上传前的已脱敏/伪匿名分享载荷
- `lipro.get_developer_report` - 仅在调试模式下可用的本地诊断导出；属于部分脱敏视图，但仍保留 `iotName` 等供应商诊断标识与本地标签，方便识别正在测试的设备（全部条目或指定 entry_id）
- `lipro.submit_developer_feedback` - 仅在调试模式下可用的一键开发者诊断反馈；上传保留 `iotName`，但会脱敏设备/房间/面板/红外资产名称等用户自定义标签（全部条目或指定 entry_id）
- `lipro.query_command_result` - 仅在调试模式下可用的开发者能力：按消息序列号查询云端上报的命令状态
- `lipro.get_city` - 仅在调试模式下可用的开发者能力：按已验证的空对象 payload 契约查询云端城市元数据
- `lipro.query_user_cloud` - 仅在调试模式下可用的开发者能力：按已验证的原始空 body 契约（`-d ''`）查询用户云端元数据；实测响应可能只有顶层 `data`，没有 `code` 包装
- `lipro.fetch_body_sensor_history` - 仅在调试模式下可用的开发者能力：拉取人体传感器历史载荷用于调试
- `lipro.fetch_door_sensor_history` - 仅在调试模式下可用的开发者能力：拉取门窗传感器历史载荷用于调试
- `lipro.refresh_devices` - 强制刷新设备列表（全部条目或指定 entry_id）

固件验证清单：
- 已认证固件 trust-root 资产：`custom_components/lipro/firmware_support_manifest.json`
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

最低支持的 Home Assistant 版本：`2026.3.1`（安装元数据位于 `hacs.json`，并与 `pyproject.toml` 保持同步）。

当前访问模式真相：本仓库是 private-access。HACS 只支持公开 GitHub 仓库，因此当前仓库并不承诺今天就存在人人可达的 HACS 入口。公开 GitHub Releases、Issues、Discussions 与 Security Advisory 页面同样依赖访问模式。请把当前 checkout 中的文档文件视为唯一保证可达的 first hop。

若 `install.sh` 以 remote 模式运行且未显式指定 archive/tag，默认会解析最新的 tagged release（`latest`）。当前稳定安装说明只承诺你已经可以访问到的已校验 release 资产；如果维护者未来开放 public mirror 或 release surface，它也必须遵守这里描述的同一条 tagged-release 契约。

### HACS（仅限未来 public mirror）

HACS 必须依赖公开 GitHub 仓库。当前 private-access 仓库因此无法承诺今天就有可用的 HACS 路径。若未来 public mirror 暴露了同一组 tagged release，请改用该 mirror 的 HACS 指引，而不要假定当前仓库已经具备同等可达性。

### 脚本安装（已校验 Release 资产；需要访问权限）

```shell
# 先从你当前已经可访问的 release surface 下载以下资产。
# 请将 <release-tag> 替换为你实际下载的 tag（例如 vX.Y.Z）：
#   - install.sh
#   - lipro-hass-<release-tag>.zip
#   - SHA256SUMS
# 可选的本地签名 bundle：
#   - lipro-hass-<release-tag>.zip.sigstore.json
#   - install.sh.sigstore.json
#   - SHA256SUMS.sigstore.json

# 可选的本地校验（安装脚本内部也会用 Python/hashlib 再校验一次）
cosign verify-blob ./lipro-hass-<release-tag>.zip \
  --bundle ./lipro-hass-<release-tag>.zip.sigstore.json \
  --certificate-identity-regexp "^https://github.com/Exlany/lipro-hass/.github/workflows/release\.yml@refs/tags/<release-tag>$" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
sha256sum -c SHA256SUMS --ignore-missing

# 在你已拿到本地校验资产后，默认支持的脚本安装路径
bash ./install.sh --archive-file ./lipro-hass-<release-tag>.zip --checksum-file ./SHA256SUMS
```

说明：默认支持的脚本安装路径现在从当前访问模式下已经可得的已校验 release 资产开始。安装脚本会自行校验压缩包摘要，并在 zip 或 `SHA256SUMS` 缺失/不匹配时 fail-closed。

### 高级预览路径（不受支持）

```shell
# 显式安装开发中的 main 分支
ARCHIVE_TAG=main bash ./install.sh

# 镜像 + 预览路径（高风险：仅在你完全信任镜像域时使用）
ARCHIVE_TAG=main LIPRO_ALLOW_MIRROR=1 HUB_DOMAIN=ghfast.top bash ./install.sh
```

说明：`ARCHIVE_TAG=main`、branch fallback 与 mirror 安装只属于维护者 / 高级测试者的 preview / unsupported 路径；生产环境请优先使用经过校验的 release 资产。

### Release 资产信任边界

- 稳定安装的信任起点是经过校验的 release 资产与 `SHA256SUMS`；若未来 public mirror 提供 verified GitHub Release assets，也必须遵守同一套契约。
- 当前 release trust 证据还会发布 `SBOM`、GitHub artifact `attestation` / `provenance`（`gh attestation verify`）以及 keyless `cosign` 签名 bundle（`cosign verify-blob --bundle ...`）。
- GitHub artifact attestation / provenance 证明资产如何被构建；`cosign` 签名 bundle 证明 artifact signing。两者互补，但不能互相替代。
- Tagged release 现在会对 release-trust 栈 fail closed：blocking runtime `pip-audit`、必须存在且无 open alerts 的 tagged `CodeQL` analysis，以及签名校验，都必须在发布前通过。

### shell_command 服务

1. 先把你当前已经可访问到的 `install.sh`、`lipro-hass-<release-tag>.zip` 与 `SHA256SUMS` 下载到本地稳定目录（例如 `/config/lipro-release/`）。
2. 将以下内容添加到 `configuration.yaml`：
    ```yaml
    shell_command:
      update_lipro: >-
        bash /config/lipro-release/install.sh
        --archive-file /config/lipro-release/lipro-hass-<release-tag>.zip
        --checksum-file /config/lipro-release/SHA256SUMS
    ```
3. 重启 Home Assistant
4. 在开发者工具中调用 `service: shell_command.update_lipro`
5. 再次重启 Home Assistant

### 手动安装

1. 从你当前已经可访问的 release surface 下载 `lipro-hass-<release-tag>.zip`（例如当前 private-access 仓库，或未来的 public mirror）
2. 使用 `SHA256SUMS` 校验压缩包
3. 解压后将 `custom_components/lipro` 复制到 `config/custom_components/` 目录
4. 重启 Home Assistant

## 配置

添加集成时，需要输入您的 Lipro 账号信息：

- **手机号**：注册 Lipro 的手机号
- **密码**：Lipro 账号密码
- **记住密码**：会在本地存储密码的 MD5 哈希值，作为 hashed login 的凭证等价秘密，用于 refresh token 过期时自动重新登录。关闭可减少本地泄露面，但后续可能需要手动重新认证。

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

> 💡 **欢迎反馈！** 如果您有其他 Lipro 设备，请先走 `docs/TROUBLESHOOTING.md` → `SUPPORT.md`。若你当前的访问模式可见 GitHub issue templates（或未来 public mirror 保留该入口），再通过那条路径提交设备信息。

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
- **匿名分享错误报告**：开启后可上传已脱敏/伪匿名的错误报告（载荷仍保留稳定 installation/diagnostic 标识）
- **高级选项**：
  - **功率查询间隔**：插座功率查询频率（默认 300 秒 / 约 5 分钟，范围 30-300 秒）
  - **请求超时**：API 请求超时时间（10-60 秒）
  - **调试模式（诊断）**：采集运行诊断（mesh 拓扑 + 命令轨迹），并启用仅限调试模式的开发者服务。更详细日志请通过 Home Assistant 的日志配置开启。
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
- 若 reauth 反复失败，请先附上 diagnostics；只有当 diagnostics 仍不足以解释问题，或维护者要求进一步排查时，再补充本地专用、部分脱敏的 developer report。
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

若 diagnostics 仍不足以解释问题，或维护者要求进一步排查，可再在本地预览或上报以下载荷：
- `lipro.get_developer_report` - 仅在调试模式下可用的本地诊断导出；属于部分脱敏视图，但仍保留 `iotName` 等供应商诊断标识与本地标签，便于识别实测设备
- `lipro.submit_developer_feedback` - 仅在调试模式下可用的上传契约；保留 `iotName`，但会脱敏设备/房间/面板/红外资产名称等用户自定义标签
- 若可获取，请把 `failure_summary` / `failure_entries` 与 diagnostics 一并提供，便于维护者快速判型
- `lipro.get_anonymous_share_report` - 已脱敏/伪匿名的 share-worker 载荷预览（仍包含稳定 installation/diagnostic 标识）

另见：`SUPPORT.md`（公开问题分流）与 `SECURITY.md`（私密漏洞披露）。`docs/MAINTAINER_RELEASE_RUNBOOK.md` 仅供维护者处理发版 / rehearsal / custody 工作。

## 免责声明

本集成通过逆向工程 Lipro 云端 API 实现，非官方支持。使用风险自负。

## 支持模型

- 稳定支持目标：使用你当前访问模式下可达、且与最新 tagged release 对齐的已校验资产；若未来存在 public mirror，同一契约也可能表现为匹配该标签的 HACS 安装或已校验 GitHub Release 资产
- 预览路径（`ARCHIVE_TAG=main`、branch fallback、mirror 安装）：仅属 best effort
- 公开路由保持单一路径：`docs/README.md` → `CONTRIBUTING.md` / `docs/TROUBLESHOOTING.md` / `SUPPORT.md` / `SECURITY.md`
- maintainer continuity 与 release custody 统一留在 `docs/MAINTAINER_RELEASE_RUNBOOK.md`，不回流根 README 的 public first hop

## 贡献快速路径

- 先看 `docs/README.md`，获取 canonical docs map 与双语边界
- 再看 `CONTRIBUTING.md`，获取环境搭建、定向测试、CI 命令组与 PR 约定
- 如要修改 protocol / runtime / control / external-boundary / governance，请先读 `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md`
- 公开排障 / 分流请走 `docs/TROUBLESHOOTING.md` → `SUPPORT.md`；私密披露请走 `SECURITY.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` 仅供维护者处理发版 / rehearsal / custody 工作

## 贡献

- 缺陷报告与 Pull Request：先阅读 `CONTRIBUTING.md`；仅当当前访问模式可见时再使用 GitHub Issue / PR 模板
- 使用问题与想法讨论：先查看 `SUPPORT.md`；只有当当前访问模式可见，或未来 public mirror 保留该入口时，再使用 GitHub Discussions
- 安全问题：遵循 `SECURITY.md`；仅当当前访问模式可达时才优先使用 GitHub 私密 advisory UI
- 社区行为约定：`CODE_OF_CONDUCT.md`

## 文档入口

- `docs/README.md` - canonical docs map、公开快速路径与双语边界
- `CONTRIBUTING.md` - 贡献流程、CI 契约与评审预期
- `docs/TROUBLESHOOTING.md` - 规范排障、诊断与安全分享入口
- `SUPPORT.md` - 支持路由、分流预期与提问方式
- `SECURITY.md` - 私密漏洞披露策略
- `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md` - 面向贡献者的变更边界、证据落点与定向验证地图
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` / `docs/developer_architecture.md` - 权威架构基线与当前代码布局
- `docs/adr/README.md` - 长期架构决策与取舍记录
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` - 维护者专用的发版 / rehearsal / custody 附录
- 发版清理：GitHub 公开文档集仅保留上述入口；本地缓存、coverage、benchmark 输出与 scratch 残渣不属于 release tree
- `CODE_OF_CONDUCT.md`、`.devcontainer.json`、`custom_components/lipro/quality_scale.yaml` - 社区约定、开发环境与 quality-scale 声明
