# Phase 15: Support Feedback Contract Hardening, Governance Truth Repair, and Maintainability Follow-Through - Context

**Gathered:** 2026-03-15
**Status:** Ready for planning
**Source:** PRD Express Path (`.planning/phases/15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through/15-PRD.md`)

<domain>
## Phase Boundary

本 phase 聚焦复核后仍然成立的支持面 / 治理面 / 维护性问题：
1. developer feedback 上传契约与脱敏口径收口；
2. active governance truth dead-source / phase-status drift 修补；
3. README / README_zh / support metadata / CI 真相同步；
4. service router 与 developer-report / feedback 路径热点继续拆薄；
5. testing / tooling / security / typing / residual follow-through 缺口收口。

</domain>

<decisions>
## Implementation Decisions

### Support Feedback Contract
- `iotName` 必须保留真实值；这是设备判型与调试判断真源。
- `deviceName` / `name` / room labels / panel `keyName` / IR 资产展示名等用户自定义标签必须匿名化或替换为非识别性表示。
- 对外文案必须准确描述“保留 vendor diagnosis identifiers，匿名化 user-defined labels”，不得再笼统写成完全匿名/完全脱敏。
- external-boundary fixtures 与 tests 必须覆盖带真实 `iotName` 和用户标签混合的 payload。

### Governance Truth Repair
- active governance docs 不能再引用不存在 source path。
- `PROJECT.md` / `STATE.md` / `ROADMAP.md` 的 phase/status/date/footer 必须一致。
- guards 要 fail-fast 校验 active source path existence 与关键状态一致性。

### Docs / Support Alignment
- README / README_zh 安装入口必须前置最低 HA 版本 `2026.3.1`。
- 必须显式说明 private repo 场景下 HACS validation 不执行。
- README / README_zh / `hacs.json` / `pyproject.toml` / `SECURITY.md` / Issue 模板 / CONTRIBUTING 必须同步。

### Hotspot Follow-Through
- `control/service_router.py` 保留 public handler home，不改变正式身份。
- developer report 的 local debug view 与 upload payload shaping 必须分家。
- 不引入新的 helper-root / control backdoor。

### Testing / Tooling / Typing / Residual Follow-Through
- marker registry 要么真用，要么删除。
- coverage diff 要么真正做 baseline diff，要么重命名/重定义职责。
- benchmark / dev-audit policy 要写成可执行 gate 或 documented arbitration。
- `RuntimeAccess` 与相邻 control seams 中能收窄的 `Any` 要继续收口。
- `_ClientBase` / `client_*` helper spine、`LiproMqttClient` residual naming 继续本地化与 guard hardening，不回流为正式 surface。

### Claude's Discretion
- 具体拆分粒度、plan 数量与 wave 编排；
- 哪些 tooling gap 在本 phase 直接落地，哪些改为 documented arbitration + guards；
- 在不引入第二主链的前提下，为 developer feedback contract 选择最小代价实现路径。

</decisions>

<specifics>
## Specific Ideas

- 新增 developer-feedback 专用 payload sanitizer / projector，使 upload contract 与 local debug report 分离；
- 为 README / README_zh / version metadata 新增一致性守卫；
- 扩展 governance checker，校验 active source path existence 与 status/date/footer drift；
- 继续抽薄 `service_router.py` 与 developer report builder，把 upload-only shaping 下沉到 focused helper；
- 对 marker / benchmark / dev-audit / coverage-diff 做一次明确裁决并固化到 CI / docs / tests。

</specifics>

<deferred>
## Deferred Ideas

- `LiproMqttClient` 物理 rename；
- 大规模 helper spine 文件级删除；
- 与北极星无关的广泛换栈或架构重写。

</deferred>

---

*Phase: 15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through*
*Context gathered: 2026-03-15 via PRD Express Path*
