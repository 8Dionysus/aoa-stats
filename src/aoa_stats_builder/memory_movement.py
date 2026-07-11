from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any

from .read_model_values import (
    is_nonempty_string,
    parse_iso_datetime_or_min,
    string_count_map,
)
from .receipt_abi import ReceiptValidationError


MEMORY_MOVEMENT_INPUT_REFS = (
    "aoa-memo/generated/memory-objects/memory_object_catalog.min.json",
    "aoa-memo/memo/objects",
    "aoa-memo/memo/intake/reviewed",
    "aoa-memo/memo/intake/receipts",
)
MEMORY_CONSUMER_REFS = (
    "repo:aoa-evals",
    "repo:aoa-kag",
    "repo:aoa-stats",
    "repo:aoa-playbooks",
    "repo:aoa-agents",
)
MEMORY_ROUTE_BOUNDARY = {
    "operation_mode": "read_only",
    "local_candidate_route": "none_without_repo_memo_port",
    "session_evidence_route": ".aoa_session_evidence_until_reviewed_intake",
    "durable_landing_route": "aoa-memo_reviewed_source_patch",
    "mcp_boundary": (
        "aoa_memo_brief_search_status_validate_and_landing_plan_dry_run_only"
    ),
}

ReferencedPayload = tuple[str, Mapping[str, Any]]


def _is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes))


def _referenced_payloads(
    values: Sequence[ReferencedPayload], *, label: str
) -> tuple[ReferencedPayload, ...]:
    normalized: list[ReferencedPayload] = []
    for index, item in enumerate(values):
        if not _is_sequence(item) or len(item) != 2:
            raise ReceiptValidationError(
                f"{label}[{index}] must be a logical ref and JSON object pair"
            )
        ref, payload = item
        if not is_nonempty_string(ref):
            raise ReceiptValidationError(
                f"{label}[{index}] must expose a non-empty logical ref"
            )
        if not isinstance(payload, Mapping):
            raise ReceiptValidationError(f"{label}[{index}] payload must be an object")
        normalized.append((str(ref), payload))
    return tuple(normalized)


def memory_object_recall_status(memory_object: Mapping[str, Any]) -> str:
    lifecycle = memory_object.get("lifecycle")
    if not isinstance(lifecycle, Mapping):
        return "unknown"
    current_recall = lifecycle.get("current_recall")
    if not isinstance(current_recall, Mapping):
        return "unknown"
    status = current_recall.get("status")
    return str(status) if is_nonempty_string(status) else "unknown"


def memory_object_bridge_status(memory_object: Mapping[str, Any]) -> str:
    bridges = memory_object.get("bridges")
    if not isinstance(bridges, Mapping):
        return "absent"
    status = bridges.get("kag_lift_status")
    return str(status) if is_nonempty_string(status) else "unknown"


def memory_object_datetime(memory_object: Mapping[str, Any], key: str) -> datetime:
    time_payload = memory_object.get("time")
    if not isinstance(time_payload, Mapping):
        return datetime.min.replace(tzinfo=UTC)
    return parse_iso_datetime_or_min(time_payload.get(key))


def _validated_memory_movement_inputs(
    catalog: Mapping[str, Any],
    memory_objects: Sequence[ReferencedPayload],
    reviewed_intakes: Sequence[ReferencedPayload],
    landing_receipts: Sequence[ReferencedPayload],
) -> tuple[
    tuple[Mapping[str, Any], ...],
    tuple[ReferencedPayload, ...],
    tuple[ReferencedPayload, ...],
    tuple[ReferencedPayload, ...],
    datetime,
]:
    if catalog.get("source_of_truth") != "aoa-memo-object-read-models-v2":
        raise ReceiptValidationError(
            "aoa-memo memory object catalog must keep source_of_truth "
            "aoa-memo-object-read-models-v2"
        )
    raw_catalog_objects = catalog.get("memory_objects")
    if not _is_sequence(raw_catalog_objects):
        raise ReceiptValidationError(
            "aoa-memo memory object min catalog must expose memory_objects"
        )
    catalog_objects = tuple(
        item for item in raw_catalog_objects if isinstance(item, Mapping)
    )
    normalized_objects = _referenced_payloads(
        memory_objects, label="reviewed memory objects"
    )
    normalized_intakes = _referenced_payloads(
        reviewed_intakes, label="reviewed intake packets"
    )
    normalized_receipts = _referenced_payloads(
        landing_receipts, label="landing receipts"
    )

    object_ids: list[str] = []
    for object_ref, memory_object in normalized_objects:
        object_id = memory_object.get("id")
        if not is_nonempty_string(object_id):
            raise ReceiptValidationError(
                f"reviewed memory object is missing id: {object_ref}"
            )
        object_ids.append(str(object_id))

    catalog_reviewed_ids: list[str] = []
    for index, item in enumerate(catalog_objects):
        if item.get("source_kind") != "reviewed_corpus":
            continue
        object_id = item.get("id")
        if not is_nonempty_string(object_id):
            raise ReceiptValidationError(
                "aoa-memo reviewed catalog row is missing id: "
                f"memory_objects[{index}]"
            )
        catalog_reviewed_ids.append(str(object_id))

    object_id_set = set(object_ids)
    catalog_reviewed_id_set = set(catalog_reviewed_ids)
    duplicate_object_ids = sorted(
        object_id for object_id, count in Counter(object_ids).items() if count > 1
    )
    duplicate_catalog_ids = sorted(
        object_id
        for object_id, count in Counter(catalog_reviewed_ids).items()
        if count > 1
    )
    if (
        object_id_set != catalog_reviewed_id_set
        or duplicate_object_ids
        or duplicate_catalog_ids
    ):
        missing_in_catalog = sorted(object_id_set - catalog_reviewed_id_set)
        missing_in_objects = sorted(catalog_reviewed_id_set - object_id_set)
        raise ReceiptValidationError(
            "aoa-memo reviewed corpus object/catalog mismatch: "
            f"missing_in_catalog={missing_in_catalog}; "
            f"missing_in_objects={missing_in_objects}; "
            f"duplicate_object_ids={duplicate_object_ids}; "
            f"duplicate_catalog_ids={duplicate_catalog_ids}"
        )

    latest_candidates = [
        memory_object_datetime(memory_object, "observed_at")
        for _, memory_object in normalized_objects
    ]
    latest_candidates.extend(
        parse_iso_datetime_or_min(receipt.get("landed_at"))
        for _, receipt in normalized_receipts
    )
    latest_candidates.extend(
        parse_iso_datetime_or_min(packet.get("created_at"))
        for _, packet in normalized_intakes
    )
    minimum = datetime.min.replace(tzinfo=UTC)
    latest_observed_at = max(latest_candidates or [minimum])
    if latest_observed_at == minimum:
        raise ReceiptValidationError(
            "aoa-memo memory movement inputs have no observable timestamp"
        )

    return (
        catalog_objects,
        normalized_objects,
        normalized_intakes,
        normalized_receipts,
        latest_observed_at,
    )


def validate_memory_movement_inputs(
    catalog: Mapping[str, Any],
    memory_objects: Sequence[ReferencedPayload],
    reviewed_intakes: Sequence[ReferencedPayload],
    landing_receipts: Sequence[ReferencedPayload],
) -> datetime:
    """Validate owner-corpus exactness and return its latest observable time."""

    return _validated_memory_movement_inputs(
        catalog,
        memory_objects,
        reviewed_intakes,
        landing_receipts,
    )[-1]


def _validated_generated_from(
    source: Mapping[str, Any],
    *,
    total_receipts: int,
    latest_observed_at: datetime,
) -> dict[str, Any]:
    required_fields = {
        "receipt_input_paths",
        "total_receipts",
        "latest_observed_at",
    }
    if set(source) != required_fields:
        raise ReceiptValidationError(
            "memory movement generated_from fields must be exactly "
            f"{sorted(required_fields)!r}"
        )
    input_paths = source.get("receipt_input_paths")
    if not _is_sequence(input_paths) or tuple(input_paths) != MEMORY_MOVEMENT_INPUT_REFS:
        raise ReceiptValidationError(
            "memory movement generated_from must keep the canonical four aoa-memo input refs"
        )
    source_total = source.get("total_receipts")
    if (
        not isinstance(source_total, int)
        or isinstance(source_total, bool)
        or source_total != total_receipts
    ):
        raise ReceiptValidationError(
            "memory movement generated_from total_receipts must match the owner bundle"
        )
    source_latest = parse_iso_datetime_or_min(source.get("latest_observed_at"))
    if source_latest != latest_observed_at:
        raise ReceiptValidationError(
            "memory movement generated_from latest_observed_at must match the owner bundle"
        )
    return {
        "receipt_input_paths": list(input_paths),
        "total_receipts": source_total,
        "latest_observed_at": latest_observed_at.isoformat().replace("+00:00", "Z"),
    }


def build_memory_movement_summary(
    source: Mapping[str, Any],
    catalog: Mapping[str, Any],
    memory_objects: Sequence[ReferencedPayload],
    reviewed_intakes: Sequence[ReferencedPayload],
    landing_receipts: Sequence[ReferencedPayload],
) -> dict[str, Any]:
    (
        catalog_objects,
        normalized_objects,
        normalized_intakes,
        normalized_receipts,
        latest_observed_at,
    ) = _validated_memory_movement_inputs(
        catalog,
        memory_objects,
        reviewed_intakes,
        landing_receipts,
    )
    generated_from = _validated_generated_from(
        source,
        total_receipts=(
            len(normalized_objects)
            + len(normalized_intakes)
            + len(normalized_receipts)
        ),
        latest_observed_at=latest_observed_at,
    )

    source_kind_counts: Counter[str] = Counter(
        str(item.get("source_kind") or "unknown") for item in catalog_objects
    )
    kind_counts: Counter[str] = Counter()
    review_state_counts: Counter[str] = Counter()
    recall_status_counts: Counter[str] = Counter()
    temperature_counts: Counter[str] = Counter()
    kag_lift_status_counts: Counter[str] = Counter()
    reviewed_object_rows: list[dict[str, Any]] = []

    for object_ref, memory_object in normalized_objects:
        object_id = str(memory_object["id"])
        kind = str(memory_object.get("kind") or "unknown")
        lifecycle = memory_object.get("lifecycle")
        trust = memory_object.get("trust")
        lifecycle_mapping = lifecycle if isinstance(lifecycle, Mapping) else {}
        trust_mapping = trust if isinstance(trust, Mapping) else {}
        review_state = str(lifecycle_mapping.get("review_state") or "unknown")
        temperature = str(trust_mapping.get("temperature") or "unknown")
        recall_status = memory_object_recall_status(memory_object)
        kag_lift_status = memory_object_bridge_status(memory_object)

        kind_counts[kind] += 1
        review_state_counts[review_state] += 1
        recall_status_counts[recall_status] += 1
        temperature_counts[temperature] += 1
        kag_lift_status_counts[kag_lift_status] += 1
        reviewed_object_rows.append(
            {
                "id": object_id,
                "kind": kind,
                "review_state": review_state,
                "current_recall_status": recall_status,
                "temperature": temperature,
                "kag_lift_status": kag_lift_status,
                "object_ref": object_ref,
            }
        )

    landing_result_counts = Counter(
        str(receipt.get("result") or "unknown")
        for _, receipt in normalized_receipts
    )
    landed_object_refs = sorted(
        {
            str(receipt.get("object_ref"))
            for _, receipt in normalized_receipts
            if is_nonempty_string(receipt.get("object_ref"))
        }
    )

    return {
        "schema_version": "aoa_stats_memory_movement_summary_v1",
        "generated_from": generated_from,
        "authority": {
            "summary_owner": "aoa-stats",
            "memory_owner": "aoa-memo",
            "authority_ceiling": (
                "Derived movement summary only; weaker than aoa-memo reviewed "
                "memory objects, landing receipts, and source refs."
            ),
        },
        "source_kind_counts": string_count_map(source_kind_counts),
        "reviewed_corpus": {
            "object_count": len(normalized_objects),
            "by_kind": string_count_map(kind_counts),
            "by_review_state": string_count_map(review_state_counts),
            "by_recall_status": string_count_map(recall_status_counts),
            "by_temperature": string_count_map(temperature_counts),
            "by_kag_lift_status": string_count_map(kag_lift_status_counts),
            "objects": reviewed_object_rows,
        },
        "reviewed_intake": {
            "packet_count": len(normalized_intakes),
            "landing_receipt_count": len(normalized_receipts),
            "landing_result_counts": string_count_map(landing_result_counts),
            "landed_object_refs": landed_object_refs,
        },
        "consumer_handoff": {
            "consumer_refs": list(MEMORY_CONSUMER_REFS),
            "handoff_memory_ref": (
                "memo.decision.2026-05-22.reviewed-memory-consumer-handoff-spine"
            ),
            "posture": "derived_consumer_summary",
            "memory_route_boundary": dict(MEMORY_ROUTE_BOUNDARY),
        },
    }
