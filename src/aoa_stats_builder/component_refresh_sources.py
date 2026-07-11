from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .component_refresh import validate_reviewed_component_refresh_sets
from .receipt_abi import ReceiptValidationError


SDK_REVIEWED_CLOSEOUT_EXAMPLES = Path(
    "mechanics/checkpoint/parts/reviewed-closeout-context-carry/examples"
)
SDK_COMPONENT_DRIFT_HINTS_EXAMPLE = (
    SDK_REVIEWED_CLOSEOUT_EXAMPLES / "component_drift_hints.example.json"
)
SDK_COMPONENT_REFRESH_DECISIONS_EXAMPLE = (
    SDK_REVIEWED_CLOSEOUT_EXAMPLES
    / "component_refresh_followthrough_decision.example.json"
)


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _thaw(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True, slots=True)
class ComponentRefreshInputBundle:
    source: Mapping[str, Any]
    hints: Sequence[Mapping[str, Any]]
    decisions: Sequence[Mapping[str, Any]]

    def __post_init__(self) -> None:
        object.__setattr__(self, "source", _freeze(self.source))
        object.__setattr__(self, "hints", _freeze(self.hints))
        object.__setattr__(self, "decisions", _freeze(self.decisions))

    def mutable_parts(
        self,
    ) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
        return _thaw(self.source), _thaw(self.hints), _thaw(self.decisions)


def reviewed_sdk_example_paths(sdk_root: Path) -> tuple[Path, Path]:
    return (
        sdk_root / SDK_COMPONENT_DRIFT_HINTS_EXAMPLE,
        sdk_root / SDK_COMPONENT_REFRESH_DECISIONS_EXAMPLE,
    )


def _load_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ReceiptValidationError(f"missing {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ReceiptValidationError(f"invalid JSON in {label}: {path}") from exc
    if not isinstance(payload, dict):
        raise ReceiptValidationError(f"{label} must be a JSON object: {path}")
    return payload


def load_reviewed_sdk_example_bundle(sdk_root: Path) -> ComponentRefreshInputBundle:
    sdk_root = sdk_root.expanduser().resolve()
    hint_path, decision_path = reviewed_sdk_example_paths(sdk_root)
    hint_set = _load_json_object(hint_path, label="component drift hint example")
    decision_set = _load_json_object(
        decision_path,
        label="component refresh followthrough decision example",
    )
    hints, decisions, latest_hint_observed_at = (
        validate_reviewed_component_refresh_sets(hint_set, decision_set)
    )
    source = {
        "receipt_input_paths": [
            f"aoa-sdk/{hint_path.relative_to(sdk_root).as_posix()}",
            f"aoa-sdk/{decision_path.relative_to(sdk_root).as_posix()}",
        ],
        "total_receipts": 2,
        "latest_observed_at": latest_hint_observed_at.isoformat().replace(
            "+00:00", "Z"
        ),
    }
    return ComponentRefreshInputBundle(
        source=source,
        hints=hints,
        decisions=decisions,
    )
