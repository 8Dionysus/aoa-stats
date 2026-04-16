from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = REPO_ROOT.parent
CANONICAL_ENVELOPE_SCHEMA_PATH = REPO_ROOT / "schemas" / "stats-event-envelope.schema.json"
CANONICAL_ENVELOPE_SCHEMA_REF = "schemas/stats-event-envelope.schema.json"
EVENT_KIND_REGISTRY_PATH = REPO_ROOT / "config" / "stats_event_kind_registry.json"
EVENT_KIND_REGISTRY_REF = "config/stats_event_kind_registry.json"
DEFAULT_EVALS_MIRROR_PATH = WORKSPACE_ROOT / "aoa-evals" / "schemas" / "stats-event-envelope.schema.json"
ALLOWED_MIRROR_METADATA_KEYS = frozenset(
    {"$id", "title", "description", "x-canonical_schema_ref"}
)


class ReceiptValidationError(ValueError):
    pass


def load_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ReceiptValidationError(f"missing {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ReceiptValidationError(f"{path}: invalid JSON for {label}") from exc
    if not isinstance(payload, dict):
        raise ReceiptValidationError(f"{path}: {label} must be a JSON object")
    return payload


def receipt_sort_key(receipt: dict[str, Any]) -> tuple[str, str]:
    return (receipt["observed_at"], receipt["event_id"])


def load_receipts(paths: list[Path]) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for path in paths:
        if path.suffix == ".jsonl":
            receipts.extend(load_receipts_from_jsonl(path))
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ReceiptValidationError(f"{path}: invalid JSON receipt feed") from exc
        if isinstance(payload, dict):
            validate_receipt(payload, location=str(path))
            receipts.append(payload)
            continue
        if not isinstance(payload, list):
            raise ReceiptValidationError(f"{path}: receipt feed must be a JSON object or array")
        for index, item in enumerate(payload):
            if not isinstance(item, dict):
                raise ReceiptValidationError(f"{path}[{index}]: receipt must be an object")
            validate_receipt(item, location=f"{path}[{index}]")
            receipts.append(item)

    deduped: dict[str, dict[str, Any]] = {}
    for receipt in receipts:
        deduped[receipt["event_id"]] = receipt
    return sorted(deduped.values(), key=receipt_sort_key)


def load_receipts_from_jsonl(path: Path) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ReceiptValidationError(
                f"{path}:{line_number}: invalid JSONL receipt line"
            ) from exc
        if not isinstance(item, dict):
            raise ReceiptValidationError(f"{path}:{line_number}: receipt must be an object")
        validate_receipt(item, location=f"{path}:{line_number}")
        receipts.append(item)
    return receipts


@lru_cache(maxsize=1)
def canonical_envelope_schema() -> dict[str, Any]:
    return load_json_object(
        CANONICAL_ENVELOPE_SCHEMA_PATH,
        label=CANONICAL_ENVELOPE_SCHEMA_REF,
    )


@lru_cache(maxsize=1)
def supported_event_kinds() -> frozenset[str]:
    payload = canonical_envelope_schema()
    properties = payload.get("properties")
    if not isinstance(properties, dict):
        raise ReceiptValidationError(
            f"{CANONICAL_ENVELOPE_SCHEMA_REF}: missing properties object"
        )
    event_kind = properties.get("event_kind")
    if not isinstance(event_kind, dict):
        raise ReceiptValidationError(
            f"{CANONICAL_ENVELOPE_SCHEMA_REF}: missing properties.event_kind object"
        )
    enum = event_kind.get("enum")
    if not isinstance(enum, list) or not enum:
        raise ReceiptValidationError(
            f"{CANONICAL_ENVELOPE_SCHEMA_REF}: properties.event_kind.enum must be a non-empty list"
        )
    supported = {item for item in enum if isinstance(item, str) and item}
    if len(supported) != len(enum):
        raise ReceiptValidationError(
            f"{CANONICAL_ENVELOPE_SCHEMA_REF}: properties.event_kind.enum must contain only non-empty strings"
        )
    return frozenset(supported)


def validate_receipt(receipt: dict[str, Any], *, location: str) -> None:
    required_fields = (
        "event_kind",
        "event_id",
        "observed_at",
        "run_ref",
        "session_ref",
        "actor_ref",
        "object_ref",
        "evidence_refs",
        "payload",
    )
    for field in required_fields:
        if field not in receipt:
            raise ReceiptValidationError(f"{location}: missing field '{field}'")

    for field in ("event_kind", "event_id", "run_ref", "session_ref", "actor_ref"):
        if not isinstance(receipt[field], str) or not receipt[field]:
            raise ReceiptValidationError(f"{location}.{field}: must be a non-empty string")
    if receipt["event_kind"] not in supported_event_kinds():
        raise ReceiptValidationError(
            f"{location}.event_kind: unsupported event kind {receipt['event_kind']!r}; "
            f"see {CANONICAL_ENVELOPE_SCHEMA_REF}"
        )

    try:
        datetime.fromisoformat(receipt["observed_at"].replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ReceiptValidationError(
            f"{location}.observed_at: must be an ISO datetime"
        ) from exc

    object_ref = receipt["object_ref"]
    if not isinstance(object_ref, dict):
        raise ReceiptValidationError(f"{location}.object_ref: must be an object")
    for field in ("repo", "kind", "id"):
        if not isinstance(object_ref.get(field), str) or not object_ref[field]:
            raise ReceiptValidationError(
                f"{location}.object_ref.{field}: must be a non-empty string"
            )

    evidence_refs = receipt["evidence_refs"]
    if not isinstance(evidence_refs, list):
        raise ReceiptValidationError(f"{location}.evidence_refs: must be a list")
    for index, item in enumerate(evidence_refs):
        if not isinstance(item, dict):
            raise ReceiptValidationError(
                f"{location}.evidence_refs[{index}]: must be an object"
            )
        for field in ("kind", "ref"):
            if not isinstance(item.get(field), str) or not item[field]:
                raise ReceiptValidationError(
                    f"{location}.evidence_refs[{index}].{field}: must be a non-empty string"
                )

    if not isinstance(receipt["payload"], dict):
        raise ReceiptValidationError(f"{location}.payload: must be an object")
    supersedes = receipt.get("supersedes")
    if supersedes is not None and (not isinstance(supersedes, str) or not supersedes):
        raise ReceiptValidationError(f"{location}.supersedes: must be omitted or a non-empty string")


def resolve_active_receipts(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    receipt_by_id = {receipt["event_id"]: receipt for receipt in receipts}
    supersedes_by_id = {
        receipt["event_id"]: receipt["supersedes"]
        for receipt in receipts
        if isinstance(receipt.get("supersedes"), str)
        and receipt["supersedes"] in receipt_by_id
        and receipt["supersedes"] != receipt["event_id"]
    }
    cycle_nodes = find_supersedes_cycle_nodes(supersedes_by_id)
    effective_supersedes = {
        event_id: target_id
        for event_id, target_id in supersedes_by_id.items()
        if event_id not in cycle_nodes and target_id not in cycle_nodes
    }

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        family_root = resolve_receipt_family_root(receipt["event_id"], effective_supersedes)
        grouped[family_root].append(receipt)

    active = [max(group, key=receipt_sort_key) for group in grouped.values()]
    return sorted(active, key=receipt_sort_key)


def find_supersedes_cycle_nodes(supersedes_by_id: dict[str, str]) -> set[str]:
    cycle_nodes: set[str] = set()
    seen_done: set[str] = set()

    for start in supersedes_by_id:
        if start in seen_done:
            continue
        order: list[str] = []
        positions: dict[str, int] = {}
        current = start
        while current in supersedes_by_id:
            if current in seen_done:
                break
            if current in positions:
                cycle_nodes.update(order[positions[current] :])
                break
            positions[current] = len(order)
            order.append(current)
            current = supersedes_by_id[current]
        seen_done.update(order)

    return cycle_nodes


def resolve_receipt_family_root(event_id: str, supersedes_by_id: dict[str, str]) -> str:
    current = event_id
    while current in supersedes_by_id:
        current = supersedes_by_id[current]
    return current


def generated_from(receipts: list[dict[str, Any]], input_paths: list[str]) -> dict[str, Any]:
    latest_observed_at = max(receipt["observed_at"] for receipt in receipts)
    return {
        "receipt_input_paths": input_paths,
        "total_receipts": len(receipts),
        "latest_observed_at": latest_observed_at,
    }


@lru_cache(maxsize=1)
def load_event_kind_registry(
    path: Path = EVENT_KIND_REGISTRY_PATH,
) -> dict[str, Any]:
    return load_json_object(path, label=EVENT_KIND_REGISTRY_REF)


def active_registry_event_kinds(registry: dict[str, Any] | None = None) -> list[str]:
    payload = registry or load_event_kind_registry()
    entries = payload.get("event_kinds")
    if not isinstance(entries, list):
        raise ReceiptValidationError(
            f"{EVENT_KIND_REGISTRY_REF}: event_kinds must be a list"
        )
    active: list[str] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ReceiptValidationError(
                f"{EVENT_KIND_REGISTRY_REF}: event_kinds[{index}] must be an object"
            )
        kind = entry.get("event_kind")
        if not isinstance(kind, str) or not kind:
            raise ReceiptValidationError(
                f"{EVENT_KIND_REGISTRY_REF}: event_kinds[{index}].event_kind must be a non-empty string"
            )
        if entry.get("status") == "active":
            active.append(kind)
    return active


def normalize_schema_for_mirror_compare(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in payload.items()
        if key not in ALLOWED_MIRROR_METADATA_KEYS
    }


def validate_receipt_abi_governance(
    *,
    repo_root: Path | None = None,
    workspace_root: Path | None = None,
) -> list[str]:
    root = (repo_root or REPO_ROOT).resolve()
    federation_root = (workspace_root or root.parent).resolve()
    errors: list[str] = []

    schema_payload = load_json_object(
        root / CANONICAL_ENVELOPE_SCHEMA_REF,
        label=CANONICAL_ENVELOPE_SCHEMA_REF,
    )
    registry_payload = load_json_object(
        root / EVENT_KIND_REGISTRY_REF,
        label=EVENT_KIND_REGISTRY_REF,
    )

    registry_version = registry_payload.get("schema_version")
    if registry_version != 1:
        errors.append(
            f"{EVENT_KIND_REGISTRY_REF}: unsupported schema_version {registry_version!r}"
        )

    entries = registry_payload.get("event_kinds")
    if not isinstance(entries, list) or not entries:
        errors.append(f"{EVENT_KIND_REGISTRY_REF}: event_kinds must be a non-empty list")
    else:
        seen: set[str] = set()
        active_order: list[str] = []
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                errors.append(f"{EVENT_KIND_REGISTRY_REF}: event_kinds[{index}] must be an object")
                continue
            kind = entry.get("event_kind")
            status = entry.get("status")
            owner = entry.get("payload_owner_repo")
            surfaces = entry.get("summary_surface_names")
            if not isinstance(kind, str) or not kind:
                errors.append(
                    f"{EVENT_KIND_REGISTRY_REF}: event_kinds[{index}].event_kind must be a non-empty string"
                )
                continue
            if kind in seen:
                errors.append(f"{EVENT_KIND_REGISTRY_REF}: duplicate event_kind {kind!r}")
            seen.add(kind)
            if status not in {"active", "deprecated", "reserved"}:
                errors.append(
                    f"{EVENT_KIND_REGISTRY_REF}: event_kinds[{index}].status must be active, deprecated, or reserved"
                )
            if not isinstance(owner, str) or not owner:
                errors.append(
                    f"{EVENT_KIND_REGISTRY_REF}: event_kinds[{index}].payload_owner_repo must be a non-empty string"
                )
            if not isinstance(surfaces, list) or any(
                not isinstance(item, str) or not item for item in surfaces
            ):
                errors.append(
                    f"{EVENT_KIND_REGISTRY_REF}: event_kinds[{index}].summary_surface_names must be a list of non-empty strings"
                )
            if status == "active":
                active_order.append(kind)

        schema_enum = schema_payload.get("properties", {}).get("event_kind", {}).get("enum")
        if not isinstance(schema_enum, list) or not schema_enum:
            errors.append(
                f"{CANONICAL_ENVELOPE_SCHEMA_REF}: properties.event_kind.enum must be a non-empty list"
            )
        else:
            schema_active = [item for item in schema_enum if isinstance(item, str) and item]
            if schema_active != active_order:
                errors.append(
                    "active registry event kinds must match the canonical schema enum order exactly"
                )

    mirror_path = federation_root / "aoa-evals" / "schemas" / "stats-event-envelope.schema.json"
    if mirror_path.exists():
        mirror_payload = load_json_object(mirror_path, label=str(mirror_path))
        if normalize_schema_for_mirror_compare(schema_payload) != normalize_schema_for_mirror_compare(
            mirror_payload
        ):
            errors.append(
                f"{mirror_path}: local mirror drifted from {CANONICAL_ENVELOPE_SCHEMA_REF}"
            )

    return errors
