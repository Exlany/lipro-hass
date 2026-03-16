# Phase 18 Research

**Phase:** `18 Host-Neutral Boundary Nucleus Extraction`
**Source inputs:** `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, baseline/review assets, `Phase 10` / `Phase 17` artifacts, focused code scan
**Date:** 2026-03-16

## Inputs

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/ARCHITECTURE_POLICY.md`
- `.planning/phases/10-api-drift-isolation-core-boundary-prep/10-CONTEXT.md`
- `.planning/phases/10-api-drift-isolation-core-boundary-prep/10-RESEARCH.md`
- `.planning/phases/17-final-residual-retirement-typed-contract-tightening-and-milestone-closeout/17-CONTEXT.md`
- `.planning/phases/17-final-residual-retirement-typed-contract-tightening-and-milestone-closeout/17-RESEARCH.md`
- `custom_components/lipro/config_flow.py`
- `custom_components/lipro/entry_auth.py`
- `custom_components/lipro/flow/login.py`
- `custom_components/lipro/core/auth/manager.py`
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/protocol/contracts.py`
- `custom_components/lipro/core/capability/models.py`
- `custom_components/lipro/core/capability/registry.py`
- `custom_components/lipro/core/device/device.py`
- `custom_components/lipro/core/device/device_views.py`
- `custom_components/lipro/const/categories.py`
- `custom_components/lipro/helpers/platform.py`
- `tests/flows/test_config_flow.py`
- `tests/core/test_init.py`
- `tests/core/test_token_persistence.py`
- `tests/core/test_categories.py`
- `tests/core/device/test_capabilities.py`
- `tests/core/capability/test_registry.py`
- `tests/meta/test_dependency_guards.py`

## Key Findings

### 1. Auth session truth 已成熟，但 login/bootstrap seam 仍滞留在 HA adapter 层

`core/auth/manager.py` 已拥有稳定的 `AuthSessionSnapshot`，`entry_auth.py` 的 token persistence 也只消费这套 formal contract；但 `config_flow.py` 仍直接 new `LiproProtocolFacade` + `LiproAuthManager` 完成登录，而 `flow/login.py` 的 `LoginResult` 继续在 HA flow 层定义“成功登录后该如何投影到 entry data”。这说明：

- formal auth/session truth 已经足够成熟，可作为 host-neutral nucleus；
- 但 **login use case / result projector / bootstrap seam** 仍散落在 `config_flow.py`、`flow/login.py`、`entry_auth.py` 三个 adapter homes；
- 若未来要做 `Phase 19` 的 headless proof，最容易被复制/分叉的就是这段 bootstrap/login story。

**Implication:** `Phase 18` 应先抽出 host-neutral auth/login/bootstrap contract 与 projector seam，让 HA flow / entry setup 只保留 adapter 输入/持久化职责。

### 2. `entry_auth.py` 与 `EntryLifecycleController` 之间仍存在“adapter orchestration + shared bootstrap”混合地带

`entry_auth.py` 里既有明显 HA-only 的 `ConfigEntryAuthFailed` / `ConfigEntryNotReady` 映射，也有 `build_entry_auth_context()`、`get_entry_int_option()`、token persistence 这类更接近 reusable bootstrap helper 的逻辑；`control/entry_lifecycle_controller.py` 则继续注入这些函数式协作者来组装 entry lifecycle。这比旧架构已经先进很多，但仍留下一个问题：

- host-neutral auth/bootstrap seam 没有一个显式、可复用、可守卫的 home；
- 未来宿主若要复用 auth bootstrap，容易去复制 `entry_auth.py` 或直接模仿 `config_flow.py`；
- 目前 adapter 与 nucleus 的边界更多靠“维护者理解”，而不是靠 module home / contract 命名固定下来。

**Implication:** `Phase 18` 应把共享 bootstrap parts 向 `core/auth` 或明确的 host-neutral helper home 收敛，同时保留 HA-specific exception mapping / config-entry persistence 在 adapter。

### 3. `device/capability` 方向存在最明确的 host-specific leak：HA platform projection 仍在 core truth 里

这是本 phase 最清晰、最硬的物理问题：

- `const/categories.py` 同时承担 **device kind classification** 与 `CATEGORY_TO_PLATFORMS` / `get_platforms_for_category()`；
- `core/capability/models.py` 的 `CapabilitySnapshot` 直接包含 `platforms: tuple[str, ...]` 与 `supports_platform()`；
- `core/capability/registry.py` 在构造 capability snapshot 时直接写入 HA platform strings；
- `core/device/device_views.py` 明确把 `category()` / `platforms()` 表述为 “Home Assistant category/platforms”；
- 平台模块如 `light.py` / `cover.py` 通过 `device.capabilities.supports_platform("light")` 之类路径消费这层投影。

这说明 device/domain 真源与 HA host projection 还没有完全分层：**host-neutral nucleus 里仍携带平台适配语义**。

**Implication:** `Phase 18` 应把 `device kind / capability truth` 与 `HA platform projection` 分成两层：前者保留在 nucleus，后者下沉到 adapter projection/home；但不在本 phase 引入新 root 或大规模平台重写。

### 4. 当前 meta guards 还没有专门覆盖 host-neutral nucleus locality

现有 baseline/guards 已经很好地保护了：

- entity/platform 不直连 protocol internals；
- control 不 bypass runtime/protocol internals；
- boundary decoders 不越界；
- MQTT transport import 不扩散。

但它们还没有直接表达以下规则：

- nucleus homes 不得 import `homeassistant`；
- nucleus homes 不得再次承载 HA platform projection strings / adapter-only helpers；
- `config_flow.py` / `entry_auth.py` 允许依赖 host-neutral auth contract，但不允许重新定义第二套 login result truth。

**Implication:** `Phase 18` 的 deliverable 不能只有代码拆分，还必须补 architecture policy + dependency guards + focused regression，锁住新的 nucleus locality。

### 5. `LiproProtocolFacade` / `Coordinator` 已基本满足“只保留正式根身份”的前提，本 phase 不应扰动根

`Phase 10` 与 `Phase 17` 的收敛结果说明：当前真正需要做的是 helper/contract/home extraction，而不是重做 façade 或 coordinator。`core/protocol/facade.py` 继续以 protocol root 组装 REST/MQTT 子门面；`coordinator_entry.py` 继续是 HA runtime public home；`core/__init__.py` 也未再把 `Coordinator` 混入 core public surface。

**Implication:** `Phase 18` 应避免 touching root identity，只做 **contract seams / helper home / adapter demotion / guards**。这也是防止 second root 回潮的关键。

## Recommended Phase 18 Scope

### Plan 18-01 — 提炼 host-neutral auth/device contracts 与 adapter seams

建议收敛的焦点：

- 让 `flow/login.py` 的 `LoginResult`、`config_flow.py` 的 `_async_do_login()` / `_async_try_login()` 与 `entry_auth.py` 的 auth bootstrap 共享同一组 host-neutral auth/login result contract；
- 把 `device kind` 与 `HA platform projection` 的概念分离，明确哪一层是 host-neutral capability truth，哪一层是 adapter projection seam；
- 保持 `LiproProtocolFacade` / `Coordinator` 不动，只梳理它们周围的 typed contract 与 collaborator home。

高概率涉及：

- `custom_components/lipro/config_flow.py`
- `custom_components/lipro/entry_auth.py`
- `custom_components/lipro/flow/login.py`
- `custom_components/lipro/core/auth/manager.py`
- `custom_components/lipro/core/capability/models.py`
- `custom_components/lipro/core/capability/registry.py`
- `custom_components/lipro/core/device/device_views.py`
- `custom_components/lipro/const/categories.py`

### Plan 18-02 — 抽离 auth/device/shared helpers 到 nucleus home

建议收敛的焦点：

- 把已成熟的 auth/login/bootstrap projector helper 从 flow/entry adapter 移到 `core/auth` 或等价的 host-neutral helper home；
- 把 device/capability 中的 host-neutral classification truth 与 HA-only platform projection 分拆，避免 `core/device` / `core/capability` 继续承载 adapter 平台语义；
- 同步更新调用点，让 HA flow、entry setup、platform setup 改为消费 seam/projection，而不是直接依赖旧 home。

高概率涉及：

- `custom_components/lipro/core/auth/**`
- `custom_components/lipro/flow/login.py`
- `custom_components/lipro/config_flow.py`
- `custom_components/lipro/entry_auth.py`
- `custom_components/lipro/core/capability/**`
- `custom_components/lipro/core/device/**`
- `custom_components/lipro/helpers/platform.py`
- `custom_components/lipro/light.py`
- `custom_components/lipro/cover.py`
- `custom_components/lipro/switch.py`
- 及相邻平台 setup 文件

### Plan 18-03 — 补齐 locality guards 与 focused regression

建议收敛的焦点：

- 为新的 nucleus home 增加 import/locality 规则，明确禁止 `homeassistant` imports 与 HA-only projection 回流；
- 更新 baseline/docs，让 `PUBLIC_SURFACES.md`、`DEPENDENCY_MATRIX.md`、`ARCHITECTURE_POLICY.md` 正式承认 host-neutral nucleus family 的身份，但明确其 **不是** 新 public root；
- 补齐 focused regression tests，覆盖 auth/login seam、entry auth bootstrap、device/capability projection 分层、dependency guards。

高概率涉及：

- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/ARCHITECTURE_POLICY.md`
- `tests/meta/test_dependency_guards.py`
- `tests/flows/test_config_flow.py`
- `tests/core/test_init.py`
- `tests/core/test_token_persistence.py`
- `tests/core/test_categories.py` 或其后续替代测试
- `tests/core/device/test_capabilities.py`
- `tests/core/capability/test_registry.py`

## Explicit Defers

以下内容必须明确 defer，不应混进 `Phase 18`：

1. **`CORE-02` / headless or CLI composition root proof** —— 这是 `Phase 19` 的正式目标；
2. **remaining replay/boundary family completion**（`SIM-03/05`）—— 属于 `Phase 20`；
3. **broad-catch / exception classification 全量 hardening**（`ERR-02` / `OBS-03`）—— 属于 `Phase 21`；
4. **v1.2 governance/release full closeout**（`GOV-16` 的最终收口）—— 属于 `Phase 22`；
5. **physical shared SDK / package split / cross-repo extraction** —— 不属于本轮里程碑的允许动作。

## Risks

### 1. device/capability 平台投影外移会带来较多测试与平台装配面联动

`tests/core/test_categories.py`、`tests/core/device/test_capabilities.py`、`tests/core/capability/test_registry.py`、`tests/entities/test_descriptors.py` 以及各 platform setup 文件都与现有 `DeviceCategory/platforms` 语义耦合。若一次性做大规模 rename 或类型重命名，容易制造高 churn。

**Mitigation:** 在 `Phase 18` 里优先做 seam 分层与 home demotion，谨慎控制 naming churn，必要时保留 transitional projection helper，但要有明确 delete gate。

### 2. auth/bootstrap seam 抽离若过度设计，容易演化成 framework story

`config_flow.py` 与 `entry_auth.py` 的共享逻辑确实值得收口，但如果引入过多抽象层、builder 或 generic host adapter framework，就会偏离 north-star。

**Mitigation:** 只抽成熟 contract / projector / use case helper；不要引入“可插拔宿主框架”。

### 3. 守卫若只写 import 规则，不覆盖 projection truth，仍可能留下语义回流

仅禁止 `homeassistant` import 还不够；HA platform strings、platform-specific helper names 也可能以纯字符串或 const mapping 形式重新混入 nucleus。

**Mitigation:** baseline wording 与 targeted regression 必须一起上，必要时增加 file_contains 或 targeted fixture assertions，而不是只靠 import guard。

## Validation Matrix

### Focused fast loop

- `uv run pytest -q tests/flows/test_config_flow.py tests/core/test_init.py tests/core/test_token_persistence.py`
- `uv run pytest -q tests/core/device/test_capabilities.py tests/core/capability/test_registry.py tests/entities/test_descriptors.py`
- `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py`

### Phase-specific architecture / governance loop

- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py`

### Full confidence loop after implementation

- `uv run ruff check custom_components/lipro tests`
- `uv run mypy`
- `uv run pytest -q`

## Final Arbitration

`Phase 18` 的最佳实现不是“宣称我们已经有 shared core”，也不是“再做一轮大拆包”，而是把已经在 `Phase 10` 成熟、在 `Phase 17` 清完尾债之后真正留下的 **host-neutral auth/device nucleus** 物理归位：

- auth/session/login/bootstrap 只保留一条 host-neutral contract story；
- device/capability 只保留 device/domain truth，不再把 HA platform projection 记成 core truth；
- HA flow、entry setup、platform setup 继续只是 adapter / projection；
- `LiproProtocolFacade` / `Coordinator` 继续保持唯一正式根；
- 守卫与文档把这条边界固定下来，为 `Phase 19` 的 headless proof 铺路，但不偷跑进去。
