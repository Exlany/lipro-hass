# External Integrations

**Analysis Date:** 2026-03-27

> Snapshot: `2026-03-27`
> Freshness: 基于 `custom_components/lipro/{manifest.json,firmware_manifest.py,firmware_support_manifest.json,const/api.py}`、`custom_components/lipro/core/{api,auth,mqtt,anonymous_share}/**`、`custom_components/lipro/{config_flow.py,entry_auth.py,diagnostics.py,system_health.py}`、`.github/workflows/{ci,release,codeql}.yml`、`.github/dependabot.yml`、`README.md`、`README_zh.md`、`SUPPORT.md`、`SECURITY.md`、`pyproject.toml`、`.planning/baseline/{AUTHORITY_MATRIX.md,DEPENDENCY_MATRIX.md}` 与 `tests/meta/{test_external_boundary_authority.py,test_external_boundary_fixtures.py,test_firmware_support_manifest_repo_asset.py,test_governance_release_contract.py,test_version_sync.py}` 的当前截面。
> Derived collaboration map: 本文件是受约束的协作图谱 / 派生视图，仅用于导航、审阅与后续实现对齐。
> Authority: 若与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{PROJECT.md,ROADMAP.md,REQUIREMENTS.md,STATE.md}`、`.planning/baseline/*.md` 或 `.planning/reviews/*.md` 冲突，以后者为准；本文件不得反向充当当前治理真源。

## APIs & External Services

**Vendor Cloud APIs:**
- Lipro Smart Home REST API - 登录、设备列表与产品配置请求由 `custom_components/lipro/const/api.py` 中的 Smart Home base URL 定义，协议入口位于 `custom_components/lipro/core/protocol/facade.py`，REST façade 位于 `custom_components/lipro/core/api/rest_facade.py`，stable import home 位于 `custom_components/lipro/core/api/client.py`。
  - SDK/Client: `custom_components/lipro/core/api/rest_facade.py`、`custom_components/lipro/core/api/endpoints/*.py`
  - Auth: 非 env 驱动；凭证来自 `custom_components/lipro/config_flow.py` 与 `custom_components/lipro/entry_auth.py` 管理的 Home Assistant config entry
- Lipro IoT REST API - 命令发送、状态查询、OTA 查询、定时任务、城市与云区域查询的 base URL 与 path 常量位于 `custom_components/lipro/const/api.py`，鉴权/续期位于 `custom_components/lipro/core/auth/manager.py` 与 `custom_components/lipro/core/api/transport_signing.py`。
  - SDK/Client: `custom_components/lipro/core/api/rest_facade.py`、`custom_components/lipro/core/api/endpoints/*.py`
  - Auth: access token / refresh token 与签名流程由 `custom_components/lipro/core/auth/manager.py` 和 `custom_components/lipro/core/api/transport_signing.py` 处理，不依赖环境变量

**Vendor Realtime Broker:**
- Aliyun MQTT broker - 主机、端口、实例标识与 keepalive 常量位于 `custom_components/lipro/const/api.py`，连接与订阅生命周期由 `custom_components/lipro/core/mqtt/{transport.py,transport_runtime.py}` 管理，上层 child façade 位于 `custom_components/lipro/core/protocol/mqtt_facade.py`。
  - SDK/Client: `custom_components/lipro/core/mqtt/transport.py`、`custom_components/lipro/core/protocol/mqtt_facade.py`
  - Auth: 凭证由 `custom_components/lipro/core/mqtt/credentials.py` 基于供应商返回的加密字段做 AES/HMAC 推导，不依赖环境变量

**Auxiliary Support Services:**
- Anonymous share worker - 上报与 token 刷新端点定义于 `custom_components/lipro/core/anonymous_share/const.py`，客户端逻辑位于 `custom_components/lipro/core/anonymous_share/{share_client.py,share_client_refresh.py,share_client_submit.py}`。
  - SDK/Client: `custom_components/lipro/core/anonymous_share/share_client.py`
  - Auth: 非 env 驱动；通过 `custom_components/lipro/core/anonymous_share/const.py` 中的公开 client API key 与运行时 install token 协作
- Remote firmware advisory - 远端 advisory URL 定义于 `custom_components/lipro/firmware_manifest.py`，本地 trust-root 资产位于 `custom_components/lipro/firmware_support_manifest.json`。
  - SDK/Client: `custom_components/lipro/firmware_manifest.py`
  - Auth: Not detected

**Repository / Distribution Surfaces:**
- GitHub repository / releases / docs / support / security - 入口定义于 `pyproject.toml`、`README.md`、`README_zh.md`、`SUPPORT.md`、`SECURITY.md`、`.github/ISSUE_TEMPLATE/*.yml` 与 `.github/pull_request_template.md`。
  - SDK/Client: `.github/workflows/{ci,release,codeql}.yml`
  - Auth: `secrets.GITHUB_TOKEN` 与 OIDC 权限仅用于 `.github/workflows/release.yml` 的发版与 attestation，不进入 Home Assistant 运行时

## Data Storage

**Databases:**
- Not detected.
  - Connection: Not applicable.
  - Client: Not applicable.

**File Storage:**
- Local filesystem only。
- 运行时静态资产位于 `custom_components/lipro/firmware_support_manifest.json`、`custom_components/lipro/services.yaml`、`custom_components/lipro/icons.json`、`custom_components/lipro/translations/*.json`。
- 外部边界与协议契约样本位于 `tests/fixtures/external_boundaries/**`、`tests/fixtures/protocol_boundary/**`、`tests/fixtures/protocol_replay/**`。

**Caching:**
- 无外部缓存服务；仅使用进程内缓存。
- 远端固件 advisory 30 分钟 TTL 缓存在 `custom_components/lipro/firmware_manifest.py`。
- MQTT 连接、订阅与重连状态缓存在 `custom_components/lipro/core/mqtt/transport.py`。
- API 请求 pacing / rate-limit / backoff 状态缓存在 `custom_components/lipro/core/api/request_policy.py`。
- 匿名分享的上传窗口、退避与 install token 刷新状态缓存在 `custom_components/lipro/core/anonymous_share/*.py`。

## Authentication & Identity

**Auth Provider:**
- Custom vendor account auth。
  - Implementation: `custom_components/lipro/config_flow.py` → `custom_components/lipro/entry_auth.py` → `custom_components/lipro/core/auth/manager.py` → `custom_components/lipro/core/api/endpoints/auth.py` → `custom_components/lipro/core/api/rest_facade.py`
- Home Assistant config entry identity 由 `custom_components/lipro/config_flow.py` 中的 `lipro_{user_id}` unique ID 约束。
- 协议签名身份由 `custom_components/lipro/const/api.py` 与 `custom_components/lipro/core/api/transport_signing.py` 提供。
- MQTT 连接身份由 `custom_components/lipro/core/mqtt/credentials.py` 基于供应商返回字段推导。

## Monitoring & Observability

**Error Tracking:**
- External error-tracking SaaS: None detected.
- 仓库级静态安全与供应链检查位于 `.github/workflows/codeql.yml`、`.github/workflows/ci.yml` 与 `.github/workflows/release.yml`。

**Logs:**
- 运行时日志基于 Python `logging`，贯穿 `custom_components/lipro/**`。
- 敏感信息脱敏位于 `custom_components/lipro/control/redaction.py` 与 `custom_components/lipro/core/api/response_safety.py`。
- Diagnostics / system-health / telemetry 出口位于 `custom_components/lipro/{diagnostics.py,system_health.py}`、`custom_components/lipro/control/telemetry_surface.py`、`custom_components/lipro/core/telemetry/{exporter.py,sinks.py}`。
- 外部边界漂移由 `tests/meta/test_external_boundary_authority.py`、`tests/meta/test_external_boundary_fixtures.py` 与 `tests/meta/test_firmware_support_manifest_repo_asset.py` 守卫。

## CI/CD & Deployment

**Hosting:**
- 生产运行时宿主是用户自己的 Home Assistant。
- 源码、release 资产、issue intake、docs 与安全策略宿主是 GitHub，入口定义在 `pyproject.toml`、`.github/**`、`README.md`、`SUPPORT.md` 与 `SECURITY.md`。
- `hacs.json` 提供 HACS 元数据，但 `README.md` 与 `README_zh.md` 明确指出 HACS 是否可用取决于仓库可见性。

**CI Pipeline:**
- `.github/workflows/ci.yml` 负责 lint/type、governance guards、runtime `pip-audit`、阻塞测试、benchmark lane 与 preview compatibility lane。
- `.github/workflows/release.yml` 复用 CI 契约后执行 tagged runtime `pip-audit`、tagged CodeQL gate、SBOM 生成、GitHub artifact attestation 与 keyless `cosign` 签名/验签。
- `.github/workflows/codeql.yml` 提供独立 CodeQL 分析。
- `.github/dependabot.yml` 每日刷新 `devcontainers`、`github-actions` 与 `pip` 生态。

## Environment Configuration

**Required env vars:**
- 本地开发：`LIPRO_DEVELOP_CONFIG_DIR`、`LIPRO_DEVELOP_SMOKE_ONLY`，定义于 `scripts/develop`。
- 本地安全审计：`PIP_AUDIT_INCLUDE_DEV`，定义于 `scripts/lint`。
- 安装脚本：`ARCHIVE_TAG`、`ARCHIVE_FILE`、`LIPRO_ALLOW_MIRROR`、`LIPRO_ALLOW_BRANCH_FALLBACK`、`LIPRO_INSTALL_MAX_FILES`、`LIPRO_INSTALL_MAX_UNCOMPRESSED_BYTES`、`LIPRO_INSTALL_MAX_SINGLE_FILE_BYTES`，定义于 `install.sh`。
- Release workflow：`GITHUB_TOKEN` / `GH_TOKEN` 由 `.github/workflows/release.yml` 从 `secrets.GITHUB_TOKEN` 注入。

**Secrets location:**
- 用户账号、access token、refresh token 与 `phone_id` 由 `custom_components/lipro/config_flow.py` 与 `custom_components/lipro/entry_auth.py` 写入 Home Assistant config entry。
- GitHub 发版凭证仅存在于 `.github/workflows/release.yml` 的运行时环境。
- 仓库中未检测到 `.env*` 文件。

## Webhooks & Callbacks

**Incoming:**
- None。
- 实时入站消息只通过 MQTT topic 进入 `custom_components/lipro/core/mqtt/transport_runtime.py`，并在 `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py` 中完成规范化。

**Outgoing:**
- Vendor REST 调用发往 `custom_components/lipro/const/api.py` 中定义的 Smart Home 与 IoT base URLs。
- Vendor MQTT 连接发往 `custom_components/lipro/const/api.py` 中定义的 Aliyun broker。
- 匿名分享上报与 token 刷新发往 `custom_components/lipro/core/anonymous_share/const.py` 中定义的 worker 端点。
- 远端固件 advisory 从 `custom_components/lipro/firmware_manifest.py` 拉取；最终 `certified` 真相仍以 `custom_components/lipro/firmware_support_manifest.json` 为准。
- Release-time SBOM、attestation 与 cosign 验签通过 `.github/workflows/release.yml` 访问 GitHub API 与 Sigstore 工具链。

## Risks & Recommendations

**Vendor Protocol Drift:**
- 风险：供应商 base URL、签名常量、merchant code、MQTT instance 与 AES 相关材料集中在 `custom_components/lipro/const/api.py`，上游协议一旦变化会同时影响登录、控制与推送。
- 建议：继续把 `tests/fixtures/protocol_replay/**`、`tests/meta/test_external_boundary_authority.py` 与相关协议回放测试作为 vendor contract 变更的首道门禁。

**Auxiliary Host Concentration:**
- 风险：匿名分享与远端固件 advisory 同时依赖 `lipro-share.lany.me`，对应实现位于 `custom_components/lipro/core/anonymous_share/const.py` 与 `custom_components/lipro/firmware_manifest.py`，该域名故障会同时影响诊断上报与固件提示。
- 建议：保持 `custom_components/lipro/diagnostics.py` 与 `custom_components/lipro/system_health.py` 的失败暴露能力，并为该域名维护显式可用性观察与 ownership 说明。

**Trust-Root Freshness:**
- 风险：固件 `certified` 真相来自本地 `custom_components/lipro/firmware_support_manifest.json`，远端只作 advisory；若本地资产过旧，功能虽不会越权，但更新提示可能滞后。
- 建议：把 `tests/meta/test_firmware_support_manifest_repo_asset.py` 视为 release gate，并在发布前同步审视 `custom_components/lipro/firmware_manifest.py` 的远端 advisory 行为是否仍符合当前预期。

**Distribution UX:**
- 风险：`custom_components/lipro/manifest.json` 当前将 `issue_tracker` 指向文档而非 Issues，且 `README.md` 明确说明 HACS 可达性依赖仓库可见性；若入口叙事不同步，用户会在 HA / GitHub / 文档之间迷路。
- 建议：若未来开放稳定的 public issue/support surface，务必同步更新 `custom_components/lipro/manifest.json`、`README*`、`SUPPORT.md` 与 `.github/ISSUE_TEMPLATE/config.yml`。

**Preview Installer Surface:**
- 风险：`install.sh` 允许 `ARCHIVE_TAG=main`、branch fallback 与 mirror 安装，这些路径对维护者调试有价值，但不具备稳定供应链保证。
- 建议：继续将 `.github/workflows/release.yml` 产出的校验资产视为唯一稳定分发链路，不要把 preview 路径写成默认生产建议。

---

*Integration audit: 2026-03-27*
