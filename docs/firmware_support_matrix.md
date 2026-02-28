# Lipro Firmware OTA Support Matrix

[中文](firmware_support_matrix_zh.md) | English

This page is designed for two views:

1. **User Device View (primary)**: read by your real Home Assistant device names.
2. **Model Baseline View (secondary)**: firmware versions certified by model/type.

## Status Legend

- ✅ `Certified`: verified and in `firmware_support_manifest.json`
- 🟡 `Unknown`: discovered but not certified yet
- ❌ `Blocked`: should not be upgraded now

## User Device View (Recommended)

Use your **actual device names** (not only model codes) for readability:

| Room | Device Name | Entity ID | Model/Type | Firmware | Certification | Notes |
|---|---|---|---|---|---|---|
| Master Bedroom | Main Strip | `light.master_bed_strip` | `ff000001` | `7.10.9` | ✅ Certified | Daily use |
| Living Room | Wall Switch | `switch.living_wall_switch` | `Meizu Switch` | `3.6.6` | ✅ Certified | Stable |
| _Add your own_ | _..._ | _..._ | _..._ | _..._ | _✅/🟡/❌_ | _..._ |

## Model Baseline (Certified)

| Device Type / Model | Firmware Version | Certification | Notes |
|---|---|---|---|
| `ff000001` (Light family) | `7.10.9` | ✅ Certified | In certification manifest |
| `T21JC` | `2.6.43` | ✅ Certified | In certification manifest |
| `T21JE` | `2.6.44` | ✅ Certified | In certification manifest |
| `T23K1` | `1.3.42` | ✅ Certified | In certification manifest |
| `T21K1` | `3.5.6` | ✅ Certified | In certification manifest |
| `Meizu Switch` | `3.6.6` | ✅ Certified | In certification manifest |

## Newly Observed (Uncertified)

| Device Name | Model/Type | Firmware | Certification | Action |
|---|---|---|---|---|
| _None currently_ | - | - | 🟡 Unknown | Add when a new firmware appears |

## Validation Checklist

1. Check the device `update` entity for available firmware.
2. Install from the `update` entity (uncertified firmware may require a second confirmation install within the confirmation window).
3. Record pre/post upgrade state in the diagnostics report.
4. Update this matrix and `custom_components/lipro/firmware_support_manifest.json`.
