from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .receipt_abi import ReceiptValidationError
from .rollout_cadence import validate_rollout_cadence_chain


ROLLOUT_CAMPAIGN_WINDOW_EXAMPLE = Path("examples/rollout_campaign_window.example.json")
DRIFT_REVIEW_WINDOW_EXAMPLE = Path("examples/drift_review_window.example.json")
ROLLBACK_FOLLOWTHROUGH_WINDOW_EXAMPLE = Path(
    "examples/rollback_followthrough_window.example.json"
)


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): _freeze(item) for key, item in value.items()}
        )
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
class RolloutCadenceInputBundle:
    source: Mapping[str, Any]
    campaign: Mapping[str, Any]
    review: Mapping[str, Any]
    rollback: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "source", _freeze(self.source))
        object.__setattr__(self, "campaign", _freeze(self.campaign))
        object.__setattr__(self, "review", _freeze(self.review))
        object.__setattr__(self, "rollback", _freeze(self.rollback))

    def mutable_parts(
        self,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
        """Preserve the historical root tuple contract for compatibility."""

        return (
            _thaw(self.source),
            _thaw(self.campaign),
            _thaw(self.review),
            _thaw(self.rollback),
        )


def rollout_cadence_reference_paths(owner_root: Path) -> tuple[Path, Path, Path]:
    return (
        owner_root / ROLLOUT_CAMPAIGN_WINDOW_EXAMPLE,
        owner_root / DRIFT_REVIEW_WINDOW_EXAMPLE,
        owner_root / ROLLBACK_FOLLOWTHROUGH_WINDOW_EXAMPLE,
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


def load_rollout_cadence_reference_bundle(
    owner_root: Path,
) -> RolloutCadenceInputBundle:
    owner_root = owner_root.expanduser().resolve()
    campaign_path, review_path, rollback_path = rollout_cadence_reference_paths(
        owner_root
    )
    campaign = _load_json_object(campaign_path, label="rollout campaign window")
    review = _load_json_object(review_path, label="drift review window")
    rollback = _load_json_object(rollback_path, label="rollback followthrough window")
    latest_observed_at = validate_rollout_cadence_chain(campaign, review, rollback)
    paths = (campaign_path, review_path, rollback_path)
    return RolloutCadenceInputBundle(
        source={
            "receipt_input_paths": [
                f"8Dionysus/{path.relative_to(owner_root).as_posix()}" for path in paths
            ],
            "total_receipts": 1,
            "latest_observed_at": latest_observed_at.isoformat().replace("+00:00", "Z"),
        },
        campaign=campaign,
        review=review,
        rollback=rollback,
    )
