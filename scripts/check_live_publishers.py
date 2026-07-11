#!/usr/bin/env python3
"""Compatibility entrypoint for the recurrence live-publisher audit mechanic."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[1]
IMPL_PATH = (
    REPO_ROOT
    / "mechanics"
    / "recurrence"
    / "parts"
    / "live-receipt-refresh"
    / "scripts"
    / "check_live_publishers.py"
)


def _load_impl() -> ModuleType:
    script_dir = str(IMPL_PATH.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location(
        "_aoa_stats_live_publisher_audit",
        IMPL_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load live publisher audit implementation: {IMPL_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_IMPL = _load_impl()
_IMPL_EXPORT_BASELINES: dict[str, object] = {}


def _sync_impl_globals() -> None:
    for _name, _value in list(globals().items()):
        if _name in {
            "_IMPL",
            "_IMPL_EXPORT_BASELINES",
            "_sync_impl_globals",
            "_wrap_impl_function",
        }:
            continue
        if _name.startswith("__") and _name.endswith("__"):
            continue
        if hasattr(_IMPL, _name) and (
            not callable(_value)
            or _value is not _IMPL_EXPORT_BASELINES.get(_name, _value)
        ):
            setattr(_IMPL, _name, _value)


def _wrap_impl_function(_function_name: str):
    def _wrapped(*args, **kwargs):
        _sync_impl_globals()
        return getattr(_IMPL, _function_name)(*args, **kwargs)

    _wrapped.__name__ = _function_name
    _wrapped.__doc__ = getattr(_IMPL, _function_name).__doc__
    return _wrapped


for _name in dir(_IMPL):
    if _name.startswith("__") and _name.endswith("__"):
        continue
    _value = getattr(_IMPL, _name)
    if callable(_value) and getattr(_value, "__module__", None) == _IMPL.__name__:
        _wrapped = _wrap_impl_function(_name)
        globals()[_name] = _wrapped
    else:
        globals()[_name] = _value
    _IMPL_EXPORT_BASELINES[_name] = globals()[_name]

CANONICAL_IMPLEMENTATION = IMPL_PATH


if __name__ == "__main__":
    raise SystemExit(main())
