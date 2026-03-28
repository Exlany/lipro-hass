# Phase 91: Protocol/runtime decomposition and typed boundary hardening - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning

<domain>
## Phase Boundary

在 `Phase 90` 已冻结的 formal-home / protected-thin-shell map 之上，优先收敛 protocol/runtime 侧剩余的 typed-boundary debt：继续把 `runtime_types.py`、`core/coordinator/types.py`、`core/protocol/boundary/rest_decoder_support.py`、`core/protocol/boundary/schema_registry.py`、`core/command/trace.py` 的 `Any` / dynamic payload 面缩窄成可仲裁 contract，同时只允许对 `command_runtime.py` / `mqtt_runtime.py` 做 inward split 或 typed helper 收口，不得改变 ownership，也不得让 `__init__.py`、`runtime_access.py`、`entities/base.py`、`entities/firmware_update.py` 回流 orchestration。

</domain>

<decisions>
## Implementation Decisions

### Runtime / Protocol formal-home strategy
- **D-01:** `custom_components/lipro/core/coordinator/runtime/command_runtime.py`、`custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py`、`custom_components/lipro/core/api/rest_facade.py`、`custom_components/lipro/core/api/request_policy.py` 继续是 formal homes；若需要拆分，只能 inward 到同 family 的 support helper / typed model，formal-home 文件保留 owner 身份。
- **D-02:** `custom_components/lipro/__init__.py`、`custom_components/lipro/control/runtime_access.py`、`custom_components/lipro/entities/base.py`、`custom_components/lipro/entities/firmware_update.py` 若被触碰，只允许做 typed projection / alias 收口；不得新增 orchestration、runtime/protocol internals 读取或第二条故事线。

### Typed boundary hardening
- **D-03:** protocol/runtime 共享 contract 优先复用现有 `core/api/types.py`、`core/command/result_policy.py` 与 `runtime_types.py`；避免在 coordinator / entity / diagnostics 层继续平行发明匿名 `dict[str, Any]` 语义。
- **D-04:** `core/protocol/boundary/schema_registry.py` 与 `core/protocol/boundary/result.py` 优先改为协变/erased-object registry，而不是继续把 `Any` 作为 decoder family 总线类型。
- **D-05:** `core/protocol/boundary/rest_decoder_support.py` 必须把 raw payload 处理收敛到 `object` + narrow mapping helpers；canonical payload 仍通过 boundary family 返回，不允许 raw vendor mapping 向 runtime/entity 继续穿透。
- **D-06:** `core/command/trace.py` 与 command-runtime telemetry 必须共享单一 trace contract；不要在 trace helpers、runtime telemetry、tests 之间维持多套 loosely-typed 字典故事。

### Verification / no-growth policy
- **D-07:** Phase 91 必须新增 focused no-growth guard：对上述 typed-boundary 文件的 `Any` / broad dynamic 面积做显式预算，漂移时第一时间失败。
- **D-08:** Phase 91 的验证优先 focused pytest + `uv run mypy` + `uv run ruff check .` + `uv run python scripts/check_file_matrix.py --check`；同时同步 baseline/review/docs/current-route truth，确保路线清晰推进到 Phase 92。

### the agent's Discretion
- 在不改变 ownership 的前提下，自主决定最小而彻底的 typed helper 拆分点。
- 自主选择最小充分的 focused tests / meta guards 组合。
- 自主决定是否把局部 alias 收敛到 shared type home，只要不引入第二 root 或新 public surface。

</decisions>

<specifics>
## Specific Ideas

- 以“缩小 dynamic surface + 增加 no-growth guard”为主，不做 cosmetic rename 或无收益的大搬家。
- 以 `Phase 90` freeze map 为唯一输入真源；本 phase 不重新争论 formal-home / thin-shell 身份。
- 以开源维护视角要求：type contract、governance docs、meta guards、focused tests 必须能让后续贡献者直接理解边界，不依赖口头背景。

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Governance / roadmap truth
- `AGENTS.md` — 项目级执行契约、north-star 硬约束、文档同步规则与验证命令。
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 唯一正式架构裁决源。
- `.planning/PROJECT.md` — 当前里程碑目标与 follow-up target。
- `.planning/ROADMAP.md` — `Phase 91` 目标、依赖与 success criteria。
- `.planning/REQUIREMENTS.md` — `ARC-24` / `TYP-23` requirement truth。
- `.planning/STATE.md` — 当前 phase 路由与状态真值。

### Phase 90 frozen inputs
- `.planning/phases/90-hotspot-routing-freeze-and-formal-home-decomposition-map/90-VERIFICATION.md` — five hotspots / four thin shells / delete-gate 已冻结的证据。
- `.planning/phases/90-hotspot-routing-freeze-and-formal-home-decomposition-map/90-VALIDATION.md` — Phase 90 focused gates 与 final gate。
- `docs/developer_architecture.md` — 当前 formal homes、protected thin shells 与 phase routing 叙述。

### Boundary / surface governance
- `.planning/baseline/PUBLIC_SURFACES.md` — public surface / formal-home / thin-shell truth。
- `.planning/baseline/DEPENDENCY_MATRIX.md` — dependency guard 与 runtime/control 访问规则。
- `.planning/baseline/VERIFICATION_MATRIX.md` — verification topology 与 phase closeout proof。
- `.planning/reviews/FILE_MATRIX.md` — file ownership / role 真值。
- `.planning/reviews/RESIDUAL_LEDGER.md` — residual/delete-gate truth。
- `.planning/reviews/KILL_LIST.md` — active kill target truth。

### Code + tests for this phase
- `custom_components/lipro/runtime_types.py` — outward runtime contract。
- `custom_components/lipro/core/coordinator/types.py` — coordinator local typed contract home。
- `custom_components/lipro/core/protocol/boundary/rest_decoder_support.py` — REST boundary canonicalization helper home。
- `custom_components/lipro/core/protocol/boundary/schema_registry.py` — decoder registry home。
- `custom_components/lipro/core/command/trace.py` — command trace helper home。
- `custom_components/lipro/core/coordinator/runtime/command_runtime.py` — formal command-runtime owner。
- `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py` — formal MQTT-runtime owner。
- `tests/core/api/test_protocol_contract_boundary_decoders.py` — protocol boundary decode contract。
- `tests/core/coordinator/runtime/test_runtime_telemetry_methods.py` — runtime telemetry contract。
- `tests/core/coordinator/runtime/test_command_runtime_orchestration.py` — command runtime telemetry / failure flow。
- `tests/meta/test_phase89_runtime_boundary_guards.py` — protected thin shell no-backdoor baseline。
- `tests/meta/test_phase90_hotspot_map_guards.py` — phase90 frozen map guard。

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `custom_components/lipro/core/api/types.py`：已提供 `JsonObject` / `JsonValue` / `OtaInfoRow` 等 shared payload contracts，可作为 boundary typing 真源。
- `custom_components/lipro/core/command/result_policy.py`：已提供 `TracePayload`、`CommandResultVerifyTrace` 与 command-result typed language，可复用于 `core/command/trace.py` 与 runtime telemetry。
- `custom_components/lipro/core/api/request_policy_support.py`、`custom_components/lipro/control/runtime_access_support.py`：证明当前仓库接受“formal home + support-only inward helper”模式，可作为 hotspot inward split 参考。

### Established Patterns
- formal home 不删除，只 inward split support helpers；review/baseline/docs/tests 必须同步承认 ownership 不变。
- public contract 优先通过 shared types / protocol contracts 暴露，不依赖匿名 dict 约定。
- meta guards 习惯把 phase 结果锁成 no-growth budget + docs ledger consistency 双保险。

### Integration Points
- `runtime_types.py` 连接 entities/control 与 coordinator runtime contract。
- `rest_decoder_support.py` / `schema_registry.py` 连接 protocol boundary 与 canonical payload contracts。
- `core/command/trace.py` / `command_runtime.py` / `services/telemetry_service.py` 连接 command failure language、runtime telemetry 与 diagnostics/export surfaces。

</code_context>

<deferred>
## Deferred Ideas

- `control/redaction.py` 与 `core/anonymous_share/sanitize.py` 的统一 redaction registry → `Phase 92`。
- diagnostics/share/exporters 的 redaction contract 收口与 test topicization → `Phase 92`。
- assurance topicization、microbenchmark / hotspot budget 与更广泛 quality freeze → `Phase 93`。

</deferred>

---

*Phase: 91-protocol-runtime-decomposition-and-typed-boundary-hardening*
*Context gathered: 2026-03-28*
