# Phase 19 Context

**Phase:** `19 Headless Consumer Proof & Adapter Demotion`
**Milestone:** `v1.2 Host-Neutral Core & Replay Completion` (draft)
**Date:** 2026-03-16
**Status:** Ready for planning
**Source:** roadmap draft + v1.2 milestone draft + Phase 18 verification + baseline/review truth + focused code scan

## Why Phase 19 Exists

`Phase 18` 已把 host-neutral nucleus 的关键真相抽到稳定位置：`AuthSessionSnapshot` / `AuthBootstrapSeed` / `build_protocol_auth_context()`、`LiproProtocolFacade`、`CapabilityRegistry` / `CapabilitySnapshot` / `LiproDevice`、`helpers/platform.py` adapter projection seam、以及相关 dependency/public-surface guards 都已经明确归位。当前剩下的核心问题，不再是“shared truth 有没有”，而是 **如何证明同一套 truth 能被非 Home Assistant consumer 复用，同时不长出第二条正式主链**。

最近一轮复查显示，真正仍然带有宿主装配残留的位置主要集中在 adapter wiring，而不是正式根：

1. `custom_components/lipro/config_flow.py` 仍持有一条以 `ConfigFlow` / `self.hass` / `async_get_clientsession()` 为宿主前提的登录装配路径；
2. `custom_components/lipro/entry_auth.py` 仍持有一条以 `ConfigEntry` / `entry.data` / token persistence 为前提的 setup 装配路径；
3. `custom_components/lipro/flow/credentials.py` 与 `custom_components/lipro/flow/login.py` 仍混合存在 pure helper 与 HA projection/helper 语义；
4. 各平台 `async_setup_entry()` 仍重复“读取 `entry.runtime_data` -> 过滤 devices -> `async_add_entities`”这一层 adapter 壳；
5. `custom_components/lipro/control/runtime_access.py` 仍显式假定 `ConfigEntry` registry 是 runtime locator，这只能是 HA host 内部事实，不能被误判成 shared consumer contract。

因此，`Phase 19` 的目标不是做“CLI 产品化”或“再抽一个 shared runtime”，而是做一次 **headless consumer proof**：证明 headless / CLI-style consumer 只需建立在既有 host-neutral nucleus 与 formal protocol/boundary truth 上即可完成 auth、device discovery 与 replay/evidence proof；与此同时，把剩余 HA-only assumptions 继续压回 adapter 壳，防止未来维护者误把 adapter wiring 视为可复用业务根。

## Goal

1. 建立一条最小、可验证、非 public-root 的 headless composition / boot contract，证明 headless consumer 可以复用 `AuthBootstrapSeed`、`build_protocol_auth_context()`、`LiproProtocolFacade`、device/capability truth；
2. 用同一套 nucleus 跑通 `auth -> device discovery -> replay/evidence proof`，且全程复用正式 public path / authority path，而不是复制第二套协议实现；
3. 继续 demote `config_flow.py`、`entry_auth.py`、`flow/*` 与平台 setup 中残留的 HA-only assumptions，让它们只保留 adapter / projection 身份；
4. 把 “headless proof 只是 proof consumer，不是第二 root” 回写到 phase 资产与后续治理计划中，为 `Phase 20/21/22` 留下清晰边界。

## Decisions (Locked)

- **单一正式主链不变**：`LiproProtocolFacade` 仍是唯一正式 protocol root；`Coordinator` 仍是唯一正式 runtime orchestration root。
- **proof 不是 product root**：本 phase 允许建立 headless proof harness / boot contract / assurance-style consumer，但不允许引入新的 `CLI root`、新的 package export、或新的第二合法入口叙事。
- **不抽 shared runtime**：headless consumer 只能复用 protocol/auth/device/boundary truth；不得把 `Coordinator`、`runtime_data`、entry lifecycle 或 HA runtime orchestration 抽成共享核心。
- **adapter 继续只是 adapter**：`config_flow.py`、`entry_auth.py`、`flow/login.py`、`flow/schemas.py`、`flow/options_flow.py`、平台 `async_setup_entry()` 与 `runtime_access.py` 都必须继续被裁定为 HA adapter / projection / locator，而不是 shared business root。
- **proof 必须复用正式 authority path**：auth 要复用 `AuthSessionSnapshot` 与 bootstrap helpers；device discovery 要复用 `LiproProtocolFacade`、canonical contracts、`CapabilityRegistry` / `LiproDevice`；replay/evidence 要复用既有 replay harness / evidence collector，而不是复制 vendor payload 解析链。
- **本 phase 不做 release-grade CLI**：允许出现 proof script、test harness、headless consumer fixture 或 boot helper，但不做分发级 CLI 产品、不引入新的对外 public command surface。
- **最小治理同步是强制项**：若 `Phase 19` 改动 public/dependency/verification/authority truth，执行中必须同步 `.planning/baseline/PUBLIC_SURFACES.md`、`.planning/baseline/DEPENDENCY_MATRIX.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/baseline/AUTHORITY_MATRIX.md`（条件适用）与 review docs；若本 phase 在执行后进入 completed truth，则同轮同步 `.planning/STATE.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`。这与 `Phase 22` 的全局 closeout 不冲突：`Phase 22` 负责整轮 v1.2 收尾，而不是替代本 phase 的最小 truth sync。
- **本 phase 不偷跑后续大项**：remaining boundary-family completion 属于 `Phase 20`；broad-catch / observability hardening 属于 `Phase 21`；governance/release closeout 属于 `Phase 22`。

## Non-Negotiable Constraints

- 不得出现 “HA root / CLI root” 双正式入口；
- 不得把 proof harness 放进 `custom_components/lipro/__init__.py`、`custom_components/lipro/core/__init__.py`、`custom_components/lipro/core/protocol/__init__.py` 等 public export surface；
- 不得把 `Coordinator`、`entry.runtime_data`、control locator 或 platform setup seam 误提升为 shared consumer contract；
- 不得让 `core/auth`、`core/capability`、`core/device` 新增 `homeassistant` import，或让 `helpers/platform.py` 反向定义 nucleus 真相；
- 不得让 replay/evidence proof 旁路正式 `LiproProtocolFacade` / canonical contracts / authority fixtures；
- 不得通过大规模 rename / package split / framework 抽象掩盖真正目标；Phase 19 要的是 proof + adapter demotion，不是再造架构故事。

## Specific Concerns To Address

- `custom_components/lipro/config_flow.py` 的 `_async_do_login()` / `_async_try_login()` 与 `custom_components/lipro/entry_auth.py` 的 `build_entry_auth_context()` / `_build_entry_auth_seed()` / token persistence，如何继续收敛为一套更明确的 boot contract，而不是两条 parallel wiring；
- `custom_components/lipro/flow/credentials.py`、`custom_components/lipro/flow/login.py` 中哪些 helper 是 pure input/auth helper，哪些只是 HA projection / error mapping / title shaping，是否需要继续 inward / outward demotion；
- headless proof 的最小落点应该在哪里：`tests/harness/**`、`scripts/**`、focused integration test，还是受限的 proof helper module；无论落点在哪，都不能形成 package-level root；
- headless consumer 需要复用哪些 formal collaborators 才算“证明同一套 nucleus”：至少包括 `AuthBootstrapSeed`、`build_protocol_auth_context()`、`AuthSessionSnapshot`、`LiproProtocolFacade`、device/capability truth、replay driver / evidence collector；
- 平台 `async_setup_entry()` 重复 wiring 是否应继续向 adapter helper 收薄，但又不把 platform filtering/strings 回流进 nucleus；
- 哪些 baseline wording / delete gates / future hooks 必须在规划阶段先写清，避免后续把 headless proof 演化成长期合法的第二入口。

## Deferred Ideas

- shipping-grade CLI / standalone executable / packaging surface；
- 把 `Coordinator` 抽成 headless runtime 或 second root；
- Phase 20 的 remaining boundary/replay family completion；
- Phase 21 的 broad-catch / failure classification / observability hardening；
- Phase 22 的 global roadmap/state/governance/release closeout；
- 大规模 package split、framework 化 shared SDK、monorepo multi-host productization。
