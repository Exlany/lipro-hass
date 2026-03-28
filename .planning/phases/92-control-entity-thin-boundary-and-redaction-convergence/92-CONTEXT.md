# Phase 92: Control/entity thin-boundary and redaction convergence - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning

<domain>
## Phase Boundary

在 `Phase 91` 已收紧 protocol/runtime canonical + typed boundary 之后，`Phase 92` 只处理 control/entity 侧仍残留的高风险边界：统一 diagnostics / anonymous-share / telemetry exporter 的 redaction registry 与 detection logic，收紧 unknown secret-like fields 的默认行为，同时把四个当前仍偏厚的测试巨石继续 topicize 成 thin shell + sibling suites。

</domain>

<decisions>
## Implementation Decisions

### Redaction convergence
- **D-01:** `custom_components/lipro/core/utils/redaction.py` 是 shared cross-plane redaction truth home；若需要扩展 registry / pattern helpers / key normalization，只能向该 formal helper home inward 收敛，不再在 control/share/telemetry 家族各自发明第二套 key registry。
- **D-02:** `custom_components/lipro/control/redaction.py` 继续是 diagnostics-facing adapter home；它可以保留 `**REDACTED**` diagnostics style，但 key registry、secret-like detection 与 string-pattern family 必须来自 shared policy。
- **D-03:** `custom_components/lipro/core/anonymous_share/sanitize.py` 继续是 anonymous-share structure-preserving sanitizer home；它可以保留 `[TOKEN] / [IP] / [MAC] / [DEVICE_ID]` sink markers 与 truncation budget，但 key registry、secret-like detection 与 string-pattern family 必须来自 shared policy。
- **D-04:** `custom_components/lipro/core/telemetry/json_payloads.py` / `exporter.py` 的 blocked keys 与 reference aliases 必须复用 shared policy truth，不再长期维护第三套手写名单。
- **D-05:** unknown secret-like keys 默认 fail-closed；只要 key name 落入 shared redaction heuristics，就不能再因列表漏登记而透传。

### Thin-boundary and tests
- **D-06:** `custom_components/lipro/diagnostics.py` 继续是 thin adapter；`control/diagnostics_surface.py` / diagnostics helpers 只能消费 shared redaction contract，不得直接知道 anonymous-share 私有 sanitizer 细节。
- **D-07:** entities/platform 行为不重开 runtime ownership；`tests/platforms/test_light_entity_behavior.py` 的 topicization 只做 test topology 收敛，不改 light entity 的 public behavior。
- **D-08:** `tests/core/api/test_api_status_service.py`、`tests/core/api/test_api_command_surface_responses.py`、`tests/platforms/test_light_entity_behavior.py`、`tests/services/test_services_diagnostics.py` 必须进一步 topicize；原根文件要降成 thin shell，仅保留 re-export / import side-effect / minimal anchor。

### Verification / no-growth
- **D-09:** Phase 92 必须新增 focused guards 或更新既有 meta/governance truth，保证 shared redaction story 与 new test topology 被 CI 持续承认。
- **D-10:** 验证优先级：focused unit/integration tests -> `tests/meta` -> `scripts/check_file_matrix.py --check` -> `uv run ruff check .` -> `uv run mypy`。

### the agent's Discretion
- 自主决定 shared redaction helper 的具体 API，只要不引入第二 public surface。
- 自主决定四个 mega suite 的最小拆分粒度，但必须是 concern-local sibling files，而不是新的 mega helper。
- 自主决定是否为 telemetry/exporter 引入更严格的 alias/drop policy，只要 outward fixtures 与 developer/diagnostics views 继续稳定。

</decisions>

<specifics>
## Specific Ideas

- shared policy 应至少统一：key normalization、explicit sensitive keys、secret-like key heuristics、reference-alias map、string redaction regex family。
- diagnostics 与 anonymous share 可以保留不同 placeholder 风格，但不能再保留不同的 secret detection truth。
- 若四个 mega suites 被拆分，`FILE_MATRIX.md`、`TESTING.md` 与 focused guards 必须同步更新。

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Governance / roadmap truth
- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`

### Phase 91 inputs
- `.planning/phases/91-protocol-runtime-decomposition-and-typed-boundary-hardening/91-VERIFICATION.md`
- `.planning/phases/91-protocol-runtime-decomposition-and-typed-boundary-hardening/91-VALIDATION.md`
- `.planning/phases/91-protocol-runtime-decomposition-and-typed-boundary-hardening/91-03-SUMMARY.md`

### Production hotspots
- `custom_components/lipro/core/utils/redaction.py`
- `custom_components/lipro/control/redaction.py`
- `custom_components/lipro/control/diagnostics_surface.py`
- `custom_components/lipro/diagnostics.py`
- `custom_components/lipro/core/anonymous_share/sanitize.py`
- `custom_components/lipro/core/anonymous_share/collector.py`
- `custom_components/lipro/core/anonymous_share/report_builder.py`
- `custom_components/lipro/core/telemetry/json_payloads.py`
- `custom_components/lipro/core/telemetry/exporter.py`
- `custom_components/lipro/services/diagnostics/helpers.py`
- `custom_components/lipro/services/diagnostics/types.py`

### Tests / guards
- `tests/core/test_diagnostics_redaction.py`
- `tests/core/anonymous_share/test_sanitize.py`
- `tests/core/telemetry/test_exporter.py`
- `tests/services/test_services_diagnostics.py`
- `tests/core/api/test_api_status_service.py`
- `tests/core/api/test_api_command_surface_responses.py`
- `tests/platforms/test_light_entity_behavior.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_dependency_guards.py`
- `tests/meta/toolchain_truth_testing_governance.py`
- `.planning/codebase/TESTING.md`
- `.planning/reviews/FILE_MATRIX.md`

</canonical_refs>
