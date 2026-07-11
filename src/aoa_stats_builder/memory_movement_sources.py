from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .memory_movement import (
    MEMORY_MOVEMENT_INPUT_REFS,
    ReferencedPayload,
    validate_memory_movement_inputs,
)
from .receipt_abi import ReceiptValidationError


MEMORY_OBJECT_CATALOG = Path(
    "generated/memory-objects/memory_object_catalog.min.json"
)
REVIEWED_MEMORY_OBJECT_ROOT = Path("memo/objects")
REVIEWED_INTAKE_ROOT = Path("memo/intake/reviewed")
LANDING_RECEIPT_ROOT = Path("memo/intake/receipts")


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


def _mutable_referenced_payloads(
    values: Sequence[ReferencedPayload],
) -> list[tuple[str, dict[str, Any]]]:
    return [(str(ref), _thaw(payload)) for ref, payload in values]


@dataclass(frozen=True, slots=True)
class MemoryMovementInputBundle:
    source: Mapping[str, Any]
    catalog: Mapping[str, Any]
    memory_objects: Sequence[ReferencedPayload]
    reviewed_intakes: Sequence[ReferencedPayload]
    landing_receipts: Sequence[ReferencedPayload]

    def __post_init__(self) -> None:
        object.__setattr__(self, "source", _freeze(self.source))
        object.__setattr__(self, "catalog", _freeze(self.catalog))
        object.__setattr__(self, "memory_objects", _freeze(self.memory_objects))
        object.__setattr__(self, "reviewed_intakes", _freeze(self.reviewed_intakes))
        object.__setattr__(self, "landing_receipts", _freeze(self.landing_receipts))

    def mutable_parts(
        self,
    ) -> tuple[
        dict[str, Any],
        dict[str, Any],
        list[tuple[str, dict[str, Any]]],
        list[tuple[str, dict[str, Any]]],
        list[tuple[str, dict[str, Any]]],
    ]:
        return (
            _thaw(self.source),
            _thaw(self.catalog),
            _mutable_referenced_payloads(self.memory_objects),
            _mutable_referenced_payloads(self.reviewed_intakes),
            _mutable_referenced_payloads(self.landing_receipts),
        )


def memory_movement_source_paths(memo_root: Path) -> tuple[Path, Path, Path, Path]:
    memo_root = memo_root.expanduser().resolve()
    return (
        memo_root / MEMORY_OBJECT_CATALOG,
        memo_root / REVIEWED_MEMORY_OBJECT_ROOT,
        memo_root / REVIEWED_INTAKE_ROOT,
        memo_root / LANDING_RECEIPT_ROOT,
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


def _display_aoa_memo_ref(*, memo_root: Path, path: Path) -> str:
    try:
        relative_path = path.relative_to(memo_root)
    except ValueError as exc:
        raise ReceiptValidationError(
            f"aoa-memo memory movement source escaped its configured root: {path}"
        ) from exc
    return f"aoa-memo/{relative_path.as_posix()}"


def _load_json_file_set(
    root: Path, *, memo_root: Path, label: str
) -> tuple[ReferencedPayload, ...]:
    if not root.exists():
        raise ReceiptValidationError(f"missing {label}: {root}")
    return tuple(
        (
            _display_aoa_memo_ref(memo_root=memo_root, path=path),
            _load_json_object(path, label=f"{label} JSON"),
        )
        for path in sorted(root.glob("*.json"))
    )


def _load_memory_object_set(
    root: Path, *, memo_root: Path
) -> tuple[ReferencedPayload, ...]:
    if not root.exists():
        raise ReceiptValidationError(
            f"missing reviewed memory object corpus: {root}"
        )
    return tuple(
        (
            _display_aoa_memo_ref(memo_root=memo_root, path=path),
            _load_json_object(path, label="reviewed memory object"),
        )
        for path in sorted(root.rglob("object.json"))
    )


def load_memory_movement_bundle(memo_root: Path) -> MemoryMovementInputBundle:
    memo_root = memo_root.expanduser().resolve()
    catalog_path, objects_root, reviewed_root, receipts_root = (
        memory_movement_source_paths(memo_root)
    )
    catalog = _load_json_object(
        catalog_path, label="aoa-memo memory object min catalog"
    )
    memory_objects = _load_memory_object_set(objects_root, memo_root=memo_root)
    reviewed_intakes = _load_json_file_set(
        reviewed_root,
        memo_root=memo_root,
        label="aoa-memo reviewed intake packets",
    )
    landing_receipts = _load_json_file_set(
        receipts_root,
        memo_root=memo_root,
        label="aoa-memo landing receipts",
    )
    latest_observed_at = validate_memory_movement_inputs(
        catalog,
        memory_objects,
        reviewed_intakes,
        landing_receipts,
    )
    return MemoryMovementInputBundle(
        source={
            "receipt_input_paths": list(MEMORY_MOVEMENT_INPUT_REFS),
            "total_receipts": (
                len(memory_objects) + len(reviewed_intakes) + len(landing_receipts)
            ),
            "latest_observed_at": latest_observed_at.isoformat().replace(
                "+00:00", "Z"
            ),
        },
        catalog=catalog,
        memory_objects=memory_objects,
        reviewed_intakes=reviewed_intakes,
        landing_receipts=landing_receipts,
    )
