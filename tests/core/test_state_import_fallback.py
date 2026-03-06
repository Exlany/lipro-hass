"""Tests for coordinator state module import-time fallbacks."""

from __future__ import annotations

import builtins
import importlib.util
import sys


def test_state_sets_ha_version_to_none_when_homeassistant_const_missing(monkeypatch):
    from custom_components.lipro.core.coordinator import state

    module_path = state.__file__
    assert module_path is not None

    module_name = "custom_components.lipro.core.coordinator._state_import_error_test"
    sys.modules.pop(module_name, None)

    original_import = builtins.__import__

    def _fake_import(name, globals_=None, locals_=None, fromlist=(), level=0):
        if name == "homeassistant.const":
            raise ImportError("missing homeassistant.const")
        return original_import(name, globals_, locals_, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _fake_import)

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
        assert module.HA_VERSION is None
    finally:
        sys.modules.pop(module_name, None)
