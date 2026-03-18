# Integration Map
> Snapshot: `2026-03-18`
> Freshness: Phase 32 对齐刷新；仅按 `AGENTS.md`、`.planning/{ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md`、`docs/developer_architecture.md` 与当前 CI/release/public-doc truth 截面成立。上述真源变更后，本图谱必须同步刷新或标记过时。
> Derived collaboration map: 本文件是受约束的协作图谱 / 派生视图，仅用于导航、协作与局部审阅。
> Authority: 若与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 或 `docs/developer_architecture.md` 冲突，以后者为准；本图谱不得反向充当当前治理真源，且必须同步回写、标记为过时，或注明历史观察。

## Mapping Basis
- Mandatory sources consumed for this map: `AGENTS.md`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `.planning/PROJECT.md`, `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/baseline/*.md`, `.planning/reviews/*.md`, `pyproject.toml`, `.github/workflows/*`, `custom_components/lipro/manifest.json`.
- Related integration surfaces also checked: `README.md`, `README_zh.md`, `hacs.json`, `install.sh`, `custom_components/lipro/services.yaml`, `custom_components/lipro/core/**`, `custom_components/lipro/control/**`, `blueprints/automation/lipro/*.yaml`, `tests/fixtures/**`, `tests/harness/**`, `tests/meta/**`, `scripts/*.py`.

## Home Assistant Ecosystem Integration
| Surface | Paths | Integration details |
| --- | --- | --- |
| Config entry lifecycle | `custom_components/lipro/__init__.py`, `custom_components/lipro/control/entry_lifecycle_controller.py`, `custom_components/lipro/control/service_registry.py` | sets up/unloads HA entries, platforms, services, device-registry listeners, runtime infra |
| UI onboarding / options | `custom_components/lipro/config_flow.py`, `custom_components/lipro/flow/login.py`, `custom_components/lipro/flow/options_flow.py`, `custom_components/lipro/flow/schemas.py`, `custom_components/lipro/translations/*.json` | phone/password login, reauth, reconfigure, options and localized copy |
| Entity platforms | `custom_components/lipro/light.py`, `cover.py`, `switch.py`, `fan.py`, `climate.py`, `binary_sensor.py`, `sensor.py`, `select.py`, `update.py`, `custom_components/lipro/entities/*.py` | maps Lipro devices into HA platforms and firmware update entities |
| Diagnostics / health | `custom_components/lipro/diagnostics.py`, `custom_components/lipro/system_health.py`, `custom_components/lipro/control/diagnostics_surface.py`, `custom_components/lipro/control/system_health_surface.py` | HA diagnostics export and system-health reporting both consume formal control-plane surfaces |
| Services | `custom_components/lipro/services.yaml`, `custom_components/lipro/services/contracts.py`, `custom_components/lipro/services/registrations.py`, `custom_components/lipro/control/service_router.py` | public services: `send_command`, `get_schedules`, `add_schedule`, `delete_schedules`, `submit_anonymous_share`, `get_anonymous_share_report`, `refresh_devices`; developer/debug services: `get_developer_report`, `submit_developer_feedback`, `query_command_result`, `get_city`, `query_user_cloud`, `fetch_body_sensor_history`, `fetch_door_sensor_history` |
| HACS / HA metadata | `custom_components/lipro/manifest.json`, `hacs.json`, `custom_components/lipro/quality_scale.yaml`, `custom_components/lipro/icons.json`, `custom_components/lipro/icon.png` | HACS custom-integration distribution, quality-scale declaration, icon/service metadata |
| Blueprint assets | `blueprints/automation/lipro/motion_light.yaml`, `blueprints/automation/lipro/device_offline_alert.yaml`, `README*.md` | importable HA automations via `my.home-assistant.io` and manual blueprint copy flow |

## Vendor HTTP Cloud Integration
| Family | Paths | Current truth |
| --- | --- | --- |
| Base hosts | `custom_components/lipro/const/api.py` | `SMART_HOME_API_URL=https://api-hilbert.lipro.com`, `IOT_API_URL=https://api-mlink.lipro.com` |
| Auth/session | `custom_components/lipro/core/api/endpoints/auth.py`, `custom_components/lipro/core/auth/manager.py`, `custom_components/lipro/entry_auth.py`, `custom_components/lipro/config_flow.py` | vendor phone/password login, token refresh, `phone_id`, token persistence into HA config entries |
| Device catalog / product config | `custom_components/lipro/core/api/endpoints/devices.py`, `custom_components/lipro/const/api.py` | fetches device lists and product configs from vendor cloud |
| Commands / status / power | `custom_components/lipro/core/api/endpoints/commands.py`, `status.py`, `custom_components/lipro/core/api/power_service.py`, `custom_components/lipro/const/api.py` | sends commands, polls device/group/connect status, queries outlet power |
| Schedule APIs | `custom_components/lipro/core/api/endpoints/schedule.py`, `custom_components/lipro/services/schedule.py`, `custom_components/lipro/const/api.py` | weekly schedules only; mesh-group schedule read/write/delete go through BLE/gateway-member candidate strategy |
| Developer-only misc APIs | `custom_components/lipro/core/api/endpoints/misc.py`, `custom_components/lipro/services/diagnostics/helpers.py`, `custom_components/lipro/const/api.py` | `query_command_result`, `get_city`, `query_user_cloud`, body/door sensor history, OTA info |
| Transport layer | `custom_components/lipro/core/api/client.py`, `client_transport.py`, `transport_core.py`, `transport_signing.py`, `transport_retry.py`, `client_pacing.py`, `client_auth_recovery.py`, `observability.py`, `response_safety.py` | async HTTP client with signing, pacing, retry, auth recovery, telemetry hooks, and response safety |
| Boundary normalization | `custom_components/lipro/core/protocol/boundary/rest_decoder.py`, `custom_components/lipro/core/protocol/contracts.py`, `tests/fixtures/api_contracts/*.json`, `tests/fixtures/protocol_replay/rest/*.json` | high-drift REST payloads are canonicalized before runtime/control consumption |

## Vendor MQTT Integration
| Surface | Paths | Current truth |
| --- | --- | --- |
| Bootstrap config | `custom_components/lipro/core/api/mqtt_api_service.py`, `custom_components/lipro/const/api.py`, `tests/fixtures/api_contracts/get_mqtt_config.*.json` | REST `get_aliyun_mqtt_config` payload is normalized first and may arrive as direct or wrapped payload |
| Broker constants | `custom_components/lipro/const/api.py` | broker `post-cn-li93yvd5304.mqtt.aliyuncs.com:8883`, instance `post-cn-li93yvd5304`, topic prefix `Topic_Device_State` |
| Credential handling | `custom_components/lipro/core/mqtt/credentials.py` | decrypts `accessKey`/`secretKey` with AES, derives MQTT HMAC credentials |
| MQTT runtime | `custom_components/lipro/core/mqtt/mqtt_client.py`, `client_runtime.py`, `connection_manager.py`, `subscription_manager.py`, `message_processor.py`, `topics.py` | `aiomqtt` client, TLS connection, topic sync, reconnect/backoff, message decode |
| Runtime bridge | `custom_components/lipro/core/coordinator/mqtt_lifecycle.py`, `custom_components/lipro/core/coordinator/runtime/mqtt/`, `custom_components/lipro/core/coordinator/services/mqtt_service.py` | keeps MQTT as runtime service under the single coordinator/root story |
| Boundary / replay proof | `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py`, `tests/fixtures/protocol_boundary/mqtt_properties.device_state.v1.json`, `tests/fixtures/protocol_replay/mqtt/device_state.v1.replay.json`, `tests/core/mqtt/test_protocol_replay_mqtt.py` | inbound state changes are verified through canonical boundary/replay assets |

## Telemetry, Diagnostics, Share, Firmware
| Surface | Paths | Current truth |
| --- | --- | --- |
| Runtime telemetry exporter | `custom_components/lipro/core/telemetry/exporter.py`, `models.py`, `ports.py`, `sinks.py`, `custom_components/lipro/control/telemetry_surface.py` | pull-first exporter merges protocol/runtime snapshots into diagnostics, system-health, developer, and CI views |
| Redaction / support safety | `custom_components/lipro/control/redaction.py`, `custom_components/lipro/services/diagnostics/helpers.py`, `tests/integration/test_telemetry_exporter_integration.py` | blocks tokens, ids, MAC/IP, and device identifiers before support sharing |
| Developer report services | `custom_components/lipro/services/diagnostics/__init__.py`, `custom_components/lipro/services/diagnostics/helpers.py`, `custom_components/lipro/services/diagnostics/types.py` | exposes sanitized runtime diagnostics and optional capability endpoints through HA services |
| Anonymous share worker | `custom_components/lipro/core/anonymous_share/const.py`, `share_client.py`, `storage.py`, `custom_components/lipro/services/share.py`, `tests/fixtures/external_boundaries/share_worker/*.json` | outbound report submission to `https://lipro-share.lany.me/api/report` with token refresh at `/api/token/refresh` |
| Developer feedback payload | `custom_components/lipro/services/diagnostics/helpers.py`, `tests/fixtures/external_boundaries/support_payload/*.json` | support/developer feedback payloads are canonicalized and guarded by external-boundary fixtures |
| Firmware trust/advisory | `custom_components/lipro/firmware_support_manifest.json`, `custom_components/lipro/firmware_manifest.py`, `custom_components/lipro/entities/firmware_update.py`, `tests/fixtures/external_boundaries/firmware/*.json` | local manifest is trust root; remote `lipro-share.lany.me` advisory cannot independently widen `certified` |
| AI debug evidence pack | `tests/harness/evidence_pack/*.py`, `scripts/export_ai_debug_evidence_pack.py`, `tests/integration/test_ai_debug_evidence_pack.py`, `.planning/reviews/V1_1_EVIDENCE_INDEX.md` | tooling-only export that pulls telemetry/replay/governance truths into AI-safe evidence artifacts |

## Docs, Scripts, Release, And QA Integrations
| Surface | Paths | Current truth |
| --- | --- | --- |
| User/docs entrypoints | `README.md`, `README_zh.md`, `docs/README.md`, `docs/developer_architecture.md`, `docs/adr/README.md` | installation, services, blueprints, architecture, ADR and support routing |
| Contributor/security flows | `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`, `.github/pull_request_template.md`, `.github/ISSUE_TEMPLATE/*.yml`, `.github/CODEOWNERS` | contribution, disclosure, support triage and review ownership |
| Local scripts | `scripts/setup`, `scripts/develop`, `scripts/lint`, `install.sh` | reproducible dev env, local HA boot, lint wrapper, GitHub/manual installer |
| CI validation | `.github/workflows/ci.yml`, `.github/workflows/release.yml` | lint/type/governance/security/test/benchmark/validate/release; release reuses CI gates |
| External CI services | `.github/workflows/ci.yml`, `hacs.json` | Codecov upload, HACS validation, Hassfest validation, scheduled benchmark runs |
| Dependency automation | `.github/dependabot.yml` | daily updates for devcontainer image, GitHub Actions, and pip ecosystem |
| Fixture/replay authority | `tests/fixtures/api_contracts/`, `tests/fixtures/external_boundaries/`, `tests/fixtures/protocol_boundary/`, `tests/fixtures/protocol_replay/`, `tests/harness/protocol/` | external payload truth, replay manifests, and evidence inputs are explicit, versioned, and guarded |
| Meta QA guards | `tests/meta/test_external_boundary_authority.py`, `test_external_boundary_fixtures.py`, `test_firmware_support_manifest_repo_asset.py`, `test_version_sync.py`, `test_blueprints.py`, `test_install_sh_guards.py` | protects version sync, blueprint validity, installer invariants, and external-boundary authority rules |

## Explicitly Absent Integrations
- No inbound webhook receiver.
- No repo-owned DB/cache/search service.
- No non-vendor broker beyond vendor Aliyun MQTT.
- No production Prometheus/OpenTelemetry sink yet; `.planning/REQUIREMENTS.md` records them as future evaluation only.
- No second host/runtime story outside Home Assistant; `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` keeps the project HA-only.
