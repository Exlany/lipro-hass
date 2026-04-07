# Phase 45: Hotspot decomposition and typed failure semantics - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning
**Source:** `v1.6` roadmap after `Phase 42 complete`

<domain>
## Phase Boundary

本 phase 只处理三类 maintainability / hotspot 尾债：

1. `rest_decoder_support.py`、`diagnostics_api_service.py`、`share_client.py`、`message_processor.py` 等热点文件仍过厚，helper / forwarding / decision density 偏高；
2. diagnostics / share / message / protocol touched-zone 仍残留 bool-fail、弱语义 fallback 或不稳定失败表达，typed result / reason code 还未完全收口；
3. benchmark 目前仍主要停留在 advisory artifact 层，baseline compare / threshold warning / no-regression gate 语义需要正式化。

本 phase 不重新定义 release/support/security continuity contract，不继续处理 `.planning/phases/**` authority pruning，也不重开 control/services boundary 解耦；这些由 `Phase 42` 与 `Phase 43` / `Phase 44` 负责。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- 热点拆分只能沿现有正式 seams 下沉：`protocol boundary`、child façade、anonymous-share focused modules、MQTT focused helpers；不得新造 root / manager hierarchy / compatibility folklore。
- public surface 不得扩张；必要重排必须隐藏在既有 import homes / façade homes 之后。
- typed failure semantics 必须是 machine-consumable 的正式合同：reason code / typed result / explicit exception family 要能被日志、diagnostics 与测试稳定消费。
- benchmark 语义需要更接近 no-regression contract，但不能靠口头约定；必须通过 workflow/docs/tests/artefact story 明确表达。
- phase 要同时收 hotspot 复杂度、失败语义与 benchmark truth，避免只做“拆文件”而不解决 contract 可验证性。

### Claude's Discretion
- 先拆 protocol / api / share / mqtt 哪一组热点，还是一 requirement 一计划；
- typed result / reason code 采用 dataclass、enum 还是 lightweight typed mapping；
- benchmark baseline / threshold / artifact manifest 是在现有 `ci.yml` advisory lane 上增强，还是引入新的 machine-readable helper。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / active truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 北极星终态与禁止项
- `AGENTS.md` — hotspot decomposition / no-new-root / residual retirement 规则
- `.planning/PROJECT.md` — 当前 `v1.6` milestone truth
- `.planning/ROADMAP.md` — `Phase 45` 正式路线与 success criteria
- `.planning/REQUIREMENTS.md` — `HOT-11 / ERR-11 / TYP-10 / QLT-15` 真源
- `.planning/STATE.md` — execution status / next-command truth
- `.planning/phases/42-delivery-trust-gates-and-validation-hardening/42-SUMMARY.md` — 当前 benchmark / release / preview truth 已完成状态
- `.planning/phases/38-external-boundary-residual-retirement-and-quality-signal-hardening/38-02-PLAN.md` — benchmark / coverage-diff quality-signal 收口先例
- `.planning/phases/29-rest-child-facade-slimming-and-test-topicization/29-03-PLAN.md` — diagnostics_api_service / child façade slim-down 先例

### Hotspot files
- `custom_components/lipro/core/protocol/boundary/rest_decoder_support.py` — protocol hotspot target
- `custom_components/lipro/core/protocol/boundary/rest_decoder.py` — boundary split target / neighbor
- `custom_components/lipro/core/api/diagnostics_api_service.py` — diagnostics API hotspot target
- `custom_components/lipro/core/anonymous_share/share_client.py` — share client hotspot target
- `custom_components/lipro/core/mqtt/message_processor.py` — MQTT message hotspot target
- `custom_components/lipro/core/coordinator/runtime/mqtt/message_handler.py` — downstream consumer / seam reference
- `custom_components/lipro/services/share.py` — share service helper / public adapter neighbor
- `.github/workflows/ci.yml` — benchmark / preview / coverage quality-signal story 当前入口

### Tests / benchmarks
- `tests/core/api/test_protocol_contract_matrix.py` — protocol / api contract regression
- `tests/core/api/test_api_diagnostics_service.py` — diagnostics API regression
- `tests/core/test_share_client.py` — share client regression
- `tests/core/mqtt/test_message_processor.py` — MQTT message processing regression
- `tests/services/test_services_share.py` — share service regression
- `tests/meta/test_governance*.py` — governance / current-truth 守卫
- `tests/benchmarks/test_command_benchmark.py` — command benchmark
- `tests/benchmarks/test_mqtt_benchmark.py` — MQTT benchmark
- `tests/benchmarks/test_device_refresh_benchmark.py` — refresh benchmark
- `tests/benchmarks/test_coordinator_performance.py` — coordinator performance benchmark

</canonical_refs>

<specifics>
## Specific Ideas

- protocol hotspot 可优先拆 `rest_decoder_support.py` 中的 normalization / mapping / fallback helpers，避免 boundary file 同时承担多类职责；
- diagnostics/share/message 三个热点都应优先把 bool-fail / weak fallback 迁到 typed result / reason code，再谈进一步 slim-down；
- benchmark truth 不能只靠“上传一个 json artifact”讲完，至少要有 baseline / threshold / no-regression 语义与文档/测试联动；
- 若某些热点已在 earlier phase partial slim-down，Phase 45 应沿其 seam 继续，而不是推翻先前 formal homes。

</specifics>

<deferred>
## Deferred Ideas

- 不在本 phase 里新增 release/security/support continuity 工作；
- 不在本 phase 里做 `.planning/phases/**` allowlist/authority pruning；
- 不把 benchmark truth 独立成新的产品线或单独里程碑；
- 不为拆热点而扩张 public surface、引入新依赖或重新定义 façade root。

</deferred>

---

*Phase: 45-hotspot-decomposition-and-typed-failure-semantics*
*Context gathered: 2026-03-20 after Phase 42 completion*
