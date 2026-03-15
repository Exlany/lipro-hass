# TESTING
> Refreshed: `2026-03-15`
> Scope: `tests/**/*.py`、CI/pre-commit、fixtures/readmes、governance baselines 中的测试策略与质量门禁
> Derived collaboration map: 本文件是受约束的协作图谱 / 派生视图，仅用于导航、协作与局部审阅。
> Authority: 若与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 或 `docs/developer_architecture.md` 冲突，以后者为准；本图谱必须同步回写或标记为过时。

## 1. Mapping Sources

本次测试映射综合了以下真源：

- `AGENTS.md`
- `pyproject.toml`
- `.pre-commit-config.yaml`
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `README.md`
- `CONTRIBUTING.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`
- `.planning/baseline/ARCHITECTURE_POLICY.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `tests/**/*.py`
- `tests/fixtures/**/README.md`

## 2. Executive Snapshot

- 测试栈完整：`pytest`、`pytest-asyncio`、`pytest-cov`、`pytest-homeassistant-custom-component`、`pytest-benchmark`、`syrupy`、`mypy`、`xdist` 全部进入 dev 依赖。证据：`pyproject.toml:33`。
- CI 把质量拆成 `lint`、`governance`、`security`、`test`、`benchmark`、`validate` 六道门，release 先复用 CI，再做版本校验与打包。证据：`.github/workflows/ci.yml:22`, `.github/workflows/release.yml:25`, `tests/meta/test_governance_guards.py:185`。
- 当前仓库共有 `154` 个 `test_*.py` 文件；其中 `14` 个 meta guard、`4` 个 integration、`4` 个 benchmark、`4` 个 snapshot 文件；另有 `5` 个 fixture family readme 维护 authority/用途说明。
- Coverage gate 是硬门槛：主测试 job 以 `95%` 为下限，快照单独运行，之后再跑 coverage diff 与 refactor smoke。证据：`.github/workflows/ci.yml:177`, `CONTRIBUTING.md:94`。

## 3. 测试分层图谱

| 分层 | 目录 | 角色 | 证据 |
|---|---|---|---|
| 核心单测 | `tests/core/**` | 运行时、协议、设备域、MQTT、OTA、telemetry 等局部行为验证 | `docs/developer_architecture.md:513`, `tests/core/test_exceptions.py:18`, `tests/core/api/test_protocol_contract_matrix.py:1` |
| 实体/平台层 | `tests/entities/**`, `tests/platforms/**` | HA projection、描述符、平台规则与边界行为 | `docs/developer_architecture.md:516` |
| Flow / 生命周期 | `tests/flows/**` | `config_flow`、reauth、reconfigure、options 流程 | `docs/developer_architecture.md:517`, `CONTRIBUTING.md:85` |
| 服务层 | `tests/services/**` | service router、registry、diagnostics/share 等控制面契约 | `AGENTS.md:243`, `tests/services/test_service_resilience.py:264` |
| Integration | `tests/integration/**` | replay harness、MQTT coordinator、AI evidence pack 等 assurance mainline | `tests/integration/test_protocol_replay_harness.py:46`, `tests/integration/test_ai_debug_evidence_pack.py:21`, `tests/integration/test_mqtt_coordinator_integration.py:143` |
| Snapshot | `tests/snapshots/**` | 稳定输出面快照：API contract、device facade、coordinator public surface | `tests/snapshots/test_api_snapshots.py:42`, `tests/snapshots/test_coordinator_public_snapshots.py:13`, `tests/snapshots/test_device_snapshots.py:34` |
| Benchmark | `tests/benchmarks/**` | 性能 smoke + correctness 守护，覆盖 command/device refresh/MQTT/coordinator hotspots | `tests/benchmarks/test_command_benchmark.py:8`, `tests/benchmarks/test_device_refresh_benchmark.py:8`, `tests/benchmarks/test_mqtt_benchmark.py:10`, `tests/benchmarks/test_coordinator_performance.py:55` |
| Meta guards | `tests/meta/**` | 架构依赖、public surface、governance、版本同步、外部边界 authority | `tests/meta/test_dependency_guards.py:19`, `tests/meta/test_public_surface_guards.py:19`, `tests/meta/test_governance_guards.py:122` |
| Harness / fixtures | `tests/harness/**`, `tests/fixtures/**` | replay/evidence pack 基础设施与正式测试真源 | `tests/fixtures/api_contracts/README.md:5`, `tests/fixtures/protocol_replay/README.md:7`, `tests/fixtures/evidence_pack/README.md:3` |

## 4. Fixture 与测试数据策略

- `tests/conftest.py` 是主 fixture 入口：`make_device()` 统一生成 `LiproDevice`，`_CoordinatorDouble` 提供只读设备表面与 protocol doubles，避免每个测试文件各造一套 coordinator fake。证据：`tests/conftest.py:76`, `tests/conftest.py:113`。
- `tests/conftest_shared.py` 承接 API-shaped payload builder 与 runtime helper，例如 `make_api_device()`、`make_device_page()`、`refresh_and_sync_devices()`。证据：`tests/conftest_shared.py:15`, `tests/conftest_shared.py:61`, `tests/conftest_shared.py:73`。
- fixture 目录不是“素材堆”，而是 authority contract：
  - `api_contracts/` 保存高漂移 REST 边界金样本。证据：`tests/fixtures/api_contracts/README.md:5`。
  - `protocol_boundary/` 保存 replay-ready decoder family fixtures。证据：`tests/fixtures/protocol_boundary/README.md:5`。
  - `protocol_replay/` 只记录 scenario manifest，authority payload 必须引用正式真源，不得复制第二份 payload。证据：`tests/fixtures/protocol_replay/README.md:7`。
  - `external_boundaries/` 保存 support/share/firmware 等外部边界样本。证据：`tests/fixtures/external_boundaries/README.md:1`。
  - `evidence_pack/` 规定 AI evidence pack 只能 pull 正式真源，且严禁泄露 token / secret / `password_hash`。证据：`tests/fixtures/evidence_pack/README.md:3`。
- 这套 fixture/readme 结构与北极星“authority 单一真源”一致，避免 contract、replay、diagnostics 各自维护分叉样本。证据：`AGENTS.md:126`, `.planning/baseline/ARCHITECTURE_POLICY.md:21`, `tests/core/api/test_protocol_contract_matrix.py:345`。

## 5. Meta Guards 与治理门禁

- dependency guards 从 baseline 规则表派生，并用 AST/import 扫描阻止 entity/control 绕过正式边界。证据：`tests/meta/test_dependency_guards.py:19`, `.planning/baseline/ARCHITECTURE_POLICY.md:31`。
- public-surface guards 把 allowed/forbidden exports 固化为断言，防止 compat shell、backdoor property、legacy naming 回流。证据：`tests/meta/test_public_surface_guards.py:19`, `.planning/baseline/ARCHITECTURE_POLICY.md:48`。
- governance guards 同时校验 file matrix、architecture policy checker、phase asset identity、CI/release 一致性、contributor contract 与 security disclosure。证据：`tests/meta/test_governance_guards.py:122`, `tests/meta/test_governance_guards.py:160`, `tests/meta/test_governance_guards.py:185`, `tests/meta/test_governance_guards.py:213`。
- pre-push 不是跑全量，而是挑“最容易把治理打穿”的诊断三测 + governance 三测。证据：`.pre-commit-config.yaml:31`, `.pre-commit-config.yaml:43`, `CONTRIBUTING.md:80`。
- CI governance job 先跑 policy/file-matrix checker，再跑 meta guards，形成 fail-fast。证据：`.github/workflows/ci.yml:61`, `.github/workflows/ci.yml:82`, `.planning/baseline/ARCHITECTURE_POLICY.md:38`。

## 6. Snapshot / Integration / Benchmark 策略

### 6.1 Snapshot

- 快照故意做窄而稳：当前 `tests/snapshots/` 只有 `4` 个文件、`5` 个测试，用来锁定 API typed payload、protocol contract baseline、device facade 与 coordinator public snapshot。证据：`tests/snapshots/test_api_snapshots.py:42`, `tests/snapshots/test_api_snapshots.py:67`, `tests/snapshots/test_device_facade_snapshot.py:10`, `tests/snapshots/test_coordinator_public_snapshots.py:13`。
- 快照不承担“覆盖一切”的职责，而是服务于高价值、序列化稳定的 public surfaces。证据：`.github/workflows/ci.yml:188`。

### 6.2 Integration

- integration 层不是打真实云，而是验证 formal path 是否串起来：replay harness 走 `LiproProtocolFacade`/boundary path，AI evidence pack 走 exporter/harness formal truth，MQTT coordinator 走 mocked transport + real coordinator wiring。证据：`tests/integration/test_protocol_replay_harness.py:46`, `tests/integration/test_ai_debug_evidence_pack.py:21`, `tests/integration/test_mqtt_coordinator_integration.py:143`, `tests/fixtures/protocol_replay/README.md:9`。
- replay harness 不只验 canonical output，还校验 telemetry alignment 与 structured run summary。证据：`tests/integration/test_protocol_replay_harness.py:74`, `tests/integration/test_protocol_replay_harness.py:94`。

### 6.3 Benchmark

- benchmark 覆盖 command classification、device property update、MQTT message processing、identity index / device runtime hotspot，并且大多附带 correctness assertion。证据：`tests/benchmarks/test_command_benchmark.py:8`, `tests/benchmarks/test_device_refresh_benchmark.py:8`, `tests/benchmarks/test_mqtt_benchmark.py:10`, `tests/benchmarks/test_coordinator_performance.py:55`。
- benchmark job 默认只在 `schedule` / `workflow_dispatch` 运行，不阻塞普通 PR。证据：`.github/workflows/ci.yml:206`, `CONTRIBUTING.md:98`。

## 7. Bright Spots

- **CI / docs / pre-commit 三方口径一致**：贡献文档、pre-push 钩子、CI workflow、governance guards 写的是同一套命令组与门禁顺序。证据：`.pre-commit-config.yaml:31`, `.github/workflows/ci.yml:61`, `CONTRIBUTING.md:89`, `tests/meta/test_governance_guards.py:213`。
- **架构治理已经测试化**：不是“写了 ADR 就算完成”，而是 `dependency/public-surface/governance/version-sync` 都能在 PR 上自动阻断回退。证据：`tests/meta/test_dependency_guards.py:53`, `tests/meta/test_public_surface_guards.py:42`, `tests/meta/test_governance_guards.py:127`, `.github/workflows/ci.yml:88`。
- **fixture authority 意识很强**：contract / replay / evidence pack / external boundary 都有 README 解释“为什么存在、谁是 owner、不能复制什么”。证据：`tests/fixtures/api_contracts/README.md:30`, `tests/fixtures/protocol_replay/README.md:7`, `tests/fixtures/evidence_pack/README.md:3`。
- **诊断与脱敏回归被前移到 pre-push**：相比只靠全量 CI，这能更早发现支持面泄密或快照漂移。证据：`.pre-commit-config.yaml:31`, `tests/core/test_diagnostics.py:204`, `tests/core/test_diagnostics.py:390`。
- **coverage gate 很硬**：主测试 job 把 `95%` 作为底线，并额外跑 coverage diff 与 refactor smoke，减少“大改后回归网破洞”的概率。证据：`.github/workflows/ci.yml:177`, `.github/workflows/ci.yml:191`, `.github/workflows/ci.yml:194`。

## 8. Gaps 与改进空间

- **marker registry 与实际切分脱节**：`pyproject.toml` 声明了 `github` / `integration` / `slow` markers，但当前跟踪到的 `test_*.py` 文件没有使用这些 marker；套件切分主要靠目录，而不是 marker 选择。证据：`pyproject.toml:73`，以及本次仓库扫描结果。
- **benchmark 只有执行，没有阈值**：CI 只在 schedule/manual 跑 benchmark，并输出 `.benchmarks/benchmark.json`；没有历史基线、回归阈值或 PR 级别性能门槛。证据：`.github/workflows/ci.yml:206`, `.github/workflows/ci.yml:228`。
- **coverage diff 目前更像第二个最低线检查**：CI 调用 `scripts/coverage_diff.py` 时只传 `--minimum 95`，没有 baseline 文件，因此不会真正比较“相对退步”。证据：`.github/workflows/ci.yml:191`。
- **工具依赖有前瞻性，但尚未 fully exploited**：`pytest-mypy-plugins` 与 `pytest-xdist` 已进入 dev 依赖，但仓库内没有对应 type-checking plugin case，也未在 CI 中并行运行测试。证据：`pyproject.toml:45`, `pyproject.toml:46`, `.github/workflows/ci.yml:177`。
- **快照覆盖仍然很克制**：这有利于稳定，但 control-plane 输出、服务响应体、evidence-pack markdown index 等仍主要依赖常规断言，而非 snapshot 守护。证据：`tests/snapshots/test_api_snapshots.py:42`, `tests/integration/test_ai_debug_evidence_pack.py:21`。

## 9. Current Minimal Suite Guidance

- Protocol / API / boundary 变更：先跑 `tests/core/api/**` + `tests/snapshots/test_api_snapshots.py`。证据：`AGENTS.md:233`, `docs/developer_architecture.md:513`。
- Unified protocol root / MQTT 变更：加跑 `tests/core/mqtt/**` + `tests/integration/test_mqtt_coordinator_integration.py`。证据：`AGENTS.md:236`, `docs/developer_architecture.md:515`。
- Control-plane / flow / services 变更：至少覆盖 `tests/core/test_control_plane.py`、`tests/core/test_init.py`、`tests/core/test_diagnostics.py`、`tests/core/test_system_health.py`、`tests/services/**`、`tests/flows/**`。证据：`AGENTS.md:243`, `CONTRIBUTING.md:85`。
- 架构/治理/public-surface 变更：先跑 meta guards，再跑全量。证据：`AGENTS.md:246`, `CONTRIBUTING.md:95`, `.github/workflows/ci.yml:88`。
- 性能相关改动：只在性能是需求的一部分时追加 benchmark；当前 benchmark 不是默认 PR gate。证据：`CONTRIBUTING.md:98`, `.github/workflows/ci.yml:206`。
