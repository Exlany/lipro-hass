# Phase 19 Verification

status: passed

## Goal

- 核验 `Phase 19: Headless Consumer Proof & Adapter Demotion` 是否达成 `CORE-02`：同一套 host-neutral nucleus 能被 headless / CLI-style consumer 复用，完成认证、设备发现与 replay/evidence proof，且不长出第二条合法 root。
- 终审结论：**`CORE-02` 已达成；Phase 19 所需 proof 链、adapter demotion、baseline/review 同步与 repo-wide governance bundle 现已全部对齐，因此整相位签核记为 `passed`。**

## Reviewed Assets

- 规划/需求锚点：`.planning/ROADMAP.md:341`、`.planning/REQUIREMENTS.md:244`
- Phase 资产：`.planning/phases/19-headless-consumer-proof-adapter-demotion/19-CONTEXT.md:1`、`.planning/phases/19-headless-consumer-proof-adapter-demotion/19-VALIDATION.md:1`
- 已生成 summaries：`.planning/phases/19-headless-consumer-proof-adapter-demotion/19-01-SUMMARY.md:1`、`.planning/phases/19-headless-consumer-proof-adapter-demotion/19-02-SUMMARY.md:1`、`.planning/phases/19-headless-consumer-proof-adapter-demotion/19-03-SUMMARY.md:1`、`.planning/phases/19-headless-consumer-proof-adapter-demotion/19-04-SUMMARY.md:1`
- 实现/测试/治理真源：`custom_components/lipro/headless/boot.py:1`、`custom_components/lipro/config_flow.py:48`、`custom_components/lipro/entry_auth.py:37`、`tests/harness/headless_consumer.py:1`、`tests/integration/test_headless_consumer_proof.py:1`、`.planning/baseline/PUBLIC_SURFACES.md:147`、`.planning/reviews/RESIDUAL_LEDGER.md:219`

## Must-Haves

- **1. `custom_components/lipro/headless/boot.py` 保持 proof-only / non-public / non-authority / non-second-root — PASS**
  - `custom_components/lipro/headless/boot.py:1` 明示 `Local, proof-only`；`custom_components/lipro/headless/boot.py:3` 明示其 **不是 canonical / transitional public surface**。
  - `custom_components/lipro/headless/boot.py:29` 仅暴露 formal auth/session snapshot boundary；`custom_components/lipro/headless/boot.py:81` 继续委托 `build_protocol_auth_context()`，没有自行形成第二 protocol/runtime root。
  - `custom_components/lipro/headless/__init__.py:1` 与 `custom_components/lipro/headless/__init__.py:8` 明确 package 是 no-export proof-only helper home。
  - baseline/review 已同步这一身份：`.planning/baseline/PUBLIC_SURFACES.md:147`、`.planning/baseline/PUBLIC_SURFACES.md:148`、`.planning/reviews/FILE_MATRIX.md:232`、`.planning/reviews/FILE_MATRIX.md:233`、`.planning/reviews/RESIDUAL_LEDGER.md:219`、`.planning/reviews/KILL_LIST.md:175`。

- **2. `config_flow.py` 与 `entry_auth.py` 共享同一 boot seam — PASS**
  - `custom_components/lipro/config_flow.py:48` 与 `custom_components/lipro/config_flow.py:91` 通过 `build_password_boot_seed()` + `build_headless_boot_context()` 进入同一 boot seam。
  - `custom_components/lipro/entry_auth.py:37` 与 `custom_components/lipro/entry_auth.py:141` 也使用相同的 `build_headless_boot_context()`；entry 侧只额外保留 token persistence callback，未复制第二套 auth bootstrap。
  - adapter 回归测试直接 patch 同一 seam：`tests/flows/test_config_flow.py:517`、`tests/core/test_token_persistence.py:48`。
  - baseline/review 文字与实现一致：`.planning/baseline/PUBLIC_SURFACES.md:150`、`.planning/reviews/RESIDUAL_LEDGER.md:220`。

- **3. `tests/harness/headless_consumer.py` 与 `tests/integration/test_headless_consumer_proof.py` 证明 auth -> device -> replay/evidence bridge 使用同一 nucleus / formal truth family — PASS**
  - harness 直接复用同一 boot seam：`tests/harness/headless_consumer.py:104`；认证分支仅在 `password_hash` 与 token-reuse 两条 formal auth path 间切换：`tests/harness/headless_consumer.py:147`。
  - 设备物化来自 formal protocol + domain truth，而非第二实现：`tests/harness/headless_consumer.py:112` 读取 device page，`tests/harness/headless_consumer.py:113` 使用 `LiproDevice.from_api_data()`，`tests/harness/headless_consumer.py:136` 使用 `CapabilityRegistry.from_device()` 构造 capability snapshots。
  - proof artifact 明确锁定 formal public paths / assertion families：`tests/harness/headless_consumer.py:30`、`tests/harness/headless_consumer.py:35`、`tests/harness/headless_consumer.py:82`、`tests/harness/headless_consumer.py:83`。
  - integration proof 断言 headless consumer 复用同一 boot seam 并完成 auth/device 物化：`tests/integration/test_headless_consumer_proof.py:61`、`tests/integration/test_headless_consumer_proof.py:69`、`tests/integration/test_headless_consumer_proof.py:80`。
  - replay/evidence bridge 断言同一 assertion family 接到 replay manifests，同时 proof assets 不进入 authority source paths：`tests/integration/test_headless_consumer_proof.py:118`、`tests/integration/test_headless_consumer_proof.py:125`、`tests/integration/test_headless_consumer_proof.py:128`、`tests/harness/evidence_pack/sources.py:28`、`tests/meta/test_evidence_pack_authority.py:73`。

- **4. 平台 setup shell 仍薄，且不导入 `control/runtime_access.py` — PASS**
  - 薄壳 helper 继续集中在 `custom_components/lipro/helpers/platform.py:69`；其职责只有 `entry.runtime_data -> async_add_entities(...)` 的 adapter projection。
  - 平台 `async_setup_entry()` 只做 helper 委派：`custom_components/lipro/light.py:47`、`custom_components/lipro/light.py:53`、`custom_components/lipro/cover.py:41`、`custom_components/lipro/cover.py:47`、`custom_components/lipro/fan.py:95`、`custom_components/lipro/fan.py:101`、`custom_components/lipro/select.py:67`、`custom_components/lipro/select.py:73`、`custom_components/lipro/switch.py:244`、`custom_components/lipro/switch.py:250`、`custom_components/lipro/update.py:21`、`custom_components/lipro/update.py:27`。
  - 依赖矩阵与 policy 明确禁止 platform shell 重新依赖 control locator：`.planning/baseline/DEPENDENCY_MATRIX.md:42`、`.planning/baseline/DEPENDENCY_MATRIX.md:85`、`.planning/baseline/ARCHITECTURE_POLICY.md:36`、`.planning/reviews/RESIDUAL_LEDGER.md:221`。
  - meta guard 钉死这一点：`tests/meta/test_dependency_guards.py:85`。

- **5. baseline / review / meta guards 已与实现对齐 — PASS**
  - Phase 19 专项 baseline/review 已对齐：`.planning/baseline/PUBLIC_SURFACES.md:147`、`.planning/baseline/DEPENDENCY_MATRIX.md:41`、`.planning/baseline/ARCHITECTURE_POLICY.md:35`、`.planning/baseline/VERIFICATION_MATRIX.md:123`、`.planning/reviews/FILE_MATRIX.md:399`、`.planning/reviews/FILE_MATRIX.md:414`、`.planning/reviews/RESIDUAL_LEDGER.md:222`、`.planning/reviews/KILL_LIST.md:177`。
  - Phase 19 专项 meta guards 也已对齐并通过：`tests/meta/test_dependency_guards.py:81`、`tests/meta/test_public_surface_guards.py:79`、`tests/meta/test_public_surface_guards.py:148`、`tests/meta/test_evidence_pack_authority.py:73`。
  - repo-wide governance bundle `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` 现已通过，且 `STATE.md` 的 `v1.2` 执行态保留了 `Phase 17` closeout 历史，不再因旧计数硬编码误报。

## Evidence

- **静态证据**
  - `custom_components/lipro/headless/boot.py` 仅依赖 `core.auth` / `core.protocol`：`custom_components/lipro/headless/boot.py:13`、`custom_components/lipro/headless/boot.py:19`。
  - `headless` package 无 public exports：`custom_components/lipro/headless/__init__.py:8`。
  - boot seam 的生产侧实际消费者仍只有 HA adapter 两处：`custom_components/lipro/config_flow.py:48`、`custom_components/lipro/entry_auth.py:37`；其余消费者为 proof tests / harness。

- **治理文档证据**
  - Phase 19 goal/req 已正确登记：`.planning/ROADMAP.md:341`、`.planning/ROADMAP.md:344`、`.planning/REQUIREMENTS.md:244`。
  - verification matrix 已把 headless boot、proof harness、phase summaries、verification 文档纳入 required artifacts：`.planning/baseline/VERIFICATION_MATRIX.md:123`。
  - governance proof 已明确要求 non-public / non-authority / non-second-root 与 platform shell no-runtime-access：`.planning/baseline/VERIFICATION_MATRIX.md:124`。

- **执行证据（本次终审实跑）**
  - `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check` → 退出码 `0`。
  - `uv run pytest -q tests/core/test_headless_boot.py tests/flows/test_config_flow.py tests/core/test_init.py tests/core/test_token_persistence.py` → `203 passed`。
  - `uv run pytest -q tests/integration/test_headless_consumer_proof.py tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py tests/core/api/test_protocol_contract_matrix.py tests/core/capability/test_registry.py tests/snapshots/test_device_snapshots.py` → `45 passed`。
  - `uv run pytest -q tests/core/test_helpers.py tests/platforms/test_entity_behavior.py` → `41 passed`。
  - `uv run pytest -q tests/core/test_control_plane.py -k runtime_access` → `1 passed`。
  - `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py` → `32 passed`。
  - `uv run pytest -q tests/meta/test_governance_guards.py -k "governance_checker_reports_no_drift or architecture_policy_checker_reports_no_drift or architecture_policy_rule_inventory_is_stable or phase_asset_identity_is_documented_consistently or ci_and_release_workflows_share_governance_and_version_gates"` → `5 passed`。
  - `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` → `38 passed`。

## Risks / Notes

- 当前未发现阻断 `Phase 19` 签核的缺口。
- `STATE.md` 现处于 `v1.2` 执行态；governance guard 已改为要求“保留 `Phase 17` closeout 历史 + 允许后续 phase 前进”，避免后续 `Phase 20+` 再次因旧计数硬编码误报。
- `headless` boot / consumer 仍被严格限制在 proof-only / non-authority / non-second-root 身份；后续 phase 若继续扩展宿主复用，也必须沿同一 host-neutral nucleus 与 formal contracts 前进。
