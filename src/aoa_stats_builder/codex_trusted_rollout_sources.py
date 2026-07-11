from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .codex_trusted_rollout import validate_codex_trusted_rollout_chain
from .receipt_abi import ReceiptValidationError


CODEX_TRUSTED_ROLLOUT_ROOT = Path("generated/codex/rollout")
CODEX_TRUSTED_ROLLOUT_DEPLOY_HISTORY = (
    CODEX_TRUSTED_ROLLOUT_ROOT / "deploy_history.jsonl"
)
CODEX_TRUSTED_ROLLOUT_REGENERATION_CAMPAIGNS = (
    CODEX_TRUSTED_ROLLOUT_ROOT / "regeneration_campaigns.min.json"
)
CODEX_TRUSTED_ROLLOUT_ROLLBACK_WINDOWS = (
    CODEX_TRUSTED_ROLLOUT_ROOT / "rollback_windows.min.json"
)
CODEX_TRUSTED_ROLLOUT_LATEST = CODEX_TRUSTED_ROLLOUT_ROOT / "rollout_latest.min.json"


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
class CodexTrustedRolloutInputBundle:
    source: Mapping[str, Any]
    deploy_history: Sequence[Mapping[str, Any]]
    regeneration: Mapping[str, Any]
    rollback: Mapping[str, Any]
    latest: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "source", _freeze(self.source))
        object.__setattr__(
            self,
            "deploy_history",
            tuple(_freeze(row) for row in self.deploy_history),
        )
        object.__setattr__(self, "regeneration", _freeze(self.regeneration))
        object.__setattr__(self, "rollback", _freeze(self.rollback))
        object.__setattr__(self, "latest", _freeze(self.latest))

    def mutable_parts(
        self,
    ) -> tuple[
        dict[str, Any],
        list[dict[str, Any]],
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
    ]:
        """Preserve the historical mutable five-part root facade."""

        return (
            _thaw(self.source),
            _thaw(self.deploy_history),
            _thaw(self.regeneration),
            _thaw(self.rollback),
            _thaw(self.latest),
        )


def codex_trusted_rollout_paths(owner_root: Path) -> tuple[Path, Path, Path, Path]:
    return (
        owner_root / CODEX_TRUSTED_ROLLOUT_DEPLOY_HISTORY,
        owner_root / CODEX_TRUSTED_ROLLOUT_REGENERATION_CAMPAIGNS,
        owner_root / CODEX_TRUSTED_ROLLOUT_ROLLBACK_WINDOWS,
        owner_root / CODEX_TRUSTED_ROLLOUT_LATEST,
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


def _load_jsonl_objects(path: Path, *, label: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise ReceiptValidationError(f"missing {label}: {path}") from exc
    rows: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ReceiptValidationError(
                f"invalid JSON in {label}: {path}:{line_number}"
            ) from exc
        if not isinstance(payload, dict):
            raise ReceiptValidationError(
                f"{label} row must be a JSON object: {path}:{line_number}"
            )
        rows.append(payload)
    return rows


def load_codex_trusted_rollout_bundle(
    owner_root: Path,
) -> CodexTrustedRolloutInputBundle:
    owner_root = owner_root.expanduser().resolve()
    deploy_path, regeneration_path, rollback_path, latest_path = (
        codex_trusted_rollout_paths(owner_root)
    )
    deploy_history = _load_jsonl_objects(
        deploy_path,
        label="Codex trusted rollout deploy history",
    )
    regeneration = _load_json_object(
        regeneration_path,
        label="Codex trusted rollout regeneration campaigns",
    )
    rollback = _load_json_object(
        rollback_path,
        label="Codex trusted rollout rollback windows",
    )
    latest = _load_json_object(
        latest_path,
        label="Codex trusted rollout latest summary",
    )
    latest_observed_at = validate_codex_trusted_rollout_chain(
        deploy_history,
        regeneration,
        rollback,
        latest,
    )
    paths = (deploy_path, regeneration_path, rollback_path, latest_path)
    source_refs = tuple(
        f"8Dionysus/{path.relative_to(owner_root).as_posix()}" for path in paths
    )
    return CodexTrustedRolloutInputBundle(
        source={
            "receipt_input_paths": list(source_refs),
            "total_receipts": len(deploy_history),
            "latest_observed_at": latest_observed_at.isoformat().replace("+00:00", "Z"),
        },
        deploy_history=deploy_history,
        regeneration=regeneration,
        rollback=rollback,
        latest=latest,
    )
