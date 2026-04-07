# Summary 114-01

## What changed
- 收紧 `README.md`、`README_zh.md`、`SUPPORT.md`、`SECURITY.md` 与 `custom_components/lipro/services.yaml` 的 public/privacy/security wording，使其与真实 access-mode、debug-mode、diagnostics/disclosure 语义一致。
- `anonymous share` wording 现明确为 sanitized / pseudonymous payload，而不是暗示强匿名；`developer report` wording 现明确为 debug-mode-only、local-only、partially redacted 视图。
- `remember password` wording 现明确说明本地保存的是 hashed-login credential-equivalent secret。
- `scripts/lint` help 文案已承认 default mode 在匹配 changed surfaces 时会触发 focused pytest/governance assurance。
- `custom_components/lipro/flow/credentials.py` 去除了 SQL-injection/security-theater 说法，并把密码控制字符策略收紧为拒绝全部 ASCII control characters；`tests/flows/test_flow_credentials.py` 已同步。

## Why it changed
- `OSS-14` / `SEC-09` 的第一层收口不是新增入口，而是让现有 public/docs/service wording 不再比真实语义更强。
- 若文档把 pseudonymous telemetry 讲成 anonymous、把 local debug export 讲成 fully redacted、把 hashed-login secret 讲成 harmless hash，会持续误导使用者与维护者。

## Verification
- `uv run pytest -q tests/flows/test_flow_credentials.py tests/services/test_services_registry.py tests/meta/test_governance_release_continuity.py tests/meta/test_governance_release_docs.py tests/meta/toolchain_truth_docs_fast_path.py`
- `57 passed in 0.98s`

## Outcome
- Wave 1 现在把 privacy/disclosure/debug truth 压回真实强度，不再依赖读者自己猜边界。
