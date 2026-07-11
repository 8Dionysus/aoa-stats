from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .receipt_abi import ReceiptValidationError


AGENTS_OPERATOR_ROSTER = Path(
    "mechanics/titan/parts/incarnation-spine/examples/"
    "operator-console-roster.v0.json"
)
AGENTS_RUNTIME_ROSTER = Path(
    "mechanics/titan/parts/runtime-roster/examples/runtime-roster.v0.json"
)
SDK_SESSION_RECEIPT = Path(
    "mechanics/titan/parts/incarnation-identity-runtime-helper-contracts/"
    "examples/titan_session_receipt.v2.example.json"
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
class TitanIncarnationInputBundle:
    operator_roster: Mapping[str, Any]
    runtime_roster: Mapping[str, Any]
    session_receipt: Mapping[str, Any]
    source_refs: tuple[str, str, str]

    def __post_init__(self) -> None:
        object.__setattr__(self, "operator_roster", _freeze(self.operator_roster))
        object.__setattr__(self, "runtime_roster", _freeze(self.runtime_roster))
        object.__setattr__(self, "session_receipt", _freeze(self.session_receipt))

    def mutable_parts(
        self,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[str]]:
        return (
            _thaw(self.operator_roster),
            _thaw(self.runtime_roster),
            _thaw(self.session_receipt),
            list(self.source_refs),
        )


def titan_incarnation_reference_paths(
    *, agents_root: Path, sdk_root: Path
) -> tuple[Path, Path, Path]:
    return (
        agents_root / AGENTS_OPERATOR_ROSTER,
        agents_root / AGENTS_RUNTIME_ROSTER,
        sdk_root / SDK_SESSION_RECEIPT,
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


def _display_repo_path(repo_name: str, repo_root: Path, path: Path) -> str:
    try:
        relative_path = path.relative_to(repo_root)
    except ValueError as exc:
        raise ReceiptValidationError(
            f"{repo_name} Titan source escaped its configured repo root: {path}"
        ) from exc
    return f"{repo_name}/{relative_path.as_posix()}"


def load_titan_incarnation_reference_bundle(
    *, agents_root: Path, sdk_root: Path
) -> TitanIncarnationInputBundle:
    agents_root = agents_root.expanduser().resolve()
    sdk_root = sdk_root.expanduser().resolve()
    operator_path, runtime_path, session_path = titan_incarnation_reference_paths(
        agents_root=agents_root, sdk_root=sdk_root
    )
    return TitanIncarnationInputBundle(
        operator_roster=_load_json_object(
            operator_path, label="aoa-agents Titan operator roster example"
        ),
        runtime_roster=_load_json_object(
            runtime_path, label="aoa-agents Titan runtime roster example"
        ),
        session_receipt=_load_json_object(
            session_path, label="aoa-sdk Titan session receipt v2 example"
        ),
        source_refs=(
            _display_repo_path("aoa-agents", agents_root, operator_path),
            _display_repo_path("aoa-agents", agents_root, runtime_path),
            _display_repo_path("aoa-sdk", sdk_root, session_path),
        ),
    )
