from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .read_model_values import is_nonempty_string


AOA_EVALS_REPORT_REF_PREFIX = "repo:aoa-evals/"


def _owner_path(evals_root: Path, relative_path: Path) -> Path | None:
    owner_root = evals_root.expanduser().resolve()
    candidate = (owner_root / relative_path).resolve()
    try:
        candidate.relative_to(owner_root)
    except ValueError:
        return None
    return candidate


def resolve_aoa_evals_report_path(
    evals_root: Path,
    report_ref: Any,
) -> Path | None:
    if not is_nonempty_string(report_ref) or not report_ref.startswith(
        AOA_EVALS_REPORT_REF_PREFIX
    ):
        return None
    relative_ref = report_ref.removeprefix(AOA_EVALS_REPORT_REF_PREFIX)
    if not relative_ref or relative_ref.startswith(("/", "./")):
        return None
    if "\\" in relative_ref:
        return None
    parts = relative_ref.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return None
    return _owner_path(evals_root, Path(*parts))


def _load_optional_json_object(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def load_stress_recovery_report(
    evals_root: Path,
    report_ref: Any,
) -> dict[str, Any] | None:
    """Load only the exact safe repo:aoa-evals report ref."""

    return _load_optional_json_object(
        resolve_aoa_evals_report_path(evals_root, report_ref)
    )
