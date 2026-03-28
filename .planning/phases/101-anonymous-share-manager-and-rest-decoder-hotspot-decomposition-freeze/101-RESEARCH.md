# Phase 101 Research

## Scope

对 `anonymous_share` manager family 与 REST protocol boundary decode family 做“正式 home 保留 + residual cleanup / support truth tightening”式终审收口，并把治理真相前推到 `Phase 101 complete`。

## Findings

### 1. `AnonymousShareManager` 需要的是 residual cleanup，不是重开新 root
- `manager.py` 当前混合了 scope/aggregate view 创建、状态代理、缓存持久化、提交流程门面与 submit-finalize 逻辑；其 formal home 身份没问题，但 `_foo` / `foo` 双份薄包装与 accessor re-export 仍在扩大测试表面积。
- aggregate developer-feedback 现在存在 state/client/outcome 错配风险：aggregate view 选 primary state 的 metadata / lock，却仍可能用 default scope client 与 outcome state。
- `manager_submission.py` 的 aggregate traversal 在 `submit_report` / `submit_if_needed` 间重复，且 disabled scope 会被折算成 aggregate failure，语义不够诚实。
- `manager_support.py` 的 cache lifecycle 目前没有显式清空 stale reported-device keys；切换 `storage_path` 或 load 失败后可能沿用旧 keys。

### 2. REST boundary 真热点在 `rest_decoder_support.py`
- `rest_decoder.py` 本体多为 family metadata + thin decoder shell，formal home 基本正确；真正决定 canonical shape 的热点在 `rest_decoder_support.py`。
- top-level fallback property extraction 目前是“黑名单排除后全收”，更容易把 vendor metadata 或 nested payload 漏穿进 canonical `properties`。
- list-envelope offset/hasMore 语义在 `ListEnvelopeRestDecoder` 与 `DeviceListRestDecoder` 之间不够单一；负 offset 情况下存在 helper / wrapper 语义分裂。
- schedule decode 现在 parse 两次（一次 canonical、一次 fingerprint），属于低风险但值得顺手收口的重复。

### 3. `rest_facade.py` 本 phase 不做结构重拆
- `LiproRestFacade` 当前主要承担 composition root + explicit method binding；虽然文件厚，但 public surface / test blast radius 大，不适合在本 phase 深拆。
- 本轮只做 truth cleanup：child-facing typed payload wording 保持诚实，避免把 endpoint payload 说成 protocol-canonical contract。

## Recommended Phase Shape

### Plan 101-01
收口 `anonymous_share` manager family：移除 accessor re-export、合并无语义双层包装、修正 aggregate submit outcome/client selection、统一 child traversal no-op 语义，并补 focused aggregate/cache regressions。

### Plan 101-02
收口 REST boundary decode family：tighten fallback property extraction、统一 offset truth、schedule parse once，并补 boundary focused regressions；`rest_facade` 只做 wording cleanup。

### Plan 101-03
把 `.planning/*`、developer guide、maps/ledgers、focused guards 与 GSD parser truth 推进到 `Phase 101 complete`，并通过 focused + repo-wide proof chain 重新冻结 `$gsd-next -> $gsd-complete-milestone v1.27`。

## Why This Is Optimal
- 两个目标都具备清晰的 localized seam：一个是 manager family residual cleanup，一个是 protocol-boundary support truth tightening。
- 它们覆盖匿名分享与 protocol boundary 两条仍然活跃的终审热点，但不会把 `rest_facade.py` 拉进高回归半径的结构重拆。
- 这样能在不制造第二条主线的前提下，继续把 `v1.27` 收口到更诚实、更低噪声的 closeout-ready 状态。
