# Phase 114: Open-source reachability honesty and security-surface normalization - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning

<domain>
## Phase Boundary

本阶段只处理 `OSS-14` 与 `SEC-09`：把仓库的 **public-facing metadata / docs / support / security / continuity wording** 收口成一套真实、可验证、不开第二真源的叙事。

本阶段优先目标：
- 统一 `README(.md/.zh)`、`docs/README.md`、`SUPPORT.md`、`SECURITY.md`、issue/contact links、`pyproject.toml`、`custom_components/lipro/manifest.json` 的 access-mode truth；
- 明确区分 truly reachable public surfaces、access-gated GitHub/private surfaces、maintainer-only surfaces；
- 对不存在的 guaranteed non-GitHub private fallback 保持 blocker honesty，不伪造“已提供的私密安全渠道”；
- 统一匿名分享 / developer diagnostics / redaction / debug-mode developer services 的术语与 disclosure 强度；
- 为上述 truth 增加 `Phase 114` machine-checkable guards，并修平当前 planning route/progress 表中的漂移。

本阶段**不**处理：
- 改变仓库 private/public 可见性；
- 凭空创造 delegate / backup maintainer / public mirror / repo 外安全邮箱；
- 扩张 public feature surface、引入新 root、或把 maintainer-only appendix 回流为 public first hop；
- 借 public 文案修复去覆盖真实外部 blocker。

</domain>

<decisions>
## Implementation Decisions

### Public/access-mode truth
- **D-01:** 所有 public-facing docs 与 metadata 只能陈述当前真实可达 surface；GitHub Issues / Discussions / Releases / Security UI 若取决于访问模式，必须明确标注为 conditional / access-gated，而不是默认公开入口。
- **D-02:** `docs/README.md` 继续是 canonical docs map；`README.md` / `README_zh.md` 继续是 public first hop；`docs/MAINTAINER_RELEASE_RUNBOOK.md` 继续是 maintainer-only appendix，不得回流到 public first-hop 主链。
- **D-03:** `manifest.json` / `pyproject.toml` 若继续暴露 docs/support/security URLs，必须与 docs-first/access-mode truth 一致；不能新增更强的“公开 issue tracker / guaranteed security route”暗示。

### Security / privacy semantics
- **D-04:** 匿名分享相关文案不得把 pseudonymous / sanitized payload 夸大为强匿名；需诚实说明仍保留稳定 `installation_id`、`iot_name` 等诊断标识。
- **D-05:** `remember password` 文案必须说明本地保存的是 hashed-login credential-equivalent secret，而不是单纯“不可逆校验摘要”。
- **D-06:** `get_developer_report` / `submit_developer_feedback` / debug services 的 wording 必须明确其 disclosure boundary：本地部分脱敏、上传时进一步 sanitize、且仅在 debug-mode runtime entry 存在时才会注册相关 developer services。
- **D-07:** `flow/credentials.py` 的输入校验描述不得使用 security-theater 语言；只陈述本地格式/边界校验的真实作用。密码控制字符策略若可安全收紧，应与文档 truth 一并收紧。

### Governance / machine truth
- **D-08:** `Phase 114` 必须新增 focused meta guard，冻结 access-mode truth、fallback honesty、privacy terminology、developer service gating 与 `scripts/lint` 文案 truth；不能只改文档不补 guard。
- **D-09:** 本阶段允许修平 `ROADMAP.md` / `STATE.md` 中已存在的 progress table 脏数据、以及 related governance truth drift，但不得改写 authority hierarchy 或重开新 route family。
- **D-10:** 若 `AUTHORITY_MATRIX` 与 current governance tests 对 `.planning/MILESTONES.md` 的角色仍冲突，可在 audit 中登记并最小修平表述；但不得为了局部测试便利引入第二条 live selector story。

### External blockers (must stay explicit)
- **D-11:** 若仓内不存在 guaranteed non-GitHub private disclosure fallback，就必须继续在 `SECURITY.md` / planning truth 中明确写“没有”，保持 blocker 状态。
- **D-12:** 若 `.github/CODEOWNERS` 中没有 documented delegate / backup maintainer，就不得在 SUPPORT/SECURITY/README 中暗示 hidden delegate、hidden custody transfer、或未记录的 emergency path。

### the agent's Discretion
- 可决定 docs wording 的具体压缩方式，只要 public first hop 更短、更诚实，且 bilingual pairing 不漂移。
- 可决定 `manifest.json` / `pyproject.toml` 是否保留现有 URL 形态或改为更弱语义的 docs-first landing route，只要 machine truth 与 human docs 一致。
- 可决定 `Phase 114` guards 的拆分颗粒度，只要至少覆盖 access-mode truth、security fallback honesty、privacy/dev-service wording、route/progress drift。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Active-route truth
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `tests/meta/governance_current_truth.py`

### Governance / docs / authority truth
- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/README.md`
- `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/AUTHORITY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/baseline/GOVERNANCE_REGISTRY.json`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- `.planning/codebase/TESTING.md`

### Public / metadata / support surfaces under direct consideration
- `README.md`
- `README_zh.md`
- `CHANGELOG.md`
- `SUPPORT.md`
- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `custom_components/lipro/manifest.json`
- `pyproject.toml`
- `.github/ISSUE_TEMPLATE/config.yml`
- `.github/ISSUE_TEMPLATE/bug.yml`
- `.github/pull_request_template.md`
- `.github/CODEOWNERS`

### Service/privacy/security semantics under direct consideration
- `custom_components/lipro/services.yaml`
- `custom_components/lipro/control/service_registry.py`
- `custom_components/lipro/flow/credentials.py`
- `custom_components/lipro/flow/login.py`
- `custom_components/lipro/core/anonymous_share/models.py`
- `custom_components/lipro/core/anonymous_share/report_builder.py`
- `custom_components/lipro/core/anonymous_share/sanitize.py`
- `custom_components/lipro/control/redaction.py`

### Existing guards / predecessors
- `tests/meta/test_phase75_access_mode_honesty_guards.py`
- `tests/meta/test_governance_release_docs.py`
- `tests/meta/test_governance_release_contract.py`
- `tests/meta/test_governance_release_continuity.py`
- `tests/meta/test_governance_bootstrap_smoke.py`
- `tests/meta/test_version_sync.py`
- `tests/meta/toolchain_truth_docs_fast_path.py`
- `tests/services/test_services_registry.py`
- `tests/core/anonymous_share/test_sanitize.py`
- `tests/core/test_diagnostics_redaction.py`
- `tests/core/test_anonymous_share_storage.py`

</canonical_refs>

<code_context>
## Reusable Code / Current Patterns

- `README(.md/.zh)` + `docs/README.md` 已经具备 docs-first / access-mode honesty 的基本骨架；Phase 114 更像收敛 truth，而不是从零设计。
- `SECURITY.md` / `SUPPORT.md` 已明确 single-maintainer / no-documented-delegate truth；问题在于 fallback honesty 与 wording 一致性，而不是缺少 continuity 叙事。
- `service_registry.py` 已把 developer services 与 public services 分离，并以 `has_debug_mode_runtime_entry()` 做注册门槛；docs 只需把这一事实说清楚。
- `anonymous_share` / `developer_feedback` payload 已有 sanitize / redaction code 与 fixture/test coverage；Phase 114 重点是 disclosure terminology honesty，而不是重写 payload model。
- `tests/meta/test_phase113_hotspot_assurance_guards.py` 为本 phase 新 guard 提供直接模板：line budgets → 可替换为 truth / wording / route assertions。

</code_context>

<specifics>
## Specific Ideas

- 114-01 可聚焦 public/security/privacy wording：修正 anonymous-share / developer-report / password-hash / debug-mode gating / lint help text 的语义强度。
- 114-02 可聚焦 metadata/governance truth：同步 `manifest.json` / `pyproject.toml` / issue links / registry / meta tests，并处理当前 `ROADMAP` / `STATE` 的 progress 漂移。
- 114-03 可作为 closeout：补 Phase 114 verification matrix / guards / summary / audit，并把 route 推进到 phase complete / milestone-complete-ready。

</specifics>

<deferred>
## Deferred Ideas

- 真正的 public mirror / public HACS / public Releases / Security UI 可达性。
- repo 外稳定私密安全邮箱或 guaranteed non-GitHub disclosure channel。
- 真实 delegate / backup maintainer / custody transfer落地。
- `.planning/codebase` freshness、planning link audit、promoted assets 第二真源等更大范围治理清算（若本 phase 无法一并收口，则保留为审计延后项）。

</deferred>
