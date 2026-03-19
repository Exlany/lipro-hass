# CONVENTIONS
> Snapshot: `2026-03-18`
> Freshness: Phase 32 对齐刷新；仅按 `AGENTS.md`、`.planning/{ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md`、`docs/developer_architecture.md` 与当前 CI/release/public-doc truth 截面成立。上述真源变更后，本图谱必须同步刷新或标记过时。
> Scope: `custom_components/lipro/**/*.py` 的编码规范、命名、一致性、异常语义、日志、类型与边界处理模式
> Authority order: `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` → `.planning/*.md` baseline/review truth → `docs/developer_architecture.md` → `AGENTS.md`
> Derived collaboration map: 本文件是受约束的协作图谱 / 派生视图，仅用于导航、协作与局部审阅。
> Authority: 若与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 或 `docs/developer_architecture.md` 冲突，以后者为准；本图谱不得反向充当当前治理真源，且必须同步回写、标记为过时，或注明历史观察。

## 1. Mapping Sources

本次映射综合了以下真源与实现：

- `AGENTS.md`
- `pyproject.toml`
- `.pre-commit-config.yaml`
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `README.md`
- `CONTRIBUTING.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`
- `.planning/baseline/ARCHITECTURE_POLICY.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/AUTHORITY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `custom_components/lipro/**/*.py`
- `tests/**/*.py`

## 2. Executive Snapshot

- 质量基线明确锁定为 `Python 3.14 + uv + ruff(all) + mypy(strict) + pytest`；测试目录允许单独放宽 typed constraints，但生产代码仍以 strict 为准。证据：`pyproject.toml:11`, `pyproject.toml:91`, `pyproject.toml:100`, `pyproject.toml:120`。
- 仓库约束不是“风格偏好”，而是北极星治理的一部分：显式组合、单一正式主链、边界归一化、正式 runtime/control/protocol/domain 分层。证据：`AGENTS.md:46`, `AGENTS.md:82`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md:23`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md:66`, `.planning/baseline/ARCHITECTURE_POLICY.md:18`。
- 自动扫描摘要：`245` 个生产 Python 文件中，`225` 个使用 `from __future__ import annotations`，`45` 个使用 `@dataclass`，`26` 个出现 `Protocol`，`18` 个出现 `type` 别名，`40` 个声明 `_LOGGER`；`540` 个函数中有 `63` 个以 `async_` 开头。

## 3. 命名与结构约定

### 3.1 模块/类命名是架构角色编码

- 生产代码大量使用角色后缀命名：`*Facade`、`*Runtime`、`*Service`、`*Router`、`*Registry`、`*Controller`、`*Surface`、`*Manager`。这不是装饰性命名，而是为了把协议面、运行面、控制面、服务面切清楚。证据：`custom_components/lipro/__init__.py:68`, `custom_components/lipro/services/registry.py:16`, `custom_components/lipro/control/service_router.py:138`, `custom_components/lipro/core/api/transport_executor.py:47`, `docs/developer_architecture.md:303`。
- Home Assistant 根模块保持薄适配，不允许回长成业务根。证据：`AGENTS.md:101`, `AGENTS.md:119`, `AGENTS.md:124`。
- 协程公开入口统一使用 `async_*` 命名：`async_setup_entry`、`async_unload_entry`、`async_handle_send_command`、`async_call_optional_capability` 等风格高度一致。证据：`custom_components/lipro/__init__.py:111`, `custom_components/lipro/control/service_router.py:138`, `custom_components/lipro/control/developer_router_support.py:96`。
- 领域与实体表面已转向显式 property / method 集，不再依赖动态委托；`LiproDevice` 通过显式 facade 暴露 identity/capabilities/state/extras。证据：`custom_components/lipro/core/device/device.py:36`, `custom_components/lipro/core/device/device.py:71`, `custom_components/lipro/core/device/device.py:171`, `.planning/reviews/RESIDUAL_LEDGER.md:18`, `.planning/reviews/RESIDUAL_LEDGER.md:163`。
- Entity descriptor 命名直接表达职责：`DeviceAttr`、`ScaledBrightness`、`ConditionalAttr`、`KelvinToPercent`。证据：`custom_components/lipro/entities/descriptors.py:35`, `custom_components/lipro/entities/descriptors.py:96`, `custom_components/lipro/entities/descriptors.py:122`, `custom_components/lipro/entities/descriptors.py:181`。

### 3.2 依赖方向有正式守卫，不靠约定俗成

- Entity/Platform 不得直连 `core.api` / `core.mqtt` / protocol boundary internals。证据：`AGENTS.md:67`, `.planning/baseline/ARCHITECTURE_POLICY.md:31`, `tests/meta/test_dependency_guards.py:53`。
- Control plane 不得绕开 `RuntimeAccess` 去散落读取 `entry.runtime_data` 或 coordinator internals。证据：`AGENTS.md:175`, `custom_components/lipro/control/runtime_access.py:17`, `.planning/baseline/ARCHITECTURE_POLICY.md:32`, `tests/meta/test_dependency_guards.py:57`。
- Public surface/compat residual/backdoor 都有 targeted bans，不允许“命名回流”伪装成正式设计。证据：`.planning/baseline/ARCHITECTURE_POLICY.md:48`, `.planning/baseline/ARCHITECTURE_POLICY.md:53`, `tests/meta/test_public_surface_guards.py:19`。

## 4. 类型、合同与边界处理模式

- 类型别名直接表达 runtime/config-entry 合同，避免裸 `ConfigEntry` 在 HA 根模块漂移。证据：`custom_components/lipro/__init__.py:62`。
- `@dataclass(slots=True)`、显式 field、显式 property 是当前领域模型主流，而不是“弱类型 dict 贯穿一切”。证据：`custom_components/lipro/core/device/device.py:36`, `custom_components/lipro/services/registry.py:16`。
- 描述符层用 `Generic[T] + @overload` 维持 mypy 可推断性；这是实体投影层的正式模式。证据：`custom_components/lipro/entities/descriptors.py:35`, `custom_components/lipro/entities/descriptors.py:72`, `docs/developer_architecture.md:284`。
- 协议边界优先做 canonicalization：Smart Home envelope 解包、IoT body 编码、`deviceType` 规范化、response code 归一化都停留在 protocol plane。证据：`custom_components/lipro/core/api/request_codec.py:9`, `custom_components/lipro/core/api/request_codec.py:33`, `custom_components/lipro/core/api/request_codec.py:42`, `custom_components/lipro/core/api/transport_executor.py:91`, `custom_components/lipro/core/api/transport_executor.py:117`, `custom_components/lipro/core/api/response_safety.py:83`, `AGENTS.md:85`。
- raw vendor payload 不应穿透到 runtime/domain/entity；这条规则既写在北极星，也落到 architecture policy。证据：`AGENTS.md:67`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md:45`, `.planning/baseline/ARCHITECTURE_POLICY.md:22`。

## 5. 异常语义与日志模式

- 异常体系是分层的：`LiproError` 作为根，MQTT/API 再细分到 auth/network/rate-limit 等分支，且 API error 保留原始 code。证据：`custom_components/lipro/core/exceptions.py:6`, `custom_components/lipro/core/exceptions.py:26`, `custom_components/lipro/core/api/errors.py:8`, `custom_components/lipro/core/api/errors.py:20`, `tests/core/test_exceptions.py:18`。
- 配置流异常处理遵循“已知业务错误映射、取消/中止直通、未知错误收口并脱敏记录”语义。证据：`custom_components/lipro/config_flow.py:123`, `custom_components/lipro/config_flow.py:127`, `custom_components/lipro/config_flow.py:129`, `custom_components/lipro/config_flow.py:131`, `custom_components/lipro/config_flow.py:139`。
- 开发者/诊断服务优先抛 `ServiceValidationError` + `translation_key`，避免底层异常语义直接污染 HA 服务层。证据：`custom_components/lipro/control/developer_router_support.py:43`, `custom_components/lipro/control/developer_router_support.py:64`, `custom_components/lipro/control/developer_router_support.py:78`。
- 服务日志默认记录可定位但脱敏的摘要：设备标识先脱敏，properties 只保留 summary，而非原始 payload。证据：`custom_components/lipro/control/service_router.py:93`, `custom_components/lipro/control/service_router.py:105`。
- 响应/诊断红线由正式 helper 统一执行：`response_safety.mask_sensitive_data()` 屏蔽 token/phone/device identifiers；`control.redaction.redact_property_value()` 递归处理 dict/list/JSON string，并额外处理 MAC/IP/deviceId literal。证据：`custom_components/lipro/core/api/response_safety.py:31`, `custom_components/lipro/core/api/response_safety.py:75`, `custom_components/lipro/control/redaction.py:91`, `custom_components/lipro/control/redaction.py:116`, `README.md:321`, `tests/core/test_diagnostics.py:204`。

## 6. 亮点

- **治理与代码口径对齐**：北极星规则、baseline、meta guards 与 CI 是同一套裁决链，而不是文档/代码两张皮。证据：`.planning/baseline/ARCHITECTURE_POLICY.md:9`, `tests/meta/test_dependency_guards.py:44`, `tests/meta/test_governance_guards.py:122`, `.github/workflows/ci.yml:61`。
- **显式领域表面已经成形**：`LiproDevice` 与实体描述符不再依赖动态 `__getattr__`，可读性与类型可验证性都更好。证据：`custom_components/lipro/core/device/device.py:36`, `custom_components/lipro/entities/descriptors.py:35`, `.planning/reviews/RESIDUAL_LEDGER.md:18`。
- **日志/诊断泄密风险控制较好**：控制面、API 层、README 与测试都围绕“自动脱敏”保持一致。证据：`custom_components/lipro/core/api/response_safety.py:31`, `custom_components/lipro/control/redaction.py:91`, `README.md:321`, `tests/core/test_log_safety.py:57`, `tests/core/test_diagnostics.py:204`。
- **异常语义尽量靠近用户面/调用面**：配置流和 developer services 都做了翻译/占位符/统一错误表述，而不是把低层实现细节直接透出。证据：`custom_components/lipro/config_flow.py:125`, `custom_components/lipro/control/developer_router_support.py:43`。

## 7. 缺口与风险

- **宽异常预算已被机器守卫限制在少数 sanctioned points**：`config_flow` 的 broad catch 已随登录/提交 helper 下沉而收口；当前只剩 `core/coordinator/lifecycle.py` 与 `EntryLifecycleController` 等 fail-closed / cleanup branches，并由 `tests/meta/test_phase31_runtime_budget_guards.py` 约束 no-growth。证据：`custom_components/lipro/core/coordinator/lifecycle.py:42`, `custom_components/lipro/core/coordinator/lifecycle.py:212`, `custom_components/lipro/control/entry_lifecycle_controller.py:337`, `custom_components/lipro/control/entry_lifecycle_controller.py:389`, `tests/meta/test_phase31_runtime_budget_guards.py:73`。
- **host glue 仍有跨文件跳转成本**：`__init__.py` 仍需串起 `runtime_infra`、`runtime_types` 与 `EntryLifecycleController`；比旧 multi-root 清晰得多，但对新贡献者仍有心智切换成本。证据：`custom_components/lipro/__init__.py:22`, `custom_components/lipro/__init__.py:370`, `custom_components/lipro/runtime_infra.py:73`, `custom_components/lipro/runtime_types.py:1`。
- **API collaborator 命名残留已缩窄但未归零**：`LiproRestFacade` 的正式协作者已经显式化为 `RestAuthRecoveryCoordinator` / `RestTransportExecutor` / `RestEndpointSurface`，不过 `client.py` 与 `client_pacing.py` 仍保留早期 mega-client 时代的命名余味。证据：`custom_components/lipro/core/api/client.py:37`, `custom_components/lipro/core/api/client_pacing.py:1`, `.planning/reviews/RESIDUAL_LEDGER.md:201`。
- **复杂度更多靠架构拆分与评审，而非 lint 硬拦**：Ruff 开启 `ALL`，但显式放宽了 `PLR0911/12/13/15` 等复杂度规则；`Coordinator` 文档仍被标注为热点大文件。证据：`pyproject.toml:170`, `docs/developer_architecture.md:187`。

## 8. Maintainer Checklist

- 新增模块/类时，名称必须先回答“它属于 protocol/runtime/control/domain/assurance 哪个角色”。
- 任何新 boundary/compat/helper 都必须先检查是否会破坏单一正式主链。证据：`AGENTS.md:251`, `AGENTS.md:255`。
- 新的用户面错误优先复用既有异常谱系、translation key 与脱敏日志 helper，而不是直接 `raise Exception("...")`。
- 任何对 control plane 的扩展都应优先经过 `RuntimeAccess` / `ServiceRouter` / `ServiceRegistry`，不要再散落读写 runtime internals。证据：`AGENTS.md:175`, `docs/developer_architecture.md:305`。
