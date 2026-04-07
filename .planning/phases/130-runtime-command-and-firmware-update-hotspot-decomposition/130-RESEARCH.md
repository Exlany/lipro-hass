# Phase 130: runtime command and firmware update hotspot decomposition - Research

**Researched:** 2026-04-01
**Domain:** command runtime / firmware update hotspot inward decomposition 与 focused proof strengthening
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- `CommandRuntime` 仍是唯一正式的 command runtime orchestration home，不得再长出第二条 runtime story。
- `LiproFirmwareUpdateEntity` 仍是 entity/update outward shell，不得把 orchestration 反向拉回 entity 之外的错误位置，也不得直连 concrete coordinator internals。
- 允许继续 inward split 到邻近的 support / policy / helper seams，但不得引入新的 public surface、compat shell 或 delete folklore。
- outward behavior 保持不变，必须依靠 focused/full tests 把现状固定住。
- repo-wide terminal audit final report、governance continuity closeout、external private-fallback honesty 明确延后到 `Phase 131`，本阶段不得伪装为已完成。

### Claude's Discretion
- `command_runtime.py` 是否把 dispatch outcome / verification / telemetry bookkeeping 继续下沉到现有或新增的 localized helper。
- `firmware_update.py` 是否把 install flow / OTA refresh pipeline / background task bookkeeping 继续下沉到邻近的 support / OTA seams。
- focused tests 的增补粒度与命名，只要仍保持 suites focused、可审阅且不回长成 megatest。

### Deferred Ideas (OUT OF SCOPE)
- `Phase 131` 的 repo-wide audit closeout。
- developer / open-source docs final current story。
- external continuity / private fallback governance decisions。
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Requirement | Phase Fit |
|----|-------------|-----------|
| ARC-41 | `command_runtime.py` 与 `firmware_update.py` 继续 inward split，并保持单一正式主链与 typed contract | 核心目标 |
| HOT-60 | 冻结 runtime/entity hotspot 的下一波拆分边界与 no-regrowth 方向 | 核心目标 |
| TST-51 | 以后续 decomposition 的 focused/full proof 链守住行为不漂移 | 核心目标 |

### Requirement Interpretation
- `ARC-41` 不是“把 formal home 切碎”，而是把 multi-topic orchestration 回压到更窄的 localized support seam，同时仍让 `CommandRuntime` 与 `LiproFirmwareUpdateEntity` 保持 outward owner 身份。
- `HOT-60` 不是“寻找 delete target”；目标是让剩余热点更诚实、更可验证，不把后续继续拆分的债务重新包装成第二条故事线。
- `TST-51` 要求测试拓扑跟着 seam 走：优先扩充现有 focused suites / direct helper tests / predecessor guards，而不是再长一个 megatest。
</phase_requirements>

## Current Topology Snapshot

### Runtime Command Half
- 正式 root 在 `custom_components/lipro/core/coordinator/runtime/command_runtime.py`；上游写侧触点主要是 `command_service`、`coordinator`、`telemetry_service`。
- 当前 root 同时承担：failure snapshot / trace ring / metrics shaping、request -> trace build、dispatch result normalization、delivery verification、success finalize、API error / reauth 协调。
- 既有 inward split 已存在于 `command_runtime_support.py` 与 `command_runtime_outcome_support.py`，但 root 仍保留较多 stage-level bookkeeping。
- `CommandBuilder.build_trace()` 已偏离真实主链：生产代码实际使用 shared `build_command_trace()`；builder 目前主要只承接 refresh-skip policy。
- `RetryStrategy.should_retry()` 在生产链上无直接使用，当前更像 test-only residual；若不处理，至少需要避免继续被当作正式 orchestration contract。

### Firmware Update Half
- outward shell 在 `custom_components/lipro/entities/firmware_update.py`，且 `tests/meta/test_phase111_runtime_boundary_guards.py` 明确冻结其只能通过 runtime coordinator verbs 访问 OTA/query/command。
- 当前 entity 同时承担：install decision/execute、background task lifecycle、OTA query/cache/fingerprint、refresh result projection、entity-private state/error handling。
- 既有邻近 helper 已存在于 `firmware_update_support.py` 与 `core/ota/{candidate.py,row_selector.py,rows_cache.py,candidate_support.py,candidate_certification_support.py}`，但 entity 主文件仍保留太多 orchestration glue。
- `firmware_update.py` 仍受 `tests/meta/test_phase113_hotspot_assurance_guards.py` 的 418 行预算约束，说明本 phase 既要 inward split，也要防止无意增长。
- `_async_finalize_refresh_task` / `_async_clear_refresh_task` 命名与其同步语义不符；`_OtaCandidate` / `_InstallCommand` 私有类型跨模块泄漏；模块级 `_OTA_REFRESH_SEMAPHORE` 是跨实体的全局并发策略副作用。

## Recommended Split Strategy

### Runtime Command: inward split around stage choreography
1. **Failure ledger / telemetry seam**
   - 目标：把 summary copy、recent traces、metrics shaping、failure state mutation 尽量下沉为更窄的 helper / pure shaping。
   - 原因：这些逻辑对外只暴露 `CommandRuntime` public surface，不需要与 dispatch / verify 主链混写在一个 root 文件里。
2. **Dispatch normalization seam**
   - 目标：把 push-failure、missing-msgSn、error-type normalization 进一步收口到 support/outcome helper，让 root 只保留 stage choreography。
   - 原因：这部分是纯 dispatch result interpretation，无需持续占据 orchestration root 体积。
3. **Verification outcome seam**
   - 目标：把 `verify -> classify -> record failure` 路径进一步统一到 outcome helper，并与 success finalize 对称。
   - 原因：当前 `command_runtime.py` 仍在本地拼接 retry schedule、sender verify、result classification；适合向 `command_runtime_outcome_support.py` 再推进半步。
4. **Request / trace seam**
   - 目标：把 request -> trace build 的残留重新归一，避免 `CommandBuilder.build_trace()` 与 shared `build_command_trace()` 两套 folklore 共存。
   - 原因：命名与 formal chain 已偏移；本 phase 至少要让 root 内部 story 更单一。

### Firmware Update: inward split around entity-private orchestration
1. **Install policy seam**
   - 目标：把 `_async_prepare_install_command()` 旁的 decision / translated-error shaping 更明确地下沉到邻近 install policy helper，使 `async_install()` 保持薄壳。
   - 原因：`core/ota/candidate_support.py` 已是天然 install decision home；entity 不应长期混持 policy 判断细节。
2. **Background task lifecycle seam**
   - 目标：收窄 added/remove/schedule/finalize/clear-error hook 相关 plumbing，并修复 `_async_*` 命名失真。
   - 原因：这部分是 entity-private task bookkeeping，最适合先从主文件剥离。
3. **OTA query/cache/fingerprint seam**
   - 目标：让 cache key、fingerprint、row selection、cloud query 的组合路径更直观，减少 entity 内部多跳和参数组装噪音。
   - 原因：底层纯逻辑已经存在于 `rows_cache.py` 与 `row_selector.py`；entity 只该保留 runtime verb 边界和 state write。
4. **Refresh projection / state seam**
   - 目标：把 candidate build、projection、last_error/last_refresh state mutation 讲成一条局部单链。
   - 原因：现在 projection、error、timestamp、write-state 交织在 `_async_refresh_ota()` 中，读者需要跨多处定位。

## Naming / Residual Findings

### Runtime Half
- `custom_components/lipro/core/coordinator/runtime/command/builder.py` 的 `build_trace()` 已非生产主链；若本 phase 不删除，至少要在 runtime root / tests 中明确其 residual 身份不再代表正式 trace story。
- `custom_components/lipro/core/coordinator/runtime/command/retry.py` 的 `should_retry()` 当前更像 test-only helper；如继续保留，应避免它被错误叙述为 orchestration 主链的一部分。
- `command_runtime_support.py` / `command_runtime_outcome_support.py` 主题仍略宽，但作为现有 localized seam 已比新增第三文件更适合优先扩容。

### Firmware Half
- `custom_components/lipro/entities/firmware_update.py` 中 `_async_finalize_refresh_task()` 与 `_async_clear_refresh_task()` 命名误导，建议在不破坏 outward shell 的前提下修正或内聚。
- `custom_components/lipro/core/ota/candidate.py` 暴露的 `_OtaCandidate` / `_InstallCommand` 私有类型已被多个模块消费；本 phase 至少要让 usage 更诚实，避免继续扩大泄漏面。
- 模块级 `_OTA_REFRESH_SEMAPHORE` 让并发策略成为隐式全局；本 phase 不一定要完全消灭，但应避免进一步扩散其影响范围。
- `_has_pending_unverified_confirmation()` / `_consume_unverified_confirmation()` 未见生产链实际使用，属于优先级较高的清理候选。

## Documentation Sync Requirements
- **若 formal-home / hotspot wording 变化：** 同步 `.planning/reviews/FILE_MATRIX.md`、`.planning/reviews/RESIDUAL_LEDGER.md`、`.planning/reviews/KILL_LIST.md`。
- **若 focused proof chain 变化：** 同步 `.planning/baseline/VERIFICATION_MATRIX.md` 与 `.planning/codebase/TESTING.md`。
- **若 phase 完成态变化：** 在执行完成并验证通过后，同步 `.planning/STATE.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`。
- **不需要为了局部 helper 收口而改动的文件：** `PUBLIC_SURFACES.md` / `DEPENDENCY_MATRIX.md` / developer docs，除非 formal external story 真发生变化。

## Open Questions
1. **`CommandBuilder.build_trace()` 是直接删除、改为复用 shared trace builder，还是暂时保留但明确 residual？**
   - 现状：仅 tests 仍显式覆盖，生产主链已不再依赖。
   - 建议：优先不让它回流主链；若移除成本低，可在本 phase 完成清理，否则至少冻结 no-regrowth。
2. **`RetryStrategy.should_retry()` 是否应在本 phase 退役？**
   - 现状：生产路径只消费 `build_retry_delays()`。
   - 建议：优先聚焦 hotspots 主链；若 removal 需要大面积 test 叙事调整，可降级为明确 residual。
3. **OTA 私有类型是否本 phase 就提升为非私有命名？**
   - 现状：泄漏真实存在。
   - 建议：若命名调整牵动过广，可先控制新增扩散并记录下一步；不要为了命名洁癖打断本 phase 的 hotspot slimming。
4. **全局 `_OTA_REFRESH_SEMAPHORE` 是否必须本 phase 本地化？**
   - 现状：是隐式全局策略。
   - 建议：如果本地化不会破坏跨实体节流语义，可顺手收口；否则记录为剩余设计权衡，不强行迁移。

## Environment Availability
- 本 phase 为仓内 Python / docs / tests 收口，不依赖新外部服务。
- 统一命令约束：所有验证命令必须使用 `uv run ...`。

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest` + `pytest-asyncio` |
| Config file | `pyproject.toml` |
| Quick runtime command | `uv run pytest -q tests/core/coordinator/runtime/test_command_runtime_orchestration.py tests/core/coordinator/runtime/test_command_runtime_support.py tests/core/coordinator/runtime/test_command_runtime_outcome_support.py tests/core/coordinator/runtime/test_runtime_telemetry_methods.py tests/core/coordinator/test_runtime_polling.py tests/core/coordinator/services/test_command_service.py` |
| Quick firmware command | `uv run pytest -q tests/platforms/test_update_install_flow.py tests/platforms/test_update_background_tasks.py tests/platforms/test_update_task_callback.py tests/platforms/test_update_entity_refresh.py tests/platforms/test_update_certification_policy.py tests/platforms/test_firmware_update_entity_edges.py tests/core/ota/test_ota_candidate.py tests/core/ota/test_ota_rows_cache.py tests/core/ota/test_ota_row_selector.py tests/core/ota/test_firmware_manifest.py` |
| Guard command | `uv run pytest -q tests/meta/test_phase95_hotspot_decomposition_guards.py tests/meta/test_phase99_runtime_hotspot_support_guards.py tests/meta/test_phase111_runtime_boundary_guards.py tests/meta/test_phase113_hotspot_assurance_guards.py tests/meta/test_phase71_hotspot_route_guards.py` |

### Requirement → Proof Map
| Req ID | Behavior | Proof |
|--------|----------|-------|
| ARC-41 | runtime/entity hotspots inward split 且不长第二条 story | runtime focused suites + firmware focused suites + predecessor/meta guards |
| HOT-60 | split boundary 冻结、formal home no-regrowth | `test_phase95_*`, `test_phase99_*`, `test_phase111_*`, `test_phase113_*`, `test_phase71_*` |
| TST-51 | changed surface regressions 足够直接、可局部执行 | runtime/firmware focused tests + `uv run ruff check .` + `uv run python scripts/check_file_matrix.py --check` |

### Execution Guidance
- **先小后大**：先跑 command runtime focused suites 与 firmware focused suites，再跑 meta guards / `ruff` / `check_file_matrix`。
- **优先扩 sibling suites**：runtime 直接扩 `test_command_runtime_support.py` / `test_command_runtime_outcome_support.py`；firmware 直接扩 `test_update_background_tasks.py` / `test_update_install_flow.py` / OTA unit suites。
- **防止无效扩张**：不要新增 megatest 或重新把 unrelated protocol/control story 混到本 phase proof chain 里。

## Sources

### Primary (HIGH confidence)
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `AGENTS.md`
- `.planning/{PROJECT.md,ROADMAP.md,REQUIREMENTS.md,STATE.md}`
- `.planning/codebase/{CONCERNS.md,TESTING.md}`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/{FILE_MATRIX.md,RESIDUAL_LEDGER.md,KILL_LIST.md}`
- `custom_components/lipro/core/coordinator/runtime/{command_runtime.py,command_runtime_support.py,command_runtime_outcome_support.py}`
- `custom_components/lipro/core/coordinator/runtime/command/{builder.py,sender.py,confirmation.py,retry.py}`
- `custom_components/lipro/entities/{base.py,firmware_update.py,firmware_update_support.py}`
- `custom_components/lipro/core/ota/{candidate.py,candidate_support.py,candidate_certification_support.py,row_selector.py,rows_cache.py,query_support.py}`
- `custom_components/lipro/firmware_manifest.py`
- `tests/core/coordinator/runtime/{test_command_runtime_support.py,test_command_runtime_orchestration.py,test_command_runtime_outcome_support.py,test_runtime_telemetry_methods.py}`
- `tests/platforms/{test_update_install_flow.py,test_update_background_tasks.py,test_update_task_callback.py,test_update_entity_refresh.py,test_update_certification_policy.py,test_firmware_update_entity_edges.py}`
- `tests/core/ota/{test_ota_candidate.py,test_ota_rows_cache.py,test_ota_row_selector.py,test_firmware_manifest.py}`
- `tests/meta/{test_phase95_hotspot_decomposition_guards.py,test_phase99_runtime_hotspot_support_guards.py,test_phase111_runtime_boundary_guards.py,test_phase113_hotspot_assurance_guards.py,test_phase71_hotspot_route_guards.py}`

### Secondary (MEDIUM confidence)
- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/core/coordinator/services/{command_service.py,telemetry_service.py,protocol_service.py}`
- `custom_components/lipro/core/api/{diagnostics_api_ota.py,diagnostics_api_ota_support.py}`

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Architecture / route truth: HIGH
- Hotspot seams / residual analysis: HIGH
- Required doc sync: HIGH
- Removal candidates (`build_trace`, `should_retry`, unused confirmation helpers): MEDIUM

**Research date:** 2026-04-01
**Valid until:** 2026-04-08（active hotspot phase，建议 7 天内消费）
