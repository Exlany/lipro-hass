# Phase 12 Research

## Research Question

在 `Phase 11` 已完成 formal mainline 收口、测试与治理真源重新对齐的前提下，如何把**当前仍真实存在**的类型契约偏差、显式 compat 残留、developer/config drift 与 contributor/open-source governance gaps 组织成一组可执行、可验证、可仲裁的 `Phase 12` plans，同时明确排除已经修复的历史问题？

## Already Fixed / Must Stay Out of Scope

- `tests/core/test_device_refresh.py` 已对齐 canonical `get_devices(offset, limit)` 路径，不再属于 active drift。
- `tests/core/ota/test_ota_candidate.py` 已对齐 `manifest_truth` contract。
- `tests/meta/test_governance_guards.py` 与 `.planning/v1.1-MILESTONE-AUDIT.md` 已不再存在真实冲突；随着 `Phase 12` 重新规划，Phase 11 审计快照现按 `superseded_snapshot` 管理。
- `custom_components/lipro/services/wiring.py` 已删除，不能再以“兼容历史测试”为名复活。
- `_ClientEndpointsMixin` aggregate export 已从 active endpoint surface 移除；它不再是 Phase 12 的 active production residual。
- `uv run pytest -q` 当前已全绿；旧审阅报告中“tests / governance 仍红”的结论已经过时。

## Remaining Accepted Problem Families

### 1. Coordinator / Runtime Public Typing Drift

- `custom_components/lipro/runtime_types.py` 里的 `LiproCoordinator` protocol 与 `Coordinator` 当前 public surface 仍不完全一致。
- `devices` 的只读/可写语义与 OTA query return contract 在 protocol、实现与 platform call sites 间仍存在裂缝。
- `entities/base.py` 与平台 setup helpers 仍残留 `Any` / `object` 宽化，导致 `uv run mypy` 失败。

### 2. REST Facade / Diagnostics Typed Return Drift

- `custom_components/lipro/core/api/client.py` 仍混用 structured rows 与 `dict[str, Any]` / `object` fallback。
- `ScheduleApiService` typed protocol 与 `LiproRestFacade` method signatures 仍未完全一致。
- `control/diagnostics_surface.py` 与 `services/diagnostics/helpers.py` 的容器/lookup typing 仍不够窄，造成 mutation 与 lookup 错误。

### 3. Remaining Explicit Compat Residuals

- `core.api.LiproClient`
- `LiproProtocolFacade.get_device_list`
- `LiproMqttFacade.raw_client`
- `DeviceCapabilities` compat alias
- `_ClientBase` 及 endpoint helper-class-level compat spine

这些残留仍是 active governance truth 的一部分，但当前策略应是**继续缩窄或删除**，而不是因为旧 narrative / 旧测试而长期合法化。

### 4. Developer / Config Truth Drift

- `docs/developer_architecture.md` 仍编码过时的文件规模叙事。
- `custom_components/lipro/quality_scale.yaml` 仍引用旧测试路径，并低估 README known limitations 数量。
- `.devcontainer.json` 仍指向 `venv/bin/python`，与仓库 `.venv` 约定不一致。

### 5. Contributor / Open-Source Governance Gaps

- `CONTRIBUTING.md` 与 `.github/pull_request_template.md` 未把 CI `security` job 纳入显式 contributor contract，或至少未清楚说明其定位。
- `.github/CODEOWNERS` 仍是单维护者配置；若项目继续保持该模型，需有更清楚的 contributor-facing 叙事。
- 顶层缺少 `CODE_OF_CONDUCT.md` / `SUPPORT.md`。
- shell 脚本静态门禁尚未进入正式 CI 故事线。

## Recommended Direction

### A. 先收类型真相，再清 residual

`uv run mypy` 仍红，说明 formal public surface 与 concrete implementation 尚未真正收口。应先让 typing 与 runtime truth 对齐，再处理 compat seam 的删除/收窄，否则 residual cleanup 会建立在脆弱 contract 上。

### B. residual cleanup 必须与治理台账同轮推进

compat seam 的物理删除或进一步缩窄，必须与 `PUBLIC_SURFACES` / `KILL_LIST` / `RESIDUAL_LEDGER` 同轮更新；否则 Phase 12 会重演“代码已变、治理未跟”的双标。

### C. docs/config 与 contributor governance 作为最后一波收口

在 code / type / residual truth 定稿后，再统一校准 developer/config artifacts 与 contributor/open-source contract，避免文档先写死过渡状态。

### D. `except Exception` 作为伴随治理，不单独立 phase bucket

宽泛异常确实仍多，但不应被抽成独立 Phase 12 主线；更合理的做法是：在 type contract、diagnostics contract 与 compat seam 收口时，顺手把已经可辨识的 broad catches 收窄。

## Suggested Plan Split

### 12-01 Coordinator / Runtime Type Contract Convergence
收口 `runtime_types.py`、`Coordinator`、平台 setup consumers 与 `entities/base.py` 的 public typing。

### 12-02 REST Facade & Diagnostics Typed Return Cleanup
收口 `core/api/client.py`、typed service protocols、`diagnostics_surface.py`、`services/diagnostics/helpers.py` 的 typed returns / containers。

### 12-03 Explicit Compat Seam Eradication & Governance Alignment
继续关闭或缩窄 active compat seams，并同步治理台账与守卫。

### 12-04 Developer / Config Truth Calibration
校准 `developer_architecture`、`quality_scale.yaml`、`.devcontainer.json` 等 active developer/config truth。

### 12-05 Contributor Contract & Open-Source Governance Hygiene
把 contributor-facing docs、community files、shell tooling stance 与实际 CI/维护模型对齐。

## Dependency Order

1. `12-01` 与 `12-02` 作为第一波：先修类型真相。
2. `12-03` 作为第二波：在类型真相稳定后收 residual seam 与 delete gates。
3. `12-04` 与 `12-05` 作为第三波：在 code truth 定稿后校准文档、配置、CI 契约与社区治理。

## Verification Strategy

- `12-01`: `uv run mypy custom_components/lipro/runtime_types.py custom_components/lipro/core/coordinator/coordinator.py custom_components/lipro/entities/base.py custom_components/lipro/light.py custom_components/lipro/cover.py custom_components/lipro/climate.py custom_components/lipro/fan.py custom_components/lipro/binary_sensor.py custom_components/lipro/sensor.py custom_components/lipro/select.py custom_components/lipro/switch.py custom_components/lipro/update.py`
- `12-02`: `uv run mypy custom_components/lipro/core/api/client.py custom_components/lipro/control/diagnostics_surface.py custom_components/lipro/services/diagnostics/helpers.py` + `uv run pytest -q tests/core/api/test_api.py tests/core/test_diagnostics.py tests/services/test_services_diagnostics.py`
- `12-03`: `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` + `uv run python scripts/check_architecture_policy.py --check` + `uv run python scripts/check_file_matrix.py --check`
- `12-04`: 文档/配置 drift 校准后，至少重跑 `uv run python scripts/check_file_matrix.py --check` 与相关 governance guards
- `12-05`: contributor/community 口径调整后，重跑 governance guards，并对新增 community files / shell tooling gate 做 smoke verification
- closeout baseline：`uv run ruff check .` + `uv run mypy` + `uv run pytest -q`

## Decision

采用“**5 plans / 3 waves**”方案：第一波收敛类型真相，第二波收残留 seam，第三波统一 developer/config truth 与 contributor/open-source governance hygiene。这样既覆盖当前仍成立的报告项，也避免把已修复的 Phase 11 问题重新合法化。
