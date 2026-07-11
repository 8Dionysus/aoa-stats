from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from .read_model_values import is_nonempty_string, parse_iso_datetime
from .receipt_abi import ReceiptValidationError


CONTINUITY_STATUSES = ("active", "reanchor_needed", "reanchored", "closed")
CONTINUITY_MEMORY_SCOPES = (
    "thread",
    "session",
    "repo",
    "project",
    "workspace",
    "ecosystem",
)
CONTINUITY_APPROVAL_MODES = ("required", "conditional", "advisory")
CONTINUITY_WINDOW_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "continuity_ref",
        "revision_window_ref",
        "reanchor_ref",
        "anchor_artifact_ref",
        "continuity_status",
        "agent_id",
        "role",
        "memory_scope",
        "approval_mode",
        "rollback_marker",
        "max_iterations",
    }
)
CONTINUITY_WINDOW_ALLOWED_FIELDS = CONTINUITY_WINDOW_REQUIRED_FIELDS | {"notes"}
CONTINUITY_EVAL_ANCHORS = (
    "aoa-continuity-anchor-integrity",
    "aoa-reflective-revision-boundedness",
    "aoa-self-reanchor-correctness",
)
CONTINUITY_EVAL_PATHS = {
    "aoa-continuity-anchor-integrity": (
        "evals/capability/aoa-continuity-anchor-integrity/EVAL.md"
    ),
    "aoa-reflective-revision-boundedness": (
        "evals/workflow/aoa-reflective-revision-boundedness/EVAL.md"
    ),
    "aoa-self-reanchor-correctness": (
        "evals/boundary/aoa-self-reanchor-correctness/EVAL.md"
    ),
}
CONTINUITY_PLAYBOOK_ID = "AOA-P-0029"
CONTINUITY_PLAYBOOK_REQUIRED_ARTIFACTS = frozenset(
    {
        "continuity_window",
        "reanchor_decision",
        "continuity_writeback_record",
    }
)
CONTINUITY_PLAYBOOK_REQUIRED_RETURN_ANCHORS = frozenset(
    {
        "continuity_window",
        "reanchor_decision",
        "anchor_trace",
    }
)
CONTINUITY_MEMO_REQUIRED_SOURCE_REFS = (
    ("aoa-agents", "self_agency_continuity_window.example.json"),
    ("aoa-playbooks", "self-agency-continuity-cycle/PLAYBOOK.md"),
    ("aoa-evals", "aoa-continuity-anchor-integrity/EVAL.md"),
    ("aoa-evals", "aoa-self-reanchor-correctness/EVAL.md"),
)
CONTINUITY_REANCHOR_FAILURE_RE = re.compile(
    r"\b(?:fail(?:ed|ure)?|never|unable)\b"
    r"|\b(?:could|did|was|were|is|are|has|have|had)\s+not\b"
    r"|\bnot\s+(?:complete(?:d)?|captur(?:e|ed)|record(?:ed)?|return(?:ed)?)\b"
)
CONTINUITY_REANCHOR_SUCCESS_RES = (
    re.compile(r"^(?:captured|recorded|completed)\s+(?:the\s+)?reanchor\b"),
    re.compile(r"^reanchor\s+(?:was\s+)?(?:captured|recorded|completed)\b"),
    re.compile(r"^returned\s+through\s+(?:the\s+)?reanchor\b"),
)


def _require_string_sequence(value: Any, *, label: str) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ReceiptValidationError(f"{label} must be a non-empty string list")
    items = tuple(value)
    if not items or not all(is_nonempty_string(item) for item in items):
        raise ReceiptValidationError(f"{label} must be a non-empty string list")
    normalized = tuple(str(item) for item in items)
    if len(normalized) != len(set(normalized)):
        raise ReceiptValidationError(f"{label} must not contain duplicates")
    return normalized


def _require_reference(value: Any, *, label: str) -> str:
    if not is_nonempty_string(value):
        raise ReceiptValidationError(f"{label} must be a non-empty string")
    return str(value)


def _validated_timeline(
    memo_thread: Mapping[str, Any],
) -> tuple[tuple[Mapping[str, Any], ...], datetime]:
    raw_timeline = memo_thread.get("timeline")
    if not isinstance(raw_timeline, Sequence) or isinstance(
        raw_timeline, (str, bytes)
    ):
        raise ReceiptValidationError(
            "self-agency continuity provenance thread must expose a non-empty timeline"
        )
    if not raw_timeline:
        raise ReceiptValidationError(
            "self-agency continuity provenance thread must expose a non-empty timeline"
        )

    timeline: list[Mapping[str, Any]] = []
    timestamps: list[datetime] = []
    previous_at: datetime | None = None
    for index, item in enumerate(raw_timeline):
        if not isinstance(item, Mapping):
            raise ReceiptValidationError(
                "self-agency continuity provenance thread "
                f"timeline[{index}] must be an object"
            )
        observed_at = parse_iso_datetime(item.get("at"))
        if observed_at is None:
            raise ReceiptValidationError(
                "self-agency continuity provenance thread "
                f"timeline[{index}].at must be a date-time"
            )
        if previous_at is not None and observed_at < previous_at:
            raise ReceiptValidationError(
                "self-agency continuity provenance thread timeline timestamps "
                "must stay ordered"
            )
        if not is_nonempty_string(item.get("action")):
            raise ReceiptValidationError(
                "self-agency continuity provenance thread "
                f"timeline[{index}].action must be a non-empty string"
            )
        previous_at = observed_at
        timestamps.append(observed_at)
        timeline.append(item)

    return tuple(timeline), timestamps[-1]


def _validate_playbook_contract(playbook: Mapping[str, Any]) -> None:
    if playbook.get("id") != CONTINUITY_PLAYBOOK_ID:
        raise ReceiptValidationError(
            f"self-agency continuity playbook must keep id {CONTINUITY_PLAYBOOK_ID}"
        )
    if playbook.get("status") != "experimental":
        raise ReceiptValidationError(
            "self-agency continuity playbook must keep experimental reference posture"
        )
    if playbook.get("scenario") != "self_agency_continuity_cycle":
        raise ReceiptValidationError(
            "self-agency continuity playbook must keep the continuity scenario"
        )
    if playbook.get("fallback_mode") != "review_required":
        raise ReceiptValidationError(
            "self-agency continuity playbook must keep review_required fallback"
        )
    if playbook.get("return_posture") != "artifact_anchor":
        raise ReceiptValidationError(
            "self-agency continuity playbook must keep artifact_anchor return posture"
        )

    expected_artifacts = set(
        _require_string_sequence(
            playbook.get("expected_artifacts"),
            label="self-agency continuity playbook expected_artifacts",
        )
    )
    missing_artifacts = sorted(
        CONTINUITY_PLAYBOOK_REQUIRED_ARTIFACTS - expected_artifacts
    )
    if missing_artifacts:
        raise ReceiptValidationError(
            "self-agency continuity playbook is missing expected artifacts: "
            + ", ".join(missing_artifacts)
        )

    return_anchors = set(
        _require_string_sequence(
            playbook.get("return_anchor_artifacts"),
            label="self-agency continuity playbook return_anchor_artifacts",
        )
    )
    missing_return_anchors = sorted(
        CONTINUITY_PLAYBOOK_REQUIRED_RETURN_ANCHORS - return_anchors
    )
    if missing_return_anchors:
        raise ReceiptValidationError(
            "self-agency continuity playbook is missing return anchors: "
            + ", ".join(missing_return_anchors)
        )

    eval_anchors = _require_string_sequence(
        playbook.get("eval_anchors"),
        label="self-agency continuity playbook eval_anchors",
    )
    if eval_anchors != CONTINUITY_EVAL_ANCHORS:
        raise ReceiptValidationError(
            "self-agency continuity playbook eval_anchors must match the published "
            "continuity anchor set"
        )


def _validate_eval_catalog(eval_catalog: Mapping[str, Any]) -> None:
    if eval_catalog.get("catalog_version") != 1:
        raise ReceiptValidationError("continuity eval catalog must keep version 1")

    eval_entries = eval_catalog.get("evals")
    if not isinstance(eval_entries, Sequence) or isinstance(
        eval_entries, (str, bytes)
    ):
        raise ReceiptValidationError("continuity eval catalog must expose evals")

    required_entries: dict[str, Mapping[str, Any]] = {}
    for index, item in enumerate(eval_entries):
        if not isinstance(item, Mapping):
            continue
        name = item.get("name")
        if name not in CONTINUITY_EVAL_ANCHORS:
            continue
        name_key = str(name)
        if name_key in required_entries:
            raise ReceiptValidationError(
                f"continuity eval catalog must not duplicate anchor {name_key!r}"
            )
        required_entries[name_key] = item

    missing_eval_names = [
        name for name in CONTINUITY_EVAL_ANCHORS if name not in required_entries
    ]
    if missing_eval_names:
        raise ReceiptValidationError(
            "continuity eval catalog is missing continuity anchors: "
            + ", ".join(missing_eval_names)
        )

    for name in CONTINUITY_EVAL_ANCHORS:
        entry = required_entries[name]
        if entry.get("eval_path") != CONTINUITY_EVAL_PATHS[name]:
            raise ReceiptValidationError(
                f"continuity eval anchor {name!r} must keep its canonical eval_path"
            )
        if entry.get("claim_type") != "bounded":
            raise ReceiptValidationError(
                f"continuity eval anchor {name!r} must keep bounded claim_type"
            )
        if entry.get("review_required") is not True:
            raise ReceiptValidationError(
                f"continuity eval anchor {name!r} must keep review_required"
            )
        if entry.get("status") != "draft":
            raise ReceiptValidationError(
                f"continuity eval anchor {name!r} must keep draft reference status"
            )


def validate_continuity_window_reference_chain(
    continuity_window: Mapping[str, Any],
    memo_thread: Mapping[str, Any],
    playbook_contract: Mapping[str, Any],
    eval_catalog: Mapping[str, Any],
) -> datetime:
    continuity_fields = set(continuity_window)
    missing_fields = CONTINUITY_WINDOW_REQUIRED_FIELDS - continuity_fields
    if missing_fields:
        raise ReceiptValidationError(
            "self-agency continuity window example is missing required fields: "
            + ", ".join(sorted(missing_fields))
        )
    extra_fields = continuity_fields - CONTINUITY_WINDOW_ALLOWED_FIELDS
    if extra_fields:
        raise ReceiptValidationError(
            "self-agency continuity window example has unsupported fields: "
            + ", ".join(sorted((str(field) for field in extra_fields)))
        )

    if continuity_window.get("schema_version") != "self_agency_continuity_window_v1":
        raise ReceiptValidationError(
            "self-agency continuity window example must keep schema_version "
            "self_agency_continuity_window_v1"
        )

    continuity_refs = {
        key: _require_reference(
            continuity_window.get(key),
            label=f"self-agency continuity window example {key}",
        )
        for key in (
            "continuity_ref",
            "revision_window_ref",
            "reanchor_ref",
            "anchor_artifact_ref",
        )
    }
    anchor_artifact_ref = continuity_refs["anchor_artifact_ref"]
    if not (
        anchor_artifact_ref.startswith("artifact:")
        or anchor_artifact_ref.startswith("repo:")
    ) or anchor_artifact_ref in {"artifact:", "repo:"}:
        raise ReceiptValidationError(
            "self-agency continuity window example anchor_artifact_ref must point "
            "to a named artifact or repo surface"
        )

    current_status = continuity_window.get("continuity_status")
    if current_status not in CONTINUITY_STATUSES:
        raise ReceiptValidationError(
            "self-agency continuity window example must keep continuity_status "
            "inside the published grammar"
        )
    for key in ("agent_id", "role", "rollback_marker"):
        _require_reference(
            continuity_window.get(key),
            label=f"self-agency continuity window example {key}",
        )
    if continuity_window.get("memory_scope") not in CONTINUITY_MEMORY_SCOPES:
        raise ReceiptValidationError(
            "self-agency continuity window example memory_scope is outside the "
            "published grammar"
        )
    if continuity_window.get("approval_mode") not in CONTINUITY_APPROVAL_MODES:
        raise ReceiptValidationError(
            "self-agency continuity window example approval_mode is outside the "
            "published grammar"
        )
    max_iterations = continuity_window.get("max_iterations")
    if (
        not isinstance(max_iterations, int)
        or isinstance(max_iterations, bool)
        or max_iterations < 1
    ):
        raise ReceiptValidationError(
            "self-agency continuity window example must keep positive max_iterations"
        )
    notes = continuity_window.get("notes")
    if "notes" in continuity_window and not (
        notes is None or isinstance(notes, str)
    ):
        raise ReceiptValidationError(
            "self-agency continuity window example notes must be a string or null"
        )

    for key, expected_value in continuity_refs.items():
        if memo_thread.get(key) != expected_value:
            raise ReceiptValidationError(
                "self-agency continuity provenance thread must preserve the "
                f"{key} from aoa-agents"
            )
    if memo_thread.get("writeback_target") != "provenance_thread":
        raise ReceiptValidationError(
            "self-agency continuity memo example must keep provenance_thread "
            "writeback_target"
        )

    source_refs = _require_string_sequence(
        memo_thread.get("source_refs"),
        label="self-agency continuity provenance thread source_refs",
    )
    for owner_repo, required_suffix in CONTINUITY_MEMO_REQUIRED_SOURCE_REFS:
        if not any(
            ref.startswith(f"repo:{owner_repo}/") and required_suffix in ref
            for ref in source_refs
        ):
            raise ReceiptValidationError(
                "self-agency continuity provenance thread source_refs must cite "
                f"{owner_repo}/{required_suffix}"
            )
    _require_string_sequence(
        memo_thread.get("memory_object_ids"),
        label="self-agency continuity provenance thread memory_object_ids",
    )

    _validate_playbook_contract(playbook_contract)
    _validate_eval_catalog(eval_catalog)
    _, latest_observed_at = _validated_timeline(memo_thread)
    return latest_observed_at


def continuity_reanchor_counts(
    memo_thread: Mapping[str, Any], current_status: str
) -> tuple[int, int]:
    successful = 0
    failed = 0
    timeline = memo_thread.get("timeline")
    if not isinstance(timeline, Sequence) or isinstance(timeline, (str, bytes)):
        return successful, failed
    for item in timeline:
        if not isinstance(item, Mapping):
            continue
        text = re.sub(r"\s+", " ", str(item.get("action") or "").strip().lower())
        if "reanchor" in text and CONTINUITY_REANCHOR_FAILURE_RE.search(text):
            failed += 1
            continue
        if any(pattern.search(text) for pattern in CONTINUITY_REANCHOR_SUCCESS_RES):
            successful += 1

    # Compatibility keeps the second argument, but status is posture rather than
    # occurrence evidence and therefore cannot increment either count.
    _ = current_status
    return successful, failed


def continuity_drift_flags(current_status: str, failed_reanchors: int) -> list[str]:
    flags: list[str] = []
    if current_status == "reanchor_needed":
        flags.append("reanchor_needed")
    if failed_reanchors > 0:
        flags.append("failed_reanchor_present")
    return flags


def build_continuity_window_summary(
    source: Mapping[str, Any],
    continuity_window: Mapping[str, Any],
    memo_thread: Mapping[str, Any],
) -> dict[str, Any]:
    current_status = str(continuity_window.get("continuity_status") or "closed")
    successful_reanchors, failed_reanchors = continuity_reanchor_counts(
        memo_thread, current_status
    )
    revision_window_ref = continuity_window.get("revision_window_ref")
    open_revision_windows = (
        1 if current_status != "closed" and is_nonempty_string(revision_window_ref) else 0
    )
    bounded_revision_count = 1 if is_nonempty_string(revision_window_ref) else 0
    return {
        "schema_version": "aoa_stats_continuity_window_summary_v1",
        "generated_from": {
            "receipt_input_paths": list(source["receipt_input_paths"]),
            "total_receipts": source["total_receipts"],
            "latest_observed_at": source["latest_observed_at"],
        },
        "continuity_ref": str(continuity_window.get("continuity_ref") or ""),
        "current_status": current_status,
        "open_revision_windows": open_revision_windows,
        "successful_reanchors": successful_reanchors,
        "failed_reanchors": failed_reanchors,
        "last_anchor_artifact_ref": str(
            continuity_window.get("anchor_artifact_ref") or ""
        ),
        "drift_flags": continuity_drift_flags(current_status, failed_reanchors),
        "bounded_revision_count": bounded_revision_count,
    }
