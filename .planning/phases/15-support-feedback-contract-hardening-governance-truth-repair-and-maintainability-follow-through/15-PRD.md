# Phase 15 PRD

**Date:** 2026-03-15
**Status:** Draft for planning
**Source:** 终极审阅复核 + 契约者裁决

## Objective

把终极审阅中复核后仍然成立的问题收敛为单一执行相位：

1. 明确并固化 developer feedback 上传契约；
2. 修补 active governance truth 中的死链、状态漂移与 guard 缺口；
3. 同步用户可见安装/支持文档与 CI / metadata 真相；
4. 继续拆薄 support / diagnostics 热点；
5. 收口本轮确认存在的 testing / tooling / security / typing / residual follow-through 缺口。

## Locked Decisions

### Support Feedback Contract

- `iotName` 必须保持真实值；这是设备判型与问题定位所需的供应商诊断真源，不能匿名化。
- `deviceName` / `name` 一类用户自定义显示名必须匿名化或替换为非识别性表示；不要把用户给设备起的名字直接上传。
- `roomName`、panel `keyName`、IR 资产展示名（如 `rc_list[].name`）默认按用户自定义/用户环境标签处理，除非有明确证据证明其为供应商 canonical code，否则不得原样上传。
- developer feedback 对外文案不得再笼统宣称“匿名/完全脱敏”而不说明会保留哪些诊断标识；必须准确描述“保留 `iotName` 等判型字段，移除或匿名化用户自定义标签”。
- external-boundary fixtures 与回归测试必须覆盖带 `iotName`、`deviceName`、panel label、IR asset label 的真实样本，而不是只测 `note`。

### Governance Truth Repair

- active governance docs 不能再引用不存在的 source path。
- `PROJECT.md` / `STATE.md` / `ROADMAP.md` 中 phase/status/date/footer/closeout 叙事必须一致。
- 脚本/guards 必须能 fail-fast 检查 active source path existence 与关键状态字段一致性。

### Contributor / Install Docs Alignment

- README / README_zh 安装入口必须前置最低支持 Home Assistant 版本 `2026.3.1`。
- README / README_zh 必须说明 private repo 场景下 HACS validation 不会在 CI 中执行。
- 相关口径必须与 `hacs.json`、`pyproject.toml`、`SECURITY.md`、Issue 模板、CONTRIBUTING 保持一致，并由测试守卫。

### Hotspot Follow-Through

- `control/service_router.py` 保留 public handler home 身份，但进一步下沉 developer/share/diagnostics 私有 glue。
- developer report 的“本地调试视图”与“上传给 share worker 的 payload shaping”必须分离，不再共享同一对象图与同一脱敏策略。
- 不引入新的 control-plane backdoor，也不让 helper 模块升级成新的正式 root。

### Testing / Tooling / Security Follow-Through

- `pytest` marker registry（`github` / `integration` / `slow`）要么真正落地到测试切分，要么从配置中移除，禁止名存实亡。
- `coverage_diff.py` 若继续叫 diff，CI 必须提供 baseline；若不做 diff，就要更名或重新定义职责，避免伪语义。
- benchmark policy 必须明确：要么引入历史基线/阈值，要么在文档与 CI 中明确它是 non-gating observability，不再造成“看似有门、实际无门”的误导。
- dev dependency audit 风险必须变成明确 policy：至少高危场景不应仅停留在 schedule/manual + continue-on-error。
- `pytest-xdist` / `pytest-mypy-plugins` 等已声明但未利用的工具要么落地使用，要么移除，避免空转复杂度。

### Typing / Residual Follow-Through

- `control/runtime_access.py` 与相邻 control seams 中可收窄的 `Any` 必须继续收口到正式 contract。
- `_ClientBase` / `client_*` helper spine、`LiproMqttClient` legacy naming 与其 guard story 必须继续本地化和减语义，不把 residual 重新提升成正式 surface。
- 本 phase 不做第二套主链，不广泛换栈，不进行与北极星无关的大规模重命名。

## Acceptance Criteria

1. developer feedback 上传契约有新的/更新的 fixture、tests、docs，且明确保留 `iotName`、匿名化用户标签。
2. `PROJECT.md` / `STATE.md` / `ROADMAP.md` / guards 不再存在 active dead source 与 phase-status drift。
3. README / README_zh / version/support metadata 对最低 HA 版本与 HACS caveat 保持一致，并被自动校验。
4. `service_router.py` 与 developer-feedback/report path 的热点继续拆薄，职责边界更清楚。
5. testing/tooling/security/typing/residual 的确认问题都有明确处置：落地、删除、或写成 guard-backed documented arbitration。

## Out of Scope

- 物理 rename `LiproMqttClient`
- 大规模框架替换或引入新重型依赖
- 重写整套 telemetry / replay / evidence 主链
- 把 support 相关 helper 重新提升为正式 root
