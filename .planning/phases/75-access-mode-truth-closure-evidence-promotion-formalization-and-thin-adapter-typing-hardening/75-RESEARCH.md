# Phase 75 Research

## Verified Inputs

1. **Repository visibility is private**
   - `gh repo view Exlany/lipro-hass --json visibility,url,nameWithOwner,isPrivate` → `{"visibility":"PRIVATE","isPrivate":true}`
   - `git ls-remote git@github.com:Exlany/lipro-hass.git HEAD` succeeds, proving the repository exists rather than having been deleted/renamed.
   - Public web routes under `https://github.com/Exlany/lipro-hass/*` return `404` for unauthenticated users, so current public-facing docs cannot pretend those routes are universally reachable.

2. **The HACS/public-install story must be access-mode aware**
   - HACS only supports public GitHub repositories; current docs already partially acknowledge this, but several entrypoints still label HACS / public releases / public Issues / Discussions as the default guidance for the current repo.
   - Chosen remediation direction: make the current repository's docs honest about private-access limits, while keeping wording ready for a future public mirror/release surface if the maintainer later enables one.

3. **`v1.20` closeout evidence is audited but not fully promoted**
   - `.planning/v1.20-MILESTONE-AUDIT.md` already treats `Phase 72/73/74` summary/verification/validation assets as accepted evidence.
   - `.planning/reviews/PROMOTED_PHASE_ASSETS.md` and `.planning/baseline/VERIFICATION_MATRIX.md` still lag behind that audit truth.
   - Chosen remediation direction: promote the actual allowlisted assets and tighten the state wording so Git tracking is not confused with authority.

4. **Thin-adapter typing opportunities are localized**
   - `custom_components/lipro/diagnostics.py` and `custom_components/lipro/system_health.py` are already thin adapters over typed control-plane surfaces, so they can adopt those types directly.
   - `custom_components/lipro/flow/options_flow.py` still uses broad `Any` for option payloads even though the persisted options are bounded to scalar booleans/ints/strings and normalized text selectors.
   - Chosen remediation direction: narrow types without changing behavior or reopening runtime/control ownership.

## Canonical References

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- `docs/README.md`
- `README.md`
- `README_zh.md`
- `SUPPORT.md`
- `SECURITY.md`
- `custom_components/lipro/diagnostics.py`
- `custom_components/lipro/system_health.py`
- `custom_components/lipro/flow/options_flow.py`
