# Phase 19 Research

**Phase:** `19 Headless Consumer Proof & Adapter Demotion`
**Source inputs:** `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, baseline/review assets, `Phase 18` artifacts, focused code scan, parallel explorer research
**Date:** 2026-03-16

## Inputs

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/research/v1.2-SUMMARY.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/ARCHITECTURE_POLICY.md`
- `.planning/phases/18-host-neutral-boundary-nucleus-extraction/18-CONTEXT.md`
- `.planning/phases/18-host-neutral-boundary-nucleus-extraction/18-RESEARCH.md`
- `.planning/phases/18-host-neutral-boundary-nucleus-extraction/18-VERIFICATION.md`
- `custom_components/lipro/config_flow.py`
- `custom_components/lipro/entry_auth.py`
- `custom_components/lipro/flow/credentials.py`
- `custom_components/lipro/flow/login.py`
- `custom_components/lipro/flow/schemas.py`
- `custom_components/lipro/flow/options_flow.py`
- `custom_components/lipro/helpers/platform.py`
- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/core/__init__.py`
- `custom_components/lipro/core/auth/bootstrap.py`
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/capability/registry.py`
- `custom_components/lipro/core/device/device.py`
- `tests/harness/protocol/replay_driver.py`
- `scripts/export_ai_debug_evidence_pack.py`
- `tests/flows/test_config_flow.py`
- `tests/core/test_init.py`
- `tests/core/test_token_persistence.py`
- `tests/meta/test_dependency_guards.py`
- `tests/meta/test_public_surface_guards.py`

## Key Findings

### 1. `Phase 18` 已把可复用 nucleus 真相就位；`Phase 19` 的缺口是“证明如何消费”，不是“再找一套核心”

当前仓库已经具备明确、可裁决的 host-neutral reusable truth：

- `custom_components/lipro/core/auth/bootstrap.py` 提供 `AuthBootstrapSeed` 与 `build_protocol_auth_context()`；
- `custom_components/lipro/core/auth/manager.py` / `custom_components/lipro/core/__init__.py` 提供 `AuthSessionSnapshot` 与 `LiproAuthManager` 作为 formal auth/session truth；
- `custom_components/lipro/core/protocol/facade.py` 明确 `LiproProtocolFacade` 是唯一正式 protocol root；
- `custom_components/lipro/core/capability/registry.py` 与 `custom_components/lipro/core/device/device.py` 已把 capability/device truth 留在 host-neutral nucleus；
- `tests/harness/protocol/replay_driver.py` 与 `scripts/export_ai_debug_evidence_pack.py` 已证明 replay / evidence 可以作为 assurance consumer pull 同一正式真相。

这意味着 `Phase 19` 不需要新建 shared SDK 或第二套路由；真正需要补的是一条 **headless consumer proof path**，证明 future host 只用这些既有真相就能跑通核心链路。

### 2. 现有最大残留是重复 boot wiring 与混合纯度 helper，而不是 formal root 设计错误

focused scan 与并行 explorer 研究都指向同一结论：仍然需要 demote 的，是 adapter-only wiring。

- `custom_components/lipro/config_flow.py` 仍自己负责 `async_get_clientsession()`、password-hash 登录装配与 error mapping；
- `custom_components/lipro/entry_auth.py` 仍自己负责从 `ConfigEntry` 构造 seed、拼装 protocol/auth context、以及 token persistence；
- `custom_components/lipro/flow/credentials.py` 同时包含 pure input helpers 与 HA title-facing projection helper；
- `custom_components/lipro/flow/login.py` 仍是 `hash_password()` 包装、login error mapping 与 config-entry projection 的混合 home。

这里的风险不是“系统跑不通”，而是 future maintainer 很容易把这些 adapter homes 继续误认为可复用 business root，进而在 headless proof 时复制第二套 wiring。

### 3. headless proof 的正确落点是 proof/assurance-style consumer，而不是 package export 或第二 root

north-star、STATE 与 baseline 对 future host 的裁决非常明确：

- 未来 CLI / other host 只能建立在 `LiproProtocolFacade`、boundary contracts、`AuthSessionSnapshot` 与 device/capability truth 之上；
- `Coordinator` 仍是 HA runtime root，不应被抽成 shared runtime；
- replay/evidence 是 assurance consumer，可以 pull 正式真相，但不能反向定义第二套架构。

因此，`Phase 19` 最合理的实现方向不是新建 `custom_components/lipro/headless.py` 或 package-level root，而是：

- 在 `tests/harness/**`、`tests/integration/**`、`scripts/**` 或一个受限 proof helper home 中建立最小 headless consumer proof；
- 让它复用同一 boot contract / protocol root / device truth / replay-evidence path；
- 明确它是 proof harness / assurance consumer，而非新的 production root 或 public export surface。

### 4. 已有 replay / evidence 资产足以证明 “同一 nucleus” 的后半段；前半段只差 boot contract 对齐

`tests/harness/protocol/replay_driver.py` 已经通过 `LiproProtocolFacade` 与 formal boundary public paths 做 deterministic replay；`scripts/export_ai_debug_evidence_pack.py` 已经通过 assurance collector 输出 evidence pack。这说明 “replay/evidence proof” 这一段并不需要另起炉灶。

真正需要补上的，是前半段：

- headless consumer 如何从 `AuthBootstrapSeed` / credentials 输入出发；
- 如何通过同一 `build_protocol_auth_context()` / `LiproProtocolFacade` 建立 session；
- 如何用 formal device discovery / canonicalization 跑出 `LiproDevice` / `CapabilityRegistry` truth；
- 然后再接回 replay/evidence proof，形成 `auth -> device -> replay/evidence` 的单链路证明。

### 5. adapter demotion 的首要对象是 `config_flow.py` / `entry_auth.py` / `flow/*` / 平台 setup 壳；不可触碰的是正式根与已锁定边界

并行研究明确指出，本 phase 可以且应该继续 demote：

- `config_flow.py` 与 `entry_auth.py` 的共装配/boot duplication；
- `flow/credentials.py` / `flow/login.py` 中仍然混合的 pure helper 与 HA-only projection；
- 平台 `async_setup_entry()` 的重复壳；
- `runtime_access.py` 中任何可能被误用成“共享 locator”的 duck-typed compat 故事。

但本 phase **不能** 动摇下列已锁定边界：

- `LiproProtocolFacade` 仍是唯一 protocol root；
- `Coordinator` 仍是唯一 runtime root；
- `AuthSessionSnapshot` 仍是唯一 auth truth；
- `helpers/platform.py` 仍是唯一 HA platform projection home；
- `control/runtime_access.py` 仍只是 control-plane adapter locator，不是 shared core。

### 6. 真正需要新增的治理不是“再写一套路线”，而是明确 proof-consumer 与 second-root 的界限

当前 `ARCHITECTURE_POLICY.md` 已能阻断 nucleus backflow、legacy client 回流、HA platform projection 回流等问题，但还没有显式写出 `Phase 19` 之后最关键的新裁决：

- proof harness / headless consumer 允许存在，但只能是 assurance/proof consumer；
- proof consumer 不得通过 package export、root binding、公共模块入口、或 docs wording 升级为第二正式 root；
- config flow / entry auth / flow helpers 即便被继续收薄，也仍然只是 HA adapter，而不是 shared-core storyteller。

这类规则应体现在 `PUBLIC_SURFACES.md` / `DEPENDENCY_MATRIX.md` / `ARCHITECTURE_POLICY.md` / meta guards 中，而不是只停留在 phase 文案。

## Recommended Phase 19 Scope

### 1. 固定单一 boot contract，并让 adapter / headless consumer 共用它

建议优先把 Phase 19 的第一步聚焦在 “auth/bootstrap composition contract” 上：

- 明确 `AuthBootstrapSeed` / `build_protocol_auth_context()` / `async_login_with_password_hash()` 哪些已经足够作为 shared boot contract；
- 把 shared boot contract 的最小边界写清：至少覆盖 session ownership、authenticated protocol/auth manager 暴露方式、以及 auth-session snapshot 取回方式，而不是只统一 hashed-login 入口；
- 让 `config_flow.py` 与 `entry_auth.py` 继续 inward 到同一 boot contract，而不是各自拼 session / factory / token glue；
- 让 headless proof consumer 通过同一 contract 启动，而不是复制 `config_flow` 或 `entry_auth` 的 logic；
- 明写这条 boot contract 是 local boot seam，不是 canonical/transitional public surface，也不是未来长期 public API 承诺。

### 2. 用最小 proof harness 证明 `auth -> device -> replay/evidence` 同链成立

建议把 proof consumer 放在 assurance/proof 侧，而不是 production root：

- 可行落点包括 `tests/harness/**` + focused integration test，必要时辅以 `scripts/**` proof helper；
- proof 要求复用同一 protocol root、same canonical contracts、same device/capability truth、same replay/evidence path；
- 设备真相的最小证明路径应先走 `LiproDevice.from_api_data()` materialize device，再通过 `device.capabilities` 触发 capability/registry truth，而不是先手工拼一份 `CapabilityRegistry` 输出；
- proof 输出应证明 future host 可复用 truth，而不是引入第二条 production story；
- wave 2 还应补一条 explicit bridge assertion：证明 headless proof 触达的 canonical/device truth 与 replay/evidence 使用的是同一 formal truth family，而不是只把几组测试并排跑绿。

### 3. 继续 demote adapter-only assumptions，但只处理“宿主壳”，不去撬正式根

建议 Phase 19 的 adapter demotion 只处理 high-value residual：

- `config_flow.py` / `entry_auth.py` 共享 boot wiring；
- `flow/credentials.py` / `flow/login.py` 的 mixed-purity helper 分层；
- 平台 `async_setup_entry()` 重复壳向 `helpers/platform.py` 这类 adapter helper 收薄；
- `runtime_access.py` 中任何可能被 future headless 误消费的 compat shim 明确保持 adapter-private 身份。

### 4. 写清 governance boundary：proof consumer 允许存在，但不能合法化成 public root

建议在计划中预留一轮 governance / guard follow-through：

- 更新 baseline wording，明确 headless proof 是 proof-only / assurance-style consumer；
- 新增 targeted bans，防止 `custom_components/lipro/__init__.py`、`custom_components/lipro/core/__init__.py`、`custom_components/lipro/core/protocol/__init__.py` 等模块出现 headless/CLI proof export，并显式禁止 proof home 依赖 `custom_components/lipro/control/runtime_access.py`、`custom_components/lipro/helpers/platform.py` 与 platform setup seams；
- 在 docs wording 中防止“CLI root / HA root”叙事出现；
- 把 authority 默认裁决写透：除非发生新的 truth-source family、authority precedence 变化或 sync owner 变化，否则 `Phase 19` 的 authority disposition 默认为 no-change；proof outputs 只消费 authority path，永不成为 authority path。

## Explicit Defers

以下内容必须继续 defer，不得混入 `Phase 19`：

1. release-grade CLI / packaged binary / general-purpose SDK story；
2. `Coordinator` shared runtime extraction 或新的 runtime root；
3. `Phase 20` 的 remaining boundary family completion；
4. `Phase 21` 的 broad-catch / failure classification hardening；
5. `Phase 22` 的全局 governance/release closeout；
6. 大规模 rename campaign / package split / framework abstraction。

## Risks

### 1. 最小 proof harness 若落点错误，很容易长成 second root

若把 headless proof 直接做成 package export、root module、或长期 public command surface，会直接违反单一主链原则。

**Mitigation:** 把它限定为 proof-only harness / script / test consumer，并在 baseline + guards 中写死“不是第二 root”。

### 2. 若直接复制 `config_flow.py` / `entry_auth.py` 逻辑，proof 只会证明“可以复制”，不能证明“可以复用”

最大的伪成功风险，是用新 helper 再写一遍登录、token、device discovery orchestration。

**Mitigation:** 强制 proof consumer 只经由 boot contract、formal protocol root、canonical device truth 和 assurance paths 运行。

### 3. mixed-purity helper demotion 若范围失控，容易变成低价值 churn

`flow/credentials.py` 与平台 setup 壳确实还能继续收薄，但不应演化成大规模 rename / house-cleaning。

**Mitigation:** 只收口与 headless proof 直接相关的 helper / seam；不做无 gate rename campaign。

### 4. 平台 setup 壳抽象若处理不慎，可能把 platform semantics 重新推回 shared core

平台 wiring 的复用价值只存在于 adapter 层；如果抽象位置错误，会让 `platform` strings 或 HA-specific setup semantics 再次污染 nucleus。

**Mitigation:** 仅允许向 `helpers/platform.py` 或等价 adapter helper inward，不允许反向进入 `core/capability` / `core/device`。

### 5. replay/evidence proof 若只验证工具链存在，而不验证 authority path 复用，会留下假阳性

单纯调用 exporter 或 replay driver 不足以证明 “same nucleus”；必须证明前半段 auth/device truth 与后半段 replay/evidence 同链对接。

**Mitigation:** 在 proof 计划里明确要求 single-chain verification，而不是分散的点状回归。

### 6. 如果没有显式 bridge assertion，single-chain 叙事仍可能是假连通

当前 replay 与 evidence 都建立在既有 fixture / collector 正式路径之上，但它们不会天然证明 headless proof 的 auth/device 输出与后半段消费的是同一 formal truth family。

**Mitigation:** 新增一个 bridge assertion，只证明“同一 truth family 被触达”，而不是让 evidence/exporter 直接改吃 headless proof 输出。

## Validation Architecture

### Fast feedback loop

- `uv run pytest -q tests/flows/test_config_flow.py tests/core/test_init.py tests/core/test_token_persistence.py`
- `uv run pytest -q tests/core/capability/test_registry.py tests/core/device/test_device.py tests/platforms/test_entity_behavior.py`
- `uv run pytest -q tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py`

### Architecture / governance loop

- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py`

### Full confidence loop after implementation

- `uv run ruff check .`
- `uv run mypy`
- `uv run pytest -q`

### Phase-specific validation expectation

- Wave 1 必须先证明 boot contract 被 adapter 与 proof consumer 共用，而不是继续双装配；
- Wave 2 必须证明 `auth -> device -> replay/evidence` 使用同一 nucleus 与 formal public path；
- Wave 3 必须证明 adapter demotion + governance wording/guards 已锁定 “proof consumer ≠ second root”。

## Forced Re-Research Addendum

A second forced-research pass tightened several execution details without changing the overall Phase 19 story:

- `AuthBootstrapSeed` / bootstrap helpers are sufficient to define the auth/bootstrap seam, but not yet sufficient alone to define the full headless discovery seam; the boot contract should explicitly state session ownership, authenticated protocol exposure, and auth-session snapshot retrieval.
- The minimal device-truth path should materialize devices via `LiproDevice.from_api_data()` first, then observe `device.capabilities` / registry truth; proof should not start by precomputing `CapabilityRegistry` outputs out-of-band.
- The replay/evidence half already reuses formal paths, but Phase 19 still needs an explicit bridge assertion proving headless proof touches the same formal truth family, rather than merely running headless tests and replay/evidence tests side by side.
- Governance wording should state that headless proof is an assurance/proof-only consumer, boot contract is not a canonical/transitional public surface, and authority disposition remains `no-change` unless truth-source family, precedence, or sync owner changes.
- The chosen proof home should be guarded not only against `homeassistant` and `Coordinator`, but also against `custom_components/lipro/control/runtime_access.py`, `custom_components/lipro/helpers/platform.py`, and platform setup seams.

## Final Arbitration

`Phase 19` 的最佳裁决非常明确：

- 这不是一个“发明 headless 架构”的 phase，而是一个 **证明既有 host-neutral nucleus 真的能被 headless consumer 复用** 的 phase；
- 真正该动的是 boot contract duplication、mixed-purity adapter helpers、平台 setup 壳与相关治理文案；
- 真正不能动的是 `LiproProtocolFacade`、`Coordinator`、`AuthSessionSnapshot`、`helpers/platform.py`、control-plane runtime locator 这些已经锁定的正式边界；
- 若本 phase 成功，仓库会获得一条经证明的 “future host can reuse the same truth” 故事线，而不会裂变成 “HA root + CLI root” 双体系。
