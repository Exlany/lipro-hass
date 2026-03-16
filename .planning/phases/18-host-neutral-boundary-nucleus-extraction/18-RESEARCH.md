# Phase 18 Research

**Phase:** `18 Host-Neutral Boundary Nucleus Extraction`
**Source inputs:** `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, baseline/review assets, `Phase 10` / `Phase 17` artifacts, focused code scan, forced re-research (`--research`)
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
- `custom_components/lipro/flow/schemas.py`
- `custom_components/lipro/flow/options_flow.py`
- `custom_components/lipro/core/auth/__init__.py`
- `custom_components/lipro/core/auth/manager.py`
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/capability/models.py`
- `custom_components/lipro/core/capability/registry.py`
- `custom_components/lipro/core/device/device.py`
- `custom_components/lipro/core/device/device_views.py`
- `custom_components/lipro/const/categories.py`
- `custom_components/lipro/helpers/platform.py`
- `custom_components/lipro/light.py`
- `custom_components/lipro/cover.py`
- `custom_components/lipro/climate.py`
- `custom_components/lipro/switch.py`
- `tests/flows/test_config_flow.py`
- `tests/core/test_init.py`
- `tests/core/test_token_persistence.py`
- `tests/core/test_categories.py`
- `tests/core/device/test_capabilities.py`
- `tests/core/capability/test_registry.py`
- `tests/platforms/test_entity_behavior.py`
- `tests/meta/test_dependency_guards.py`

## Key Findings

### 1. Auth session truth 已成熟，但 login/bootstrap 真相仍被 `flow/` 与 adapter homes 分裂持有

当前 auth 方向已经有一个明显成熟的 host-neutral nucleus：

- `custom_components/lipro/core/auth/manager.py` 提供 `AuthSessionSnapshot` 与 `LiproAuthManager`；
- `custom_components/lipro/entry_auth.py` 的 token persistence 已只消费 `AuthSessionSnapshot`；
- `.planning/DEPENDENCY_MATRIX.md` 也已经明确 `config_flow.py` / `entry_auth.py` 可以依赖这类 host-neutral contract。

但 forced re-research 显示，**登录与引导故事线仍然物理分裂**：

- `custom_components/lipro/flow/login.py` 定义了 `LoginResult`、`hash_password()`、`map_login_error()`；
- `custom_components/lipro/config_flow.py` 直接 new `LiproProtocolFacade` + `LiproAuthManager`，并返回 `LoginResult`；
- `custom_components/lipro/flow/schemas.py` 与 `custom_components/lipro/flow/options_flow.py` 则明确是 HA-only UI/selector/options 逻辑。

这说明 `flow/` 目录当前是 **host-neutral helper 与 HA-only flow UI 的混合包**。如果未来 Phase 18 不把可复用 login/bootstrap contract 拿出来，就会继续让新维护者误以为 `flow/login.py` 是正式 shared home，或者在 `Phase 19` 做 headless proof 时复制一套相近逻辑。

**Implication:** `Phase 18` 应把可复用 login/auth result 与 bootstrap projector helper 收口到 `core/auth` 或等价的 host-neutral home；`flow/` 保留 HA-only form/schema/options/entry-data shaping。

### 2. `entry_auth.py` 的 shared bootstrap seam 已经成形，但它仍被 adapter 异常语义包裹

`custom_components/lipro/entry_auth.py` 同时承载了三类责任：

1. `ConfigEntryAuthFailed` / `ConfigEntryNotReady` 映射 —— 明显 HA-only；
2. `build_entry_auth_context()` / `get_entry_int_option()` / `persist_entry_tokens_if_changed()` —— 更接近 reusable bootstrap helpers；
3. `clear_entry_runtime_data()` —— 明显 entry/runtime adapter cleanup。

另外，`build_entry_auth_context()` 与相关 helper 已被多个正式入口与测试消费：

- `custom_components/lipro/__init__.py` 将其注入 `EntryLifecycleController`；
- `tests/core/test_init.py` 与 `tests/core/test_token_persistence.py` 直接围绕这些函数写回归；
- `tests/test_coordinator_runtime.py` 还通过 root patch 它们的符号身份。

这意味着：**Phase 18 可以抽 seam，但不能粗暴改掉 adapter 注入表面**。若直接移动或删除这些名字，不仅会打断现有控制面装配，也会让测试 patch seam 失真。

**Implication:** 适合的做法是：把 shared bootstrap logic inward-move 到 host-neutral home，同时保留 `entry_auth.py` 作为 adapter façade / re-export / exception mapper；不要把 Phase 18 演化成无 gate rename campaign。

### 3. `device/capability` 的真实裂隙比上一轮判断更清晰：HA platform projection 正在污染 core truth

forced re-research 进一步证实，当前最明确的 host-specific leak 在 `device/capability`：

- `custom_components/lipro/const/categories.py` 同时定义 `DeviceCategory` 与 `CATEGORY_TO_PLATFORMS` / `get_platforms_for_category()`；
- `custom_components/lipro/core/capability/models.py` 的 `CapabilitySnapshot` 直接包含 `platforms` 字段与 `supports_platform()`；
- `custom_components/lipro/core/capability/registry.py` 在 registry 里就把 HA platform strings 写入 capability truth；
- `custom_components/lipro/core/device/device_views.py` 文档字符串直接声明 “Home Assistant category/platforms”；
- 平台模块 `custom_components/lipro/light.py`、`custom_components/lipro/cover.py`、`custom_components/lipro/climate.py`、`custom_components/lipro/switch.py` 直接依赖 `device.capabilities.supports_platform(...)`。

这不是单纯命名问题，而是 **device/domain truth 与 host projection 未分层**。只要 `core/capability` 继续携带 HA platform 字符串，就还不能称为真正 host-neutral nucleus。

**Implication:** `Phase 18` 必须把 “device kind / capability truth” 与 “HA platform projection” 分成两层；但由于 `supports_platform()` 已被多处平台 setup 与测试消费，应该优先做 projection seam 外移 + transitional compatibility，而不是一次性大拆所有调用点。

### 4. 现有守卫链仍缺少 nucleus-locality 专项规则

当前 baseline/guards 已很好地锁住：

- entity/platform 不直连 protocol internals；
- control 不绕过 runtime public surface；
- boundary decoder locality；
- MQTT transport locality；
- assurance 不回流 production。

但 forced re-research 发现，尚缺两类与 Phase 18 高度相关的规则：

1. **host-neutral nucleus no-HA-import rule**：至少应覆盖 `core/auth`、`core/capability`、`core/device` 等新/既有 nucleus homes，阻止 `homeassistant` imports 回流；
2. **platform projection locality rule**：明确 `CATEGORY_TO_PLATFORMS` / `get_platforms_for_category()` / `supports_platform()` 这类 host projection 不应继续被登记为 core capability truth，或至少要局部化到 adapter projection home。

仅有 import disjoint 还不够；还需要 baseline wording + focused regression 共同固定这条边界。

**Implication:** `Phase 18` 不能只交付代码收口，还必须同步 `.planning/baseline/ARCHITECTURE_POLICY.md`、`.planning/baseline/DEPENDENCY_MATRIX.md`、`.planning/baseline/PUBLIC_SURFACES.md` 与 `tests/meta/test_dependency_guards.py`。

### 5. `LiproProtocolFacade` / `Coordinator` 已满足“根不该动”的前提，本 phase 应避开 root churn

当前仓库状态显示：

- `custom_components/lipro/core/protocol/facade.py` 仍稳定承担唯一 protocol root；
- `custom_components/lipro/coordinator_entry.py` 仍是 HA runtime public home；
- `custom_components/lipro/core/__init__.py` 没有重新把 `Coordinator` 混入 core truth；
- `Phase 10` 与 `Phase 17` 已经把旧 root/residual 故事线收口到很窄。

这意味着 `Phase 18` 的真正工作是 **contract seam / helper home / projection demotion / guard hardening**，而不是对根对象做大手术。任何 touching façade/coordinator root identity 的动作，都极容易越界成 `Phase 19` 甚至 second-root experimentation。

**Implication:** `Phase 18` 必须坚持“helper inward, adapter outward, root untouched”。

## Recommended Phase 18 Scope

### 1. Auth/bootstrap seam extraction

建议聚焦：

- 把 `custom_components/lipro/flow/login.py` 里的可复用 login/auth result helper 与 HA-only `entry-data` shaping 拆开；
- 让 `custom_components/lipro/config_flow.py` 只保留 form input、error mapping、entry creation，而不是承担 shared login result truth；
- 让 `custom_components/lipro/entry_auth.py` 保留 adapter façade / exception mapping / runtime cleanup，但把共享 bootstrap internals inward-move 到 host-neutral home；
- 明确保留现有 root-injection seam（如 `build_entry_auth_context`）的稳定性，避免破坏 `__init__.py` 与测试 patch surface。

### 2. Device/capability projection demotion

建议聚焦：

- 将 `DeviceCategory` 继续保留为 device-kind truth，但审视 `CATEGORY_TO_PLATFORMS` / `get_platforms_for_category()` 是否应迁到 adapter projection helper；
- 让 `CapabilitySnapshot` 更偏向 device truth，不再把 HA platform projection 视为主语义；
- 将 `supports_platform()` 与平台选择逻辑转向 adapter seam（优先考虑 `helpers/platform.py` 或相邻 adapter projection helper），但允许短期兼容桥保持现有平台 setup 可运行；
- 同步修正文档字符串与 tests，避免继续把 `device_views.category/platforms()` 当作 “Home Assistant category/platforms” 的 core truth 输出。

### 3. Locality guards and regression proof

建议聚焦：

- 新增/收紧架构规则，至少覆盖 nucleus no-HA-import 与 host projection locality；
- 更新 baseline docs，明确 host-neutral nucleus 是 formal helper/contract family，而非新 public root；
- 用 focused tests 锁定 `build_entry_auth_context` seam、token persistence、platform filtering、capability projection 的正确分层。

## Explicit Defers

以下内容必须继续 defer，不应混进 `Phase 18`：

1. **`CORE-02` / headless or CLI composition root proof** —— 这是 `Phase 19`；
2. **remaining replay/boundary family completion**（`SIM-03/05`）—— 这是 `Phase 20`；
3. **broad-catch / exception classification 全量 hardening**（`ERR-02` / `OBS-03`）—— 这是 `Phase 21`；
4. **v1.2 governance/release full closeout**（`GOV-16` 的最终收口）—— 这是 `Phase 22`；
5. **physical shared SDK / package split / framework 化 host system** —— 明确不属于本 phase。

## Risks

### 1. `flow/login.py` relocation 若处理不慎，容易把 HA-only flow 包与 host-neutral helper 再次缠在一起

`flow/schemas.py` 与 `flow/options_flow.py` 已明确依赖 `homeassistant`；如果只是把 `LoginResult` 留在 `flow/` 并改几处导入，实际并没有完成 nucleus extraction。

**Mitigation:** 用 module home 讲清故事：host-neutral helper inward，HA flow UI outward。

### 2. `build_entry_auth_context` 等 seam 已被 root injection 与测试 patch 广泛依赖，粗暴改名会制造低价值 churn

`tests/core/test_init.py`、`tests/core/test_token_persistence.py`、`tests/test_coordinator_runtime.py` 都围绕这些符号写了回归；Phase 18 若改动 surface，必须提供稳定 adapter façade 或过渡 alias。

**Mitigation:** 保持 outward seam 稳定，内部再收口 shared logic。

### 3. `supports_platform()` 与 `platforms` 字段传播面较广，不适合一次性物理删除

平台 setup 与 `tests/platforms/test_entity_behavior.py`、`tests/core/capability/test_registry.py` 等都依赖这条语义。一次性硬删容易让计划从“projection demotion”变成“无差别改平台”。

**Mitigation:** 本 phase 优先 demote semantics 与 home；必要时保留 transitional compatibility，并配 delete gate。

### 4. 仅加 import guard 不足以阻止字符串级 host projection 回流

即便 nucleus home 没有 `homeassistant` import，仍可能通过 `CATEGORY_TO_PLATFORMS = {"light": ...}` 这类方式继续携带 HA host 语义。

**Mitigation:** baseline wording、file-level assertions 与 focused regression 要同时上，不只靠 import scan。

## Validation Matrix

### Focused fast loop

- `uv run pytest -q tests/flows/test_config_flow.py tests/core/test_init.py tests/core/test_token_persistence.py`
- `uv run pytest -q tests/core/test_categories.py tests/core/device/test_capabilities.py tests/core/capability/test_registry.py tests/platforms/test_entity_behavior.py`
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

forced re-research 之后，`Phase 18` 的最佳裁决比上一轮更清楚：

- **auth 方向**：成熟 nucleus 是 `AuthSessionSnapshot` / auth manager / shared bootstrap helper，不是 `flow/` 整包；
- **device 方向**：成熟 nucleus 是 `DeviceCategory` / capability truth / device identity/state，不是 HA platform projection；
- **adapter 方向**：`config_flow.py`、`entry_auth.py`、platform setup、`helpers/platform.py` 应承担宿主输入、异常映射、entry shaping、platform filtering；
- **治理方向**：必须用 baseline + guards 把 “host-neutral nucleus 不是第二 root” 这条边界写死。

因此 `Phase 18` 不是“再做一轮大重构”，而是把 `Phase 10` 留下的 host-neutral debt 终于从语义层推进到物理 home 与守卫层：让 future-host 可复用 truth 真正有家，但又不让仓库裂变成第二套合法架构。
