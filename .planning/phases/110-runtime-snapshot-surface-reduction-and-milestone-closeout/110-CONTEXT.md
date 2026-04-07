# Phase 110: Runtime snapshot surface reduction and milestone closeout - Context

**Gathered:** 2026-03-30
**Status:** Ready for planning
**Source:** `v1.30` active route continuation from `.planning/MILESTONE-CONTEXT.md` + `Phase 109` completion evidence

<domain>
## Phase Boundary

本 phase 只处理 `custom_components/lipro/core/coordinator/runtime/device/snapshot.py` 与 `v1.30` milestone closeout 的最后一段 live continuation：

- 把 snapshot builder 中仍然偏厚的 sourcing / formatting / arbitration seam 继续压回更局部、显式命名的 inward collaborators。
- 保持 `Coordinator` 作为唯一 runtime root；snapshot 侧只允许 inward split，不新增第二 runtime root、不新增 control-facing backdoor、也不新增 public import story。
- 保持现有分页抓取、device filter、mesh group topology enrich、typed refresh failure 与原子拒绝语义不回退。
- 完成 `v1.30` 的 planning / baseline / reviews / docs / focused guards / milestone evidence closeout convergence。

不在本 phase 重开 REST、MQTT transport/runtime 或 anonymous-share manager 热点；这些已分别由 `Phase 107`、`Phase 108`、`Phase 109` 收口。
</domain>

<decisions>
## Locked Decisions

- `snapshot.py` 继续是 runtime snapshot orchestration 的 formal home；decomposition 只允许 inward collaborator split，禁止 outward ownership 迁移。
- `SnapshotBuilder` 的外部行为契约必须保持稳定：分页抓取、filter 过滤、mesh group metadata enrich、identity mapping 与 typed failure boundary 不得退化。
- 新抽出的 helper / support seam 必须是 localized collaborator，而不是新的 package export、public surface 或 second story。
- `Phase 110` 必须同时完成技术收口与治理封板：`ROADMAP / REQUIREMENTS / STATE / baseline / reviews / developer_architecture / focused guards / evidence index` 要讲同一条 `v1.30` closeout 故事。
- closeout 后只允许把 `v1.30` 提升为 archived evidence-ready；不得改写 `v1.29` 的 latest archived baseline truth，直到 closeout 资产显式切换完成。

### the agent's Discretion
- snapshot seam 的具体 helper 边界命名（如 page collection / row normalization / assembly / arbitration）可按现有模式择优收口。
- focused regressions 优先复用 `tests/core/test_device_refresh_snapshot.py`、`tests/core/coordinator/runtime/test_device_runtime.py` 与新增 meta guards；是否拆分额外测试文件由 planner 结合 touched seam 决定。
</decisions>

<canonical_refs>
## Canonical References

- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/MILESTONE-CONTEXT.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `docs/developer_architecture.md`
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py`
- `custom_components/lipro/core/coordinator/runtime/device/snapshot_models.py`
- `custom_components/lipro/core/coordinator/runtime/device/filter.py`
- `custom_components/lipro/core/coordinator/runtime/device_runtime.py`
- `tests/core/test_device_refresh_snapshot.py`
- `tests/core/coordinator/runtime/test_device_runtime.py`
- `tests/meta/test_governance_route_handoff_smoke.py`
- `tests/meta/governance_followup_route_current_milestones.py`
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `SnapshotBuilder._fetch_device_page()` 已把 canonical page fetch 与 page boundary 错误隔离成独立方法，可继续下沉 pagination / payload arbitration 细节。
- `_SnapshotAssembly` 已提供装配期桶结构，适合作为 assembly/seam 继续拆薄时的边界锚点。
- `snapshot_models.py` 已承载 typed snapshot result / refresh rejection models，避免 helper 抽出后把错误语义退回裸异常。
- `tests/core/test_device_refresh_snapshot.py` 已覆盖分页、filter、type categorization、parse rejection 与 mesh-group rejection，适合作为 Phase 110 focused regression backbone。

### Established Patterns
- 当前里程碑遵循“formal home 保持 outward story，support/helper 只承接 inward mechanics”的北极星法则。
- Phase 107/108/109 已证明：热点收口要同步 planning/baseline/reviews/docs/tests，不允许只改代码不改治理真源。
- runtime plane 继续要求 `Coordinator` 单根；任何 snapshot helper 都不能反向变成 runtime public surface。

### Integration Points
- `device_runtime.py` 继续消费 snapshot builder 的刷新结果与 typed failure 语义。
- governance closeout 需要与 `.planning/reviews/V1_29_EVIDENCE_INDEX.md` 的 predecessor truth 保持可审计衔接，并为 `v1.30` 生成新 closeout/evidence 链。
</code_context>

<specifics>
## Specific Ideas

- 优先延续近三 phase 的 inward decomposition 手法：先拆机械流程与命名 seams，再用 focused guards 冻结 route/home truth。
- `Phase 110` 不应把 milestone closeout 变成纯文档收尾；snapshot hotspot 与 governance closeout 必须同一 phase 完成，避免再次留下 non-blocking residual。
</specifics>

<deferred>
## Deferred Ideas

- 若后续还出现新的 runtime snapshot outward API 诉求，应作为后续 phase / backlog 单独立项，而不是在本 phase 顺手扩 scope。
- 与 `v1.30` closeout 无关的额外 repo-wide polishing、历史 phase 文案美化或跨里程碑重写，不属于本 phase。
</deferred>

---

*Phase: 110-runtime-snapshot-surface-reduction-and-milestone-closeout*
*Context gathered: 2026-03-30*
