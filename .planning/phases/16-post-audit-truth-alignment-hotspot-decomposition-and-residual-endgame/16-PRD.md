# Phase 16 PRD

**Date:** 2026-03-15
**Status:** Draft for planning
**Source:** 终极全仓审阅合并裁决 + 契约者指令（必须全面纳入，不遗漏）

## Objective

把终极审阅中仍然成立、且已被多轮复核确认的问题收敛为单一正式修复线：

1. 校准治理真源、工具链真相与本地 codebase map policy；
2. 拆薄 `core/api`、`core/protocol`、`core/coordinator`、`control`、`config_flow`、`firmware_update` 以及第二轮审判补出的 secondary hotspots；
3. 继续收紧类型契约、异常语义与 control/runtime formal contracts；
4. 收口 remaining residual/compat 认知债，避免旧 client/root 语义继续误导维护者；
5. 修正 domain/entity/OTA/test layering 的剩余边界问题；
6. 把 troubleshooting / contributor navigation / release runbook / local develop DX 同步到当前仓库真相；
7. 在 phase closeout 时做一次全仓 second-pass re-audit，确保不留下“未登记、无 owner、无 delete gate”的高风险尾债。

## Locked Decisions

### Governance Truth & Toolchain Alignment

- `AGENTS.md`、`PROJECT.md`、`ROADMAP.md`、`STATE.md`、baseline/review truths 必须与当前代码和已关闭 residual 完全一致；已关闭 seam 不得继续写成 active residual。
- `.planning/codebase/*` 必须先被裁决为“正式协作资产”或“本地缓存视图”；不能再处于半活跃、半忽略状态。
- Python runtime、mypy、Ruff、pre-commit、devcontainer 的版本口径必须对齐；不接受“运行时 3.14、lint 仍按 py313”这类漂移。
- `pytest` markers、benchmark policy、dev dependency audit policy、coverage gate 语义必须真实、单一、可解释。

### Hotspot Decomposition

- `LiproRestFacade`、`LiproProtocolFacade`、`Coordinator` 是 Phase 16 第一优先级热点；拆薄原则是把 strategy、normalizer、exception mapping、orchestration glue 外移，而不是平铺直叙地拆成更多壳文件。
- 第二梯队热点不只包含 `control/service_router.py`、`config_flow.py`、`entities/firmware_update.py`，还包括 `control/entry_lifecycle_controller.py`、`control/diagnostics_surface.py`、`control/telemetry_surface.py`、`core/coordinator/runtime/mqtt_runtime.py`、`core/api/request_policy.py`、`core/api/status_fallback.py`、`core/api/auth_service.py`、`core/api/mqtt_api_service.py`、`core/protocol/boundary/rest_decoder.py` 与 `core/utils/developer_report.py`。
- 拆薄动作必须保持 public surface 稳定，不允许为了减行数引入第二套 root、helper-root 或 backdoor。

### Type Contracts & Exception Semantics

- `core/api`、`core/protocol`、`control`、support/diagnostics 邻接面中的 `Any` / `type: ignore` / 反射式宽口要继续替换为 `Protocol`、typed alias、`TypedDict` 或更明确的 formal contract。
- 对关键链路中的 `except Exception`，必须裁决为：收窄到具体异常族，或保留 catch-all 但明确其日志、重试、reauth、swallow 与 observability policy。
- 不能只通过 `cast` / `getattr` / `callable` / `import_module` 掩盖 contract 漂移；需要把真实 contract 写出来。

### Residual Endgame

- `_ClientBase`、`_ClientPacingMixin`、`_ClientAuthRecoveryMixin`、`_ClientTransportMixin`、endpoint mixin family、`LiproMqttClient`、`get_auth_data()` fallback、power helper compat envelope 都属于 residual endgame 范围。
- Phase 16 不做“无 gate rename campaign”；physical rename `LiproMqttClient` 只有在 tests/runtime consumers 解绑后才可进入未来 phase。
- endpoint mixin exports 不得继续伪装成半公开 API；remaining helper spine 只能停留在 `core/api` 本地，且继续减语义。

### Control / Service / Runtime Contracts

- `send_command` 必须收口到统一 auth/error mainline，不再成为特殊写路径。
- `service_router.py`、`runtime_access.py`、`entry_lifecycle_controller.py`、`diagnostics_surface.py`、`telemetry_surface.py`、share / developer-report / maintenance / device-lookup 路径的 response schema 与 runtime contract 必须统一；动态导入与反射式能力探测继续下降。
- `service_router.py` 继续保持 public handler home 身份，但私有 glue、shape building 与 support-specific helper 继续下沉到 focused helper home。

### Domain / Entity / OTA / Test Layering

- `LiproDevice` 不能继续膨胀为第二套 public surface；正式领域真源应回到 `identity/capabilities/state/network_info/extras` 组合。
- capability 消费协议必须收敛，避免平台层长期混用 `supports_platform()` 与 `is_xxx` 双轨语义。
- `firmware_update` 需要回到 projection + action bridge 身份；manifest load、row arbitration、cache/hot-path I/O 进一步下沉。
- platform tests 必须优先验证真实 entity adapter；domain semantics 与 OTA 策略应回到对应 core test home。

### DX / Open Source Follow-Through

- 需要独立 troubleshooting / contributor navigation / maintainer release runbook truth，降低高治理仓库的 onboarding 压力。
- `scripts/develop` 不应继续粗暴删除整个 `config/custom_components`。
- 本 phase 的 DX 改进必须服务于维护体验，不扩展为与北极星无关的大规模文档工程。

### Zero-Carry-Forward Exit Bar

- Phase 16 完成时，不允许仍存在“本轮确认有风险，但没有进入计划文件列表、没有 residual owner、没有 delete gate、也没有风险说明”的尾债。
- Phase 16 结束前必须做一次 second-pass repo audit，复核高风险 hotspot、`Any` / `type: ignore` / broad-catch / dead marker / 动态入口 等指标，确认没有漏项继续漂浮在正式主链上，并把残余项写入显式 closeout 表。
- 任何确实无法在本 phase 清理的剩余项，必须被降格为低风险、局部、显式登记并写清 future preconditions；默认立场是“零 silent defer”。
- 最终 closeout 必须以“结构和契约更诚实、更小、更可验证”为准，而不是仅以“测试仍然绿色”自我宣告完成。

## Acceptance Criteria

1. 治理真源、toolchain truth 与 codebase map policy 形成单一正式裁决，并受脚本或 meta guards 保护。
2. Phase 16 的 6 个 plans 不只覆盖大方向，也显式覆盖 second-pass 发现的 secondary hotspots；不存在高风险文件游离于计划之外。
3. `core/api` / `core/protocol` / `core/coordinator` / `control` / domain / OTA 的热点拆薄都有明确的边界与 must-haves，而不是泛泛“重构一下”。
4. `Any` / `type: ignore` / `cast` / `getattr` / `import_module` / `except Exception` 的收口有真实 contract 与异常语义结果，而不是 cosmetic cleanup。
5. residual endgame 里的每项债务都被归类为：本 phase 收口、未来 phase defer、或 documented arbitration；并以 `item / disposition / owner / phase / delete gate / evidence` 形式落表，不留无主灰区。
6. 验证计划必须覆盖 ruff、mypy、governance guards、architecture policy、focused suites、second-pass debt audit 与 full suite gate。
7. contributor/open-source DX 入口、platform test layering、troubleshooting/runbook 与 release story 必须与真实维护路径一致。
8. Phase 16 计划要显式约束：不重开第二条正式主链、不引入重型新依赖、不做无 gate rename campaign、不中途接受 silent defer。

## Out of Scope

- 第二套 protocol/runtime/control 主链
- 与北极星无关的大规模换栈
- 只为 rename 而 rename 的全仓重命名
- 物理 rename `LiproMqttClient`（除非 tests/runtime consumers 已先解绑）
- 引入新的重型 observability / schema / DI 基础设施
- 没有 owner / delete gate / 风险说明的“暂时先留着”式 defer
