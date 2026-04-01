# Phase 119: MQTT boundary, runtime contract, and release governance hardening - Context

**Gathered:** 2026-04-01
**Status:** Ready for planning
**Source:** terminal architect review + repo-wide audit

<domain>
## Phase Boundary

本 phase 只解决当前仓内仍显著存在、且能在单一 north-star 主线内一次性收口的 architecture / governance residual：

- 斩断 `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py` 与 `custom_components/lipro/core/mqtt/*` 的循环依赖与 lazy-import folklore。
- 把 runtime/service handlers 当前仍重复声明的 coordinator/auth/command contracts 收口回 `custom_components/lipro/runtime_types.py` 单一正式真源。
- 让 `.github/workflows/release.yml` 只认 semver public release tags，并把 governance route helper / `CHANGELOG.md` / current-route docs 刷新到当前 active route truth。

本 phase 不新增业务功能，不改写 archived milestone 资产身份，不重新定义 `Coordinator` public runtime home。
</domain>

<decisions>
## Implementation Decisions

### Locked decisions
- MQTT payload size limit 与 biz-id normalization 属于 protocol-boundary family 的 shared support truth，不再由 `core/mqtt` 反向定义给 boundary 使用。
- `payload.py`、`topics.py`、`message_processor.py` 可以继续作为 MQTT transport/localized helpers，但只能单向消费 protocol-boundary family。
- `services/execution.py`、`services/command.py`、`control/entry_lifecycle_support.py` 应尽量复用 `runtime_types.py` 的 protocol/alias，而不是平行再写结构等价的 Protocol。
- `custom_components/lipro/coordinator_entry.py` 继续只承担 public runtime-home shell；本 phase 不把它删除，也不把 `core/coordinator` 讲成新的 public root。
- `release.yml` push tags 必须收窄到 semver namespace；`CHANGELOG.md` 应只讲 public release story，不再直接暴露过期 phase / archived pointer 叙事。
- governance route tests 应从 canonical contract 读取 current truth，而不是维护第二份 Python dict 真源。

### the agent's Discretion
- 共享 MQTT support 放在 `mqtt_decoder` 同层 support module 或 `mqtt_decoder.py` 本体都可以，只要满足单向依赖、命名清晰与 focused test 可验证。
- focused guard 放在现有 meta suite 还是新增 phase-local guard 文件，只要不重复造轮子即可。
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star and governance truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — north-star plane and root constraints
- `AGENTS.md` — repo-wide architectural contract and required validation slices
- `.planning/PROJECT.md` — current route contract and milestone framing
- `.planning/ROADMAP.md` — phase goal, success criteria, and active route wording
- `.planning/REQUIREMENTS.md` — requirement IDs for this phase
- `.planning/STATE.md` — active route and execution position

### MQTT boundary hotspot
- `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py` — protocol-boundary MQTT decoder authority
- `custom_components/lipro/core/mqtt/payload.py` — MQTT payload helper consuming boundary decode
- `custom_components/lipro/core/mqtt/topics.py` — topic parsing/building helper
- `custom_components/lipro/core/mqtt/message_processor.py` — message ingress processing helper
- `tests/core/mqtt/test_mqtt_payload.py` — focused payload/boundary parity proof
- `tests/core/mqtt/test_message_processor.py` — focused ingress proof

### Runtime/service contract hotspot
- `custom_components/lipro/runtime_types.py` — canonical runtime/service protocols
- `custom_components/lipro/services/execution.py` — shared authenticated coordinator execution facade
- `custom_components/lipro/services/command.py` — command service handler contracts
- `custom_components/lipro/control/entry_lifecycle_support.py` — lifecycle typing and activation state

### Release/governance freshness hotspot
- `.github/workflows/release.yml` — tagged release workflow
- `CHANGELOG.md` — public release story
- `tests/meta/governance_current_truth.py` — shared route-truth helper
- `tests/meta/test_governance_route_handoff_smoke.py` — current-route smoke checks
- `tests/meta/governance_followup_route_current_milestones.py` — current milestone continuity guards
- `tests/meta/test_governance_release_contract.py` — release workflow/changelog contract guards
- `docs/developer_architecture.md` — current developer route alignment
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` — maintainer-facing release/current-route guidance
</canonical_refs>

<specifics>
## Specific Ideas

- 把 shared MQTT support 提炼到 protocol-boundary family 后，优先让 `mqtt.payload.parse_mqtt_payload()`、`mqtt.topics.parse_topic()` 与 `MqttMessageProcessor._resolve_device_id()` 直接 import formal decode functions。
- 优先采用 `type Alias = ExistingProtocol` 或直接 import 正式 Protocol，而不是再写结构等价的局部 Protocol。
- `CHANGELOG.md` 至少需要让 `Unreleased` 明确覆盖本轮 release-namespace / governance freshness 变化，并清掉对过期 archived pointer / `Phase 10 completed` 的直接叙事。
</specifics>

<deferred>
## Deferred Ideas

- 重新裁决 `Coordinator` public home 与 `core/coordinator` internal implementation family 的长期治理 wording，如果需要更大范围 guard 重写，应留待后续 phase 单独处理。
- benchmark / preview lane 与 `scripts/lint` Phase 113 特化绑死问题，本 phase 不作为 primary scope。
</deferred>

---

*Phase: 119-mqtt-boundary-runtime-contract-and-release-governance-hardening*
*Context gathered: 2026-04-01 via terminal architect review*
