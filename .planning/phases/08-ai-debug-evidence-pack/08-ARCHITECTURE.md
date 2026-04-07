# Phase 8 Architecture

## Architectural Goal

把 `07.3 telemetry exporter`、`07.4 replay harness`、`07.5 governance closeout` 的正式产物收敛成一份 AI Debug Evidence Pack：稳定、可追溯、脱敏正确、默认 JSON 输出。

## Single Truth Chain

```text
formal sources
  - telemetry exporter views (07.3)
  - replay run summaries (07.4)
  - V1_1_EVIDENCE_INDEX.md + governance matrices (07.5)
  - boundary inventory / authority docs
-> evidence source adapters
-> pseudo-id / redaction policy
-> evidence pack schema
-> outputs
   - ai_debug_evidence_pack.json
   - ai_debug_evidence_pack.index.md
```

裁决：
- evidence pack 只 pull 正式真源；
- source adapters 只做读取/整合/字段映射；
- redaction / pseudo-id 只消费既有正式政策，不自造第二套真相；
- outputs 是 assurance artifacts，不进入 runtime 主链。

## Formal Components

### 1. `scripts/export_ai_debug_evidence_pack.py`

正式职责：
- 作为 evidence pack 的唯一导出入口；
- 从正式 source adapters 拉取数据；
- 生成 JSON pack 与 markdown index；
- 不获取 coordinator / protocol private control 权限。

### 2. `tests/harness/evidence_pack/schema.py`

正式职责：
- 定义 pack version、top-level sections、field authority trace 与 required/optional fields；
- 保持 schema 稳定、可版本化、backend-swappable。

### 3. `tests/harness/evidence_pack/sources.py`

正式职责：
- 读取 `07.3/07.4/07.5` 正式输出；
- 对每个 section 保留 source / authority metadata；
- 禁止从未登记临时路径“顺手捞数据”。

### 4. `tests/harness/evidence_pack/redaction.py`

正式职责：
- 对 pack 做最终 source-level denylist / pseudo-id transform；
- 允许真实时间戳；
- 保证 `entry_ref` / `device_ref` 等仅报告内稳定、跨报告不可关联；
- 明确禁止凭证等价物出现。

### 5. `tests/harness/evidence_pack/collector.py`

正式职责：
- 协调 source adapters、schema、redaction；
- 生成稳定 pack structure；
- 不承担 governance closeout 仲裁。

## Cross-Phase Arbitration

### `07.3` owns telemetry contracts

`08` 不改 exporter fields / semantics；
只消费 exporter truth 作为 pack 的 telemetry section 上游。

### `07.4` owns replay outputs

`08` 不改 replay driver / manifests / run summary schema；
只消费 replay run summaries 与 authority pointers。

### `07.5` owns governance closeout

`08` 不重做 matrix / residual 仲裁；
只读取 `V1_1_EVIDENCE_INDEX.md` 与 governance pointers，并把它们编入 pack。

## Output Shape

至少包含以下 sections：
- `metadata`：pack version、生成时间、source versions；
- `telemetry`：来自 exporter truth 的摘要 / views / signal highlights；
- `replay`：来自 replay run summary 的场景结果与 drift signals；
- `boundary`：authority inventory 摘要与关键 source pointers；
- `governance`：verification commands、residuals、delete gates、owner pointers；
- `index`：section-to-source 映射与 authority trace。

## Non-Goals

- 不把 evidence pack 变成第二 diagnostics surface；
- 不把 exporter / replay / governance 真源复制一份再维护；
- 不在本 phase 引入重型 observability stack 或新 runtime service。
