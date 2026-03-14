# Phase 10 Architecture

**Phase:** `10 API Drift Isolation & Core Boundary Prep`
**Status:** Executed architecture decision
**Date:** 2026-03-14

## Decision Summary

`Phase 10` 的最终裁决保持不变：**现在不物理拆出 shared `core`**。

正确做法不是提前把 HA runtime、CLI、other-host 需求揉成一个新 root，
而是先把高漂移逆向 API 的变化**封死在 protocol boundary**，再把可复用的
host-neutral nucleus 明确下来。

## Executed Decisions

### 1. Protocol plane 独占 drift absorption

以下高漂移 family 已正式收口到 protocol boundary + canonical contracts：

- `rest.device-list@v1`
- `rest.device-status@v1`
- `rest.mesh-group-status@v1`

对应实现与 authority 已固定到：

- `custom_components/lipro/core/protocol/boundary/rest_decoder.py`
- `custom_components/lipro/core/protocol/contracts.py`
- `tests/fixtures/api_contracts/`
- `tests/fixtures/protocol_replay/rest/`

runtime / control / platform 不再自己兼容 vendor envelope、field alias、pagination。

### 2. Auth/session truth 改为 formal contract

`custom_components/lipro/core/auth/manager.py` 现已提供 `AuthSessionSnapshot`，
作为 HA adapters 与未来宿主可复用的 formal auth/session contract。

已执行迁移：

- `custom_components/lipro/config_flow.py` 改走 `LiproAuthManager.login()` 返回的 session snapshot
- `custom_components/lipro/entry_auth.py` 优先消费 `get_auth_session()`，仅保留 `get_auth_data()` fallback 作为 compat seam

这让底层 login/result payload 包装层变化不再直接打穿 HA adapter。

### 3. Runtime home 继续留在 HA，core truth 保持 host-neutral

`Coordinator` 仍是唯一正式 runtime root，但它的 public home 继续固定在：

- `custom_components/lipro/coordinator_entry.py`

`custom_components/lipro/core/__init__.py` 已不再导出 `Coordinator`，
只保留 host-neutral exports，例如：

- `LiproProtocolFacade`
- `LiproMqttFacade`
- `LiproRestFacade`
- `AuthSessionSnapshot`

同时，control-plane runtime lookup 已继续收敛到：

- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/control/telemetry_surface.py`

### 4. Future host 只能复用 formal boundary

本 phase 已把“未来 CLI / other host 可以复用什么”写成正式文档事实：

**允许复用的 nucleus：**
- protocol boundary families / canonical contracts
- `LiproProtocolFacade`
- `AuthSessionSnapshot` / auth manager formal contract
- device aggregate / capability truth

**不在本 phase 抽离的 HA-specific home：**
- `Coordinator`
- `config_flow`
- diagnostics / system health adapters
- service wiring / entity glue / platform setup

## Explicit Non-Goals

- 不物理拆出 shared `core` package
- 不实现 CLI / 其他宿主
- 不引入 second root / 双主链
- 不把 HA runtime root 重新包装成“可复用核心”

## Remaining Delete-Gated Seams

`Phase 10` 之后，仍显式保留、但继续计数的 compat seam 主要只剩：

- `core.api.LiproClient`
- `LiproProtocolFacade.get_device_list`
- `LiproMqttFacade.raw_client`

这些 seam 继续保留 delete gate，但它们已不再拥有 authority truth。
