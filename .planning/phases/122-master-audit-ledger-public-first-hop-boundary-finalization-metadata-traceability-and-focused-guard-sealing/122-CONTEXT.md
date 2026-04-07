# Phase 122: master audit ledger, public first-hop boundary finalization, metadata traceability, and focused guard sealing - Context

**Gathered:** 2026-04-01
**Status:** planning-ready
**Milestone:** `v1.35 Master Audit Closure, Public Surface Finalization & Release Traceability`
**Current route:** `v1.35 active milestone route / starting from latest archived baseline = v1.34`
**Requirements basket:** `AUD-05`, `DOC-12`, `OSS-16`, `GOV-81`, `TST-44`
**Default next command:** `$gsd-execute-phase 122`

<domain>
## Phase 目标

本 phase 的目标不是再开新功能，而是把 `v1.35` 已经确认的终审结论压回一条可执行、可追溯、可守卫的正式主线：

- 为全仓 Python / docs / config / governance 残留建立**单一 master audit ledger**，不再依赖 scattered phase folklore；
- 把 `README.md`、`README_zh.md`、`docs/README.md`、`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md` 与 maintainer appendix family 的边界讲清楚，让 public first-hop 在首屏清晰可见；
- 让 `pyproject.toml`、`custom_components/lipro/manifest.json`、`hacs.json` 与 release-facing docs 的 metadata/provenance 回到 semver/tagged-release truth；
- 用 focused guards 冻结 audit ledger completeness、public first-hop vs appendix boundary、metadata traceability 与 active route truth。
</domain>

<evidence>
## 输入证据

- 路线与需求真源：`AGENTS.md`、`docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md`
- archived baseline：`.planning/v1.34-MILESTONE-AUDIT.md`、`.planning/reviews/V1_34_EVIDENCE_INDEX.md`
- 当前真实改动切片：`SUPPORT.md`、`SECURITY.md`、`docs/README.md`、`pyproject.toml`、`custom_components/lipro/manifest.json`、`tests/meta/test_version_sync.py`、`tests/meta/test_phase75_access_mode_honesty_guards.py`、`tests/meta/toolchain_truth_docs_fast_path.py`
- 边界与投影相关文档：`README.md`、`README_zh.md`、`CONTRIBUTING.md`、`docs/TROUBLESHOOTING.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`.planning/baseline/GOVERNANCE_REGISTRY.json`
- 审阅结论：仓库整体架构健康；剩余主问题集中在 public first-hop / maintainer appendix 边界、metadata traceability、治理/测试偏重，以及缺少单一 audit ledger
</evidence>

<issues>
## 已知问题

- repo-wide 审阅结论仍分散在 milestone audit、phase 资产、docs 说明与测试断言中，尚无单一 audit ledger 落表真源
- public first-hop 虽已初步收敛到 docs-first，但 `README* / CONTRIBUTING / SUPPORT / SECURITY / runbook` 之间仍需要更明确的首屏分层，防止 maintainer appendix 抢叙事
- metadata traceability 已在部分文件落地，但仍需把 `pyproject.toml`、`manifest.json`、`hacs.json` 与 release-facing docs 讲成同一条 tagged-release provenance 故事
- 现有 guards 偏分散：version sync、access-mode honesty、docs fast path 各自覆盖一段 truth，尚未形成以 `v1.35` 为中心的 focused sealing
- `PROJECT / ROADMAP / REQUIREMENTS / STATE` 已承认 `v1.35` active route，但还需要与 ledger home、3-plan 拆分、guard scope 完整对齐
</issues>

<non_goals>
## 非目标

- 不重开 `v1.34` 已归档的 runtime / protocol / control 架构收敛工作
- 不发明不存在的 public mirror、non-GitHub private fallback、delegate identity 或第二治理根
- 不更改 package semver、Home Assistant minimum version、north-star formal homes 或 release gate 基线
- 不把 `.planning/phases/**` 执行痕迹误提升为 public release doc set
</non_goals>

<risks>
## 风险

- 若 ledger home 选择不清，会再次形成“milestone audit + phase folklore + tests”三套并行故事
- 若 public-first cleanup 只挪 prose、不校正 appendix 深链与 registry 投影，后续很容易再次漂移
- 若 metadata traceability 只校验路径后缀、不冻结 tag 语义，下一次版本 bump 仍可能回退到 `main` 或 milestone-labeled provenance
- 若 focused guards 过度绑定具体措辞，会让后续文案清理困难；但过松又挡不住 drift
</risks>

<validation_surface>
## 建议验证面

- route truth / ledger completeness：`uv run pytest tests/meta/test_governance_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_followup_route.py tests/meta/governance_current_truth.py tests/meta/governance_followup_route_current_milestones.py -q`
- public first-hop / appendix boundary：`uv run pytest tests/meta/test_phase75_access_mode_honesty_guards.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py -q`
- metadata traceability / version sync：`uv run pytest tests/meta/test_version_sync.py tests/meta/test_phase114_open_source_surface_honesty_guards.py -q`
- governance/file-matrix consistency：`uv run python scripts/check_file_matrix.py --check`
</validation_surface>
