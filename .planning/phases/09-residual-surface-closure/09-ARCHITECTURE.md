# Phase 9 Architecture

## Architectural Goal

把审查报告中已登记的 protocol/runtime residual surfaces 收束回北极星正式主链：
- protocol root 的 contract 必须显式、可裁决；
- compat / concrete transport 只能存在于显式过渡 seam；
- runtime 对外只暴露只读 view 或正式 service；
- outlet power 通过正式 primitive 承载，而不是 `extra_data` 旁写。

## Single Truth Chain

```text
docs/NORTH_STAR_TARGET_ARCHITECTURE.md
  -> protocol/runtime formal surfaces
     - LiproProtocolFacade (explicit root contract)
     - Coordinator service/read-only surfaces
     - outlet power formal primitive
  -> compat quarantine
     - explicit compat aliases / test seams only
  -> governance truth
     - PUBLIC_SURFACES.md
     - VERIFICATION_MATRIX.md
     - RESIDUAL_LEDGER.md
     - KILL_LIST.md
     - FILE_MATRIX.md
  -> automated proof
     - protocol/coordinator/power targeted tests
     - meta public-surface / governance guards
```

裁决：
- formal root 只能由显式 contract 定义；
- compat seam 不能反向定义 public truth；
- runtime mutable state 只能由 coordinator internals 持有；
- supplemental power state 必须拥有正式 home；
- governance docs 与 guards 只记录/裁决正式真相，不制造第二套实现。

## Formal Components

### 1. Explicit protocol surface

正式职责：
- `LiproProtocolFacade` 只暴露显式 root-level contract；
- `rest` / `mqtt` child façade 通过显式属性访问；
- compat forwarding 若仍存在，必须待在显式 compat home，而不是 `__getattr__` 魔法里。

### 2. Compat quarantine

正式职责：
- legacy names 可以暂存，但必须有显式 owner、delete gate 与 test scope；
- `raw_client` 若仍保留，只能服务于 compat/test seam；
- 根模块/包级导出不再继续扩大 compat 语义。

### 3. Runtime read-only surface

正式职责：
- `Coordinator` 持有 live mutable registry；
- 对外访问通过 read-only mapping 或 service contract；
- platform/helpers/diagnostics 仍能稳定读取，但不能经 public contract 直接改写内部 state。

### 4. Outlet power formal primitive

正式职责：
- coordinator/runtime 把 outlet power 写入正式 primitive；
- sensor / diagnostics / helpers 从同一 primitive 读取；
- 若需要桥接旧读取路径，只能是过渡兼容层，并必须登记 delete gate。

## Cross-Phase Arbitration

### `07.5`

`09` 不重做 governance closeout 基础定义；只回写 residual/delete gate 的新增收口事实。

### `08`

`09` 不改 evidence pack truth chain；只在 public surface / residual / power truth 变更时同步其 governance pointers。

### `09`

`09` 只拥有 residual surface closure：
- protocol root/naming 收窄
- compat seam 压缩
- runtime read-only access
- outlet power formal primitive
- governance delete gate 与 guard 回写

## Deliverables

- explicit protocol/public surface contract
- read-only runtime device access contract
- outlet power formal primitive + migrated readers
- updated governance ledgers and guard evidence
- execution-ready `09-01/02/03` plans

## Non-Goals

- 不新增第二套 protocol/runtime 实现
- 不在本 phase 扩大 `Phase 8` exporter/tooling 责任
- 不为了一次性“删干净”而牺牲兼容回归稳定性
- 不把 `extra_data` 以外的任意临时旁写再次合法化
