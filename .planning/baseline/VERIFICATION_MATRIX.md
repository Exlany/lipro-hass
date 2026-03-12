# Verification Matrix

**Purpose:** 建立 requirement → artifact → test → doc → phase 的统一验证闭环。
**Status:** Baseline reference
**Updated:** 2026-03-12

## Requirement-to-Artifact Mapping

| Requirement Group | Primary Artifacts | Verification Surfaces | Phase |
|-------------------|------------------|------------------------|-------|
| `BASE-*` | baseline asset pack | document review + seed guards | 1.5 |
| `PROT-*` | protocol facades, auth/policy/normalizers, fixtures | contract tests + snapshot + integration | 1 / 2 / 2.5 |
| `CTRL-*` | control surfaces, flows, diagnostics/health/services | flow tests + diagnostics tests + redaction checks | 3 |
| `DOM-*` | capability registry/snapshot, projections | domain tests + entity/platform tests + snapshots | 4 |
| `RUN-*` | coordinator/runtime/services | runtime tests + invariants + integration | 5 |
| `ASSR-*` | guards, telemetry hooks, CI gates | meta tests + CI + coverage + verification review | 1.5 / 6 |
| `INTG-*` | external contracts, fixtures, authority rules | targeted contract tests + fixture audits | 2.6 |
| `GOV-*` | reviews docs, cleanup reports, final audit | file matrix review + residual/kill review + summary | 7 |

## Phase Exit Checklist

| Phase | Must Update | Must Verify |
|-------|-------------|-------------|
| 1 | fixtures, canonical snapshots, immutable constraints, governance closeout | contract matrix + canonical snapshot suite pass |
| 1.5 | all baseline assets | seed guards and doc alignment |
| 2 | protocol slice design, residual/kill updates | contract tests + new public surface checks |
| 2.5 | protocol root docs, residual/kill updates | shared contract + mqtt/protocol integration checks |
| 2.6 | authority matrix, boundary docs, fixtures | external boundary drift checks |
| 3 | control surface docs + reviews | flows/diagnostics/services matrix |
| 4 | capability docs + file matrix | domain/entity/platform verification |
| 5 | runtime invariant docs + residual cleanup | runtime invariant suite |
| 6 | assurance docs + CI gates | meta guards + CI proof |
| 7 | final file matrix + residual + kill list + report | full governance review |

## Governance Output Contract

每个 phase 完成时至少确认以下产物之一发生了有意义更新：

- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`

若无更新，也必须在 phase 总结中明确写出“为何无变化”。

## Phase 01 Closeout Status

- `01-01` 锁定了三条首批协议边界的 targeted contract fixtures 与 tests。
- `01-02` 为同一 baseline 增补 canonical snapshots 与 `01-IMMUTABLE-CONSTRAINTS.md`，使 Phase 1 exit contract 不再只依赖测试断言。
- 本阶段的最低执行证据为 `uv run pytest tests/core/api/test_protocol_contract_matrix.py tests/snapshots/test_api_snapshots.py -q`。
- Phase 1.5 可以直接消费这些 baseline artifacts；Phase 2 必须把它们当作 demixin / façade 重构前的输入边界。

---
*Used by: phase planning, verification, and final audit closure*
