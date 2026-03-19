# INTEGRATIONS
> Snapshot: `2026-03-19`
> Freshness: Phase 38 + 本次外部边界/治理终极审阅对齐刷新；仅按 `AGENTS.md`、`docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{PROJECT,STATE,ROADMAP,REQUIREMENTS}.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md`、`docs/developer_architecture.md`、`custom_components/lipro/**`、`.github/workflows/*.yml`、`tests/fixtures/**` 与 `tests/meta/*.py` 的当前截面成立。真源变更后，本图谱必须同步刷新或标记过时。
> Derived collaboration map: 本文件是受约束的协作图谱 / 派生视图，仅用于导航、审阅与集成边界核对。
> Authority: 若与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/baseline/AUTHORITY_MATRIX.md`、`.planning/phases/02.6-external-boundary-convergence/02.6-BOUNDARY-INVENTORY.md`、`.planning/reviews/*.md` 或 `docs/developer_architecture.md` 冲突，以后者为准；本图谱不得反向充当当前治理真源，且必须同步回写、标记为过时，或注明历史观察。

## APIs & External Services

**Home Assistant Ecosystem:**
- Home Assistant config-entry / diagnostics / system-health 集成面 - 用于入口装配、配置流、诊断导出与系统健康。
  - SDK/Client: `homeassistant.*` API，消费点位于 `custom_components/lipro/__init__.py`、`custom_components/lipro/config_flow.py`、`custom_components/lipro/diagnostics.py`、`custom_components/lipro/system_health.py`、`custom_components/lipro/control/*.py`。
  - Auth: 依赖 Home Assistant config entry 持久化；无独立环境变量。
- HACS / Hassfest 校验面 - 用于自定义集成分发与元数据校验。
  - SDK/Client: `hacs/action` 与 `home-assistant/actions/hassfest`，定义于 `.github/workflows/ci.yml`。
  - Auth: GitHub Actions 上下文；无运行时密钥。
- HA 质量对齐声明 - Bronze→Platinum 项在 `custom_components/lipro/quality_scale.yaml` 中显式登记。
  - SDK/Client: 质量清单本身与 `tests/meta/test_governance_guards.py`、`tests/meta/test_toolchain_truth.py` 形成守卫。
  - Auth: Not applicable.

**Vendor Cloud REST:**
- Lipro Smart Home / IoT 云接口 - 提供登录、刷新 token、设备目录、状态、控制、日程、OTA 与调试能力。
  - SDK/Client: `custom_components/lipro/core/protocol/facade.py` 的 `LiproProtocolFacade`，以及 stable import home 在 `custom_components/lipro/core/api/client.py`、组合根在 `custom_components/lipro/core/api/rest_facade.py` 的 `LiproRestFacade`；具体端点定义在 `custom_components/lipro/const/api.py` 与 `custom_components/lipro/core/api/endpoints/*.py`。
  - Auth: 用户手机号/密码经 `custom_components/lipro/config_flow.py`、`custom_components/lipro/entry_auth.py`、`custom_components/lipro/core/auth/manager.py` 登录，access/refresh token 存储在 Home Assistant config entry。
- 协议边界版本化与 authority chain - 用于吸收上游 payload 漂移。
  - SDK/Client: `custom_components/lipro/core/protocol/boundary/rest_decoder.py`，authority 指向 `tests/fixtures/api_contracts/*.json`。
  - Auth: 继承 REST 主链认证态；无额外 env var。

**Vendor MQTT:**
- Aliyun MQTT broker - 提供实时设备状态推送。
  - SDK/Client: `aiomqtt` + `custom_components/lipro/core/protocol/mqtt_facade.py` + `custom_components/lipro/core/mqtt/{transport,transport_runtime,connection_manager,subscription_manager,message_processor,topic_builder}.py`。
  - Auth: 先通过 REST `get_aliyun_mqtt_config` 获取配置，再在 `custom_components/lipro/core/mqtt/credentials.py` 中解密 `accessKey` / `secretKey` 并派生 MQTT 凭证；无环境变量。
- MQTT 边界版本化与回放验证 - 用于验证主题和消息 envelope 的 canonical contract。
  - SDK/Client: `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py`、`tests/fixtures/protocol_boundary/`、`tests/fixtures/protocol_replay/`、`tests/integration/test_protocol_replay_harness.py`。
  - Auth: 继承 MQTT transport 凭证；无独立 env var。

**Share / Support Worker:**
- `https://lipro-share.lany.me` - 提供匿名分享上报、开发者反馈 token 刷新与远端固件 advisory。
  - SDK/Client: `custom_components/lipro/core/anonymous_share/share_client.py`、`custom_components/lipro/core/anonymous_share/const.py`、`custom_components/lipro/services/share.py`、`custom_components/lipro/firmware_manifest.py`。
  - Auth: 公开 `X-API-Key` 常量定义于 `custom_components/lipro/core/anonymous_share/const.py`，并辅以内存 install token；无 repo `.env`。

**GitHub Platform:**
- GitHub Releases / Issues / Discussions / Security / Actions - 提供发布、支持与供应链证明。
  - SDK/Client: `pyproject.toml` 的 `project.urls`、`.github/ISSUE_TEMPLATE/*.yml`、`.github/pull_request_template.md`、`.github/CODEOWNERS`、`.github/workflows/{ci,release,codeql}.yml`。
  - Auth: GitHub Actions 工作流权限与 `GITHUB_TOKEN`；不进入 Home Assistant 运行时。

## Data Storage

**Databases:**
- Not detected.
  - Connection: Not applicable.
  - Client: Not applicable.

**File Storage:**
- Local filesystem only。
- Repo trust assets / metadata 位于 `custom_components/lipro/firmware_support_manifest.json`、`custom_components/lipro/services.yaml`、`custom_components/lipro/translations/*.json`、`custom_components/lipro/icons.json`、`tests/fixtures/**/*.json`。
- Home Assistant 持久化主要依赖 config entry / runtime_data，入口位于 `custom_components/lipro/entry_auth.py`、`custom_components/lipro/runtime_infra.py`。

**Caching:**
- None 外部缓存服务；仅有进程内缓存。
- 远端固件 advisory TTL 缓存在 `custom_components/lipro/firmware_manifest.py`。
- MQTT 连接/订阅状态缓存在 `custom_components/lipro/core/mqtt/transport.py`。
- 命令 pacing / 重试状态缓存在 `custom_components/lipro/core/api/request_policy.py`。
- 分享 worker token / upload 窗口缓存在 `custom_components/lipro/core/anonymous_share/share_client.py`。

## Authentication & Identity

**Auth Provider:**
- Custom vendor account auth。
  - Implementation: `custom_components/lipro/config_flow.py` → `custom_components/lipro/entry_auth.py` → `custom_components/lipro/core/auth/manager.py` → `custom_components/lipro/core/api/endpoints/auth.py` → `custom_components/lipro/core/api/rest_facade.py`。
- Vendor protocol signing / transport identity。
  - Implementation: REST 请求签名位于 `custom_components/lipro/core/api/transport_signing.py`；MQTT AES/HMAC 凭证派生位于 `custom_components/lipro/core/mqtt/credentials.py`；协议常量位于 `custom_components/lipro/const/api.py`。这些值是上游协议常量，不是部署期用户 secrets。

## Monitoring & Observability

**Error Tracking:**
- External error-tracking SaaS: None detected.
- 内建 exporter-backed telemetry 位于 `custom_components/lipro/core/telemetry/exporter.py`、`custom_components/lipro/core/telemetry/sinks.py`、`custom_components/lipro/control/telemetry_surface.py`。

**Logs:**
- Python `logging` 贯穿运行时；敏感信息遮罩位于 `custom_components/lipro/core/api/response_safety.py` 与 `custom_components/lipro/control/redaction.py`。
- Diagnostics / System Health / Developer payload 出口位于 `custom_components/lipro/diagnostics.py`、`custom_components/lipro/system_health.py`、`custom_components/lipro/services/diagnostics/helpers.py`。
- 外部边界漂移通过 `custom_components/lipro/core/protocol/boundary/*.py`、`tests/fixtures/external_boundaries/`、`tests/meta/test_external_boundary_authority.py`、`tests/meta/test_external_boundary_fixtures.py`、`tests/meta/test_firmware_support_manifest_repo_asset.py` 观察与约束。

## CI/CD & Deployment

**Hosting:**
- 运行时宿主是用户自己的 Home Assistant。
- 源码、Issue、Discussion、Release 与供应链证明宿主是 GitHub，对外入口由 `pyproject.toml` 与 `.github/*` 定义。

**CI Pipeline:**
- GitHub Actions CI 在 `.github/workflows/ci.yml`，包含 `lint`、`governance`、`security`、`test`、`benchmark`、`validate` 六类主门禁。
- 发布在 `.github/workflows/release.yml`，复用 CI 后再执行 tagged runtime `pip-audit`、tagged `CodeQL`、SBOM、GitHub artifact attestation、`cosign` 签名与 release identity manifest。
- 静态安全扫描在 `.github/workflows/codeql.yml`。
- 依赖更新自动化位于 `.github/dependabot.yml`。

## Environment Configuration

**Required env vars:**
- 正常 Home Assistant 运行：Not detected。
- 本地开发：`LIPRO_DEVELOP_CONFIG_DIR`、`LIPRO_DEVELOP_SMOKE_ONLY`，定义于 `scripts/develop`。
- 本地安全审计：`PIP_AUDIT_INCLUDE_DEV`，定义于 `scripts/lint`。
- 安装脚本：`ARCHIVE_TAG`、`ARCHIVE_FILE`、`LIPRO_ALLOW_MIRROR`、`LIPRO_ALLOW_BRANCH_FALLBACK`、`LIPRO_INSTALL_MAX_FILES`、`LIPRO_INSTALL_MAX_UNCOMPRESSED_BYTES`、`LIPRO_INSTALL_MAX_SINGLE_FILE_BYTES`，定义于 `install.sh`。

**Secrets location:**
- 用户凭证与 token 保存在 Home Assistant config entry，入口位于 `custom_components/lipro/config_flow.py` 与 `custom_components/lipro/entry_auth.py`。
- 分享 worker install token 仅保存在进程内存中，定义于 `custom_components/lipro/core/anonymous_share/share_client.py`。
- 仓库根目录未检测到 `.env` 或其他运行时 secret 文件。

## Webhooks & Callbacks

**Incoming:**
- None。
- 实时外部回流仅通过 MQTT topic 进入 `custom_components/lipro/core/mqtt/*`，不存在 HTTP webhook receiver。

**Outgoing:**
- Vendor REST 调用从 `custom_components/lipro/core/api/rest_facade.py` 发往 `custom_components/lipro/const/api.py` 中定义的 `https://api-hilbert.lipro.com` 与 `https://api-mlink.lipro.com`。
- Vendor MQTT TLS 连接从 `custom_components/lipro/core/mqtt/transport_runtime.py` 发往 `custom_components/lipro/const/api.py` 中定义的 `post-cn-li93yvd5304.mqtt.aliyuncs.com:8883`。
- 分享与支持上报从 `custom_components/lipro/core/anonymous_share/share_client.py` 发往 `https://lipro-share.lany.me/api/report` 与 `https://lipro-share.lany.me/api/token/refresh`。
- 远端固件 advisory 从 `custom_components/lipro/firmware_manifest.py` 拉取 `https://lipro-share.lany.me/api/firmware-support` 与 `https://lipro-share.lany.me/firmware_support_manifest.json`；最终 `certified` 真相仍以 `custom_components/lipro/firmware_support_manifest.json` 为准。
- GitHub release / attestation / code scanning 由 `.github/workflows/release.yml` 与 `.github/workflows/codeql.yml` 发起。

---

*Integration audit: 2026-03-19*
