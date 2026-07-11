from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from .read_model_values import is_nonempty_string, parse_iso_datetime
from .receipt_abi import ReceiptValidationError


CAMPAIGN_STATES = ("open", "paused", "closed", "review_required")
REVIEW_STATUSES = (
    "review_required",
    "accepted",
    "reanchor",
    "rollback_considered",
    "closed",
)
REVIEW_DECISIONS = (
    "stay_course",
    "reanchor_then_regenerate",
    "prepare_bounded_rollback",
    "split_campaign",
    "safe_stop",
)
ROLLBACK_STATUSES = ("ready_if_needed", "armed", "executed", "retired")
DRIFT_SIGNAL_NAMES = (
    "path_drift",
    "trust_drift",
    "hook_drift",
    "mcp_drift",
    "marketplace_drift",
)

CAMPAIGN_REF_RE = re.compile(r"^CAMP-\d{8}-[a-z0-9-]+-\d{2}$")
REVIEW_REF_RE = re.compile(r"^DREV-\d{8}-[a-z0-9-]+-\d{2}$")
ROLLBACK_REF_RE = re.compile(r"^RFU-\d{8}-[a-z0-9-]+-\d{2}$")
ROLLOUT_REF_RE = re.compile(r"^ROLL-\d{8}-[a-z0-9-]+-\d{2}$")
ROLLOUT_CADENCE_INPUT_REFS = (
    "8Dionysus/examples/rollout_campaign_window.example.json",
    "8Dionysus/examples/drift_review_window.example.json",
    "8Dionysus/examples/rollback_followthrough_window.example.json",
)

CAMPAIGN_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "campaign_ref",
        "workspace_root",
        "plane",
        "scope",
        "state",
        "cadence_policy",
        "rollout_campaign_refs",
        "latest_rollout_campaign_ref",
        "latest_stable_rollout_campaign_ref",
        "window_opened_at",
        "next_review_due_at",
        "source_refs",
        "owner_surface",
    }
)
CAMPAIGN_ALLOWED_FIELDS = CAMPAIGN_REQUIRED_FIELDS | {"lineage_refs"}
REVIEW_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "review_ref",
        "campaign_ref",
        "status",
        "signals",
        "decision",
        "evidence_refs",
        "rollback_anchor",
        "reviewed_at",
        "source_refs",
    }
)
ROLLBACK_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "rollback_ref",
        "campaign_ref",
        "status",
        "trigger_conditions",
        "rollback_anchor",
        "bounded_scope",
        "post_rollback_review",
        "prepared_at",
        "source_refs",
    }
)
CADENCE_POLICY_FIELDS = frozenset(
    {"review_every", "batch_size_goal", "max_open_batches"}
)
LINEAGE_FIELDS = frozenset({"candidate_refs", "seed_refs", "object_refs"})
BOUNDED_SCOPE_FIELDS = frozenset({"paths", "surface"})
SOURCE_FIELDS = frozenset(
    {"receipt_input_paths", "total_receipts", "latest_observed_at"}
)


def _require_fields(
    payload: Mapping[str, Any],
    *,
    required: frozenset[str],
    allowed: frozenset[str] | None = None,
    label: str,
) -> None:
    fields = set(payload)
    missing = required - fields
    if missing:
        raise ReceiptValidationError(
            f"{label} is missing required fields: {', '.join(sorted(missing))}"
        )
    unsupported = fields - (allowed or required)
    if unsupported:
        raise ReceiptValidationError(
            f"{label} has unsupported fields: "
            + ", ".join(sorted(str(field) for field in unsupported))
        )


def _require_mapping(value: Any, *, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ReceiptValidationError(f"{label} must be an object")
    return value


def _require_string(value: Any, *, label: str) -> str:
    if not is_nonempty_string(value):
        raise ReceiptValidationError(f"{label} must be a non-empty string")
    return str(value)


def _require_pattern(value: Any, *, pattern: re.Pattern[str], label: str) -> str:
    normalized = _require_string(value, label=label)
    if pattern.fullmatch(normalized) is None:
        raise ReceiptValidationError(f"{label} must match the published ref grammar")
    return normalized


def _require_bool(value: Any, *, label: str) -> bool:
    if not isinstance(value, bool):
        raise ReceiptValidationError(f"{label} must be boolean")
    return value


def _require_positive_int(value: Any, *, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ReceiptValidationError(f"{label} must be a positive integer")
    return value


def _require_string_sequence(
    value: Any,
    *,
    label: str,
    allow_empty: bool,
    pattern: re.Pattern[str] | None = None,
) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ReceiptValidationError(f"{label} must be a string list")
    items = tuple(value)
    if not allow_empty and not items:
        raise ReceiptValidationError(f"{label} must be a non-empty string list")
    if not all(is_nonempty_string(item) for item in items):
        raise ReceiptValidationError(f"{label} must be a string list")
    normalized = tuple(str(item) for item in items)
    if len(normalized) != len(set(normalized)):
        raise ReceiptValidationError(f"{label} must not contain duplicates")
    if pattern is not None and any(
        pattern.fullmatch(item) is None for item in normalized
    ):
        raise ReceiptValidationError(
            f"{label} entries must match the published ref grammar"
        )
    return normalized


def _require_datetime(value: Any, *, label: str) -> datetime:
    if (
        not isinstance(value, str)
        or re.search(r"[Tt].*(?:[Zz]|[+-]\d{2}:\d{2})$", value) is None
    ):
        raise ReceiptValidationError(f"{label} must be a date-time")
    parsed = parse_iso_datetime(value)
    if parsed is None:
        raise ReceiptValidationError(f"{label} must be a date-time")
    return parsed


def _validate_campaign(campaign: Mapping[str, Any]) -> tuple[datetime, datetime]:
    label = "rollout campaign window"
    _require_fields(
        campaign,
        required=CAMPAIGN_REQUIRED_FIELDS,
        allowed=CAMPAIGN_ALLOWED_FIELDS,
        label=label,
    )
    if campaign.get("schema_version") != "8dionysus_rollout_campaign_window_v1":
        raise ReceiptValidationError(f"{label} must keep its published v1 schema")
    _require_pattern(
        campaign.get("campaign_ref"),
        pattern=CAMPAIGN_REF_RE,
        label=f"{label} campaign_ref",
    )
    _require_string(campaign.get("workspace_root"), label=f"{label} workspace_root")
    if campaign.get("plane") != "codex_plane":
        raise ReceiptValidationError(f"{label} plane must stay codex_plane")
    _require_string(campaign.get("scope"), label=f"{label} scope")
    if campaign.get("state") not in CAMPAIGN_STATES:
        raise ReceiptValidationError(f"{label} state is outside the published grammar")

    policy = _require_mapping(
        campaign.get("cadence_policy"), label=f"{label} cadence_policy"
    )
    _require_fields(
        policy, required=CADENCE_POLICY_FIELDS, label=f"{label} cadence_policy"
    )
    _require_string(
        policy.get("review_every"), label=f"{label} cadence_policy.review_every"
    )
    _require_positive_int(
        policy.get("batch_size_goal"),
        label=f"{label} cadence_policy.batch_size_goal",
    )
    _require_positive_int(
        policy.get("max_open_batches"),
        label=f"{label} cadence_policy.max_open_batches",
    )

    lineage = campaign.get("lineage_refs")
    if lineage is not None:
        lineage_mapping = _require_mapping(lineage, label=f"{label} lineage_refs")
        _require_fields(
            lineage_mapping, required=LINEAGE_FIELDS, label=f"{label} lineage_refs"
        )
        for name in sorted(LINEAGE_FIELDS):
            _require_string_sequence(
                lineage_mapping.get(name),
                label=f"{label} lineage_refs.{name}",
                allow_empty=True,
            )

    rollout_refs = _require_string_sequence(
        campaign.get("rollout_campaign_refs"),
        label=f"{label} rollout_campaign_refs",
        allow_empty=False,
        pattern=ROLLOUT_REF_RE,
    )
    latest_ref = _require_pattern(
        campaign.get("latest_rollout_campaign_ref"),
        pattern=ROLLOUT_REF_RE,
        label=f"{label} latest_rollout_campaign_ref",
    )
    stable_ref = _require_pattern(
        campaign.get("latest_stable_rollout_campaign_ref"),
        pattern=ROLLOUT_REF_RE,
        label=f"{label} latest_stable_rollout_campaign_ref",
    )
    if latest_ref not in rollout_refs:
        raise ReceiptValidationError(
            f"{label} latest rollout ref must belong to rollout_campaign_refs"
        )
    if stable_ref not in rollout_refs:
        raise ReceiptValidationError(
            f"{label} latest stable ref must belong to rollout_campaign_refs"
        )

    opened_at = _require_datetime(
        campaign.get("window_opened_at"), label=f"{label} window_opened_at"
    )
    next_review_at = _require_datetime(
        campaign.get("next_review_due_at"), label=f"{label} next_review_due_at"
    )
    if next_review_at <= opened_at:
        raise ReceiptValidationError(
            f"{label} next review must follow the window opening"
        )
    _require_string_sequence(
        campaign.get("source_refs"),
        label=f"{label} source_refs",
        allow_empty=False,
    )
    _require_string(campaign.get("owner_surface"), label=f"{label} owner_surface")
    return opened_at, next_review_at


def _validate_review(review: Mapping[str, Any]) -> datetime:
    label = "drift review window"
    _require_fields(review, required=REVIEW_REQUIRED_FIELDS, label=label)
    if review.get("schema_version") != "8dionysus_drift_review_window_v1":
        raise ReceiptValidationError(f"{label} must keep its published v1 schema")
    _require_pattern(
        review.get("review_ref"), pattern=REVIEW_REF_RE, label=f"{label} review_ref"
    )
    _require_pattern(
        review.get("campaign_ref"),
        pattern=CAMPAIGN_REF_RE,
        label=f"{label} campaign_ref",
    )
    if review.get("status") not in REVIEW_STATUSES:
        raise ReceiptValidationError(f"{label} status is outside the published grammar")
    signals = _require_mapping(review.get("signals"), label=f"{label} signals")
    _require_fields(
        signals, required=frozenset(DRIFT_SIGNAL_NAMES), label=f"{label} signals"
    )
    normalized_signals = tuple(
        _require_bool(signals.get(name), label=f"{label} signals.{name}")
        for name in DRIFT_SIGNAL_NAMES
    )
    if not any(normalized_signals):
        raise ReceiptValidationError(f"{label} must name at least one positive signal")
    if review.get("decision") not in REVIEW_DECISIONS:
        raise ReceiptValidationError(
            f"{label} decision is outside the published grammar"
        )
    _require_string_sequence(
        review.get("evidence_refs"),
        label=f"{label} evidence_refs",
        allow_empty=False,
    )
    _require_pattern(
        review.get("rollback_anchor"),
        pattern=ROLLOUT_REF_RE,
        label=f"{label} rollback_anchor",
    )
    reviewed_at = _require_datetime(
        review.get("reviewed_at"), label=f"{label} reviewed_at"
    )
    _require_string_sequence(
        review.get("source_refs"), label=f"{label} source_refs", allow_empty=False
    )
    if review.get("decision") == "reanchor_then_regenerate" and review.get(
        "status"
    ) not in {"review_required", "reanchor"}:
        raise ReceiptValidationError(
            f"{label} reanchor_then_regenerate requires review_required or reanchor"
        )
    return reviewed_at


def _validate_rollback(rollback: Mapping[str, Any]) -> datetime:
    label = "rollback followthrough window"
    _require_fields(rollback, required=ROLLBACK_REQUIRED_FIELDS, label=label)
    if rollback.get("schema_version") != "8dionysus_rollback_followthrough_window_v1":
        raise ReceiptValidationError(f"{label} must keep its published v1 schema")
    _require_pattern(
        rollback.get("rollback_ref"),
        pattern=ROLLBACK_REF_RE,
        label=f"{label} rollback_ref",
    )
    _require_pattern(
        rollback.get("campaign_ref"),
        pattern=CAMPAIGN_REF_RE,
        label=f"{label} campaign_ref",
    )
    if rollback.get("status") not in ROLLBACK_STATUSES:
        raise ReceiptValidationError(f"{label} status is outside the published grammar")
    _require_string_sequence(
        rollback.get("trigger_conditions"),
        label=f"{label} trigger_conditions",
        allow_empty=False,
    )
    _require_pattern(
        rollback.get("rollback_anchor"),
        pattern=ROLLOUT_REF_RE,
        label=f"{label} rollback_anchor",
    )
    bounded_scope = _require_mapping(
        rollback.get("bounded_scope"), label=f"{label} bounded_scope"
    )
    _require_fields(
        bounded_scope, required=BOUNDED_SCOPE_FIELDS, label=f"{label} bounded_scope"
    )
    _require_string_sequence(
        bounded_scope.get("paths"),
        label=f"{label} bounded_scope.paths",
        allow_empty=False,
    )
    _require_string(
        bounded_scope.get("surface"), label=f"{label} bounded_scope.surface"
    )
    if rollback.get("post_rollback_review") not in {"required", "optional"}:
        raise ReceiptValidationError(
            f"{label} post_rollback_review is outside the published grammar"
        )
    prepared_at = _require_datetime(
        rollback.get("prepared_at"), label=f"{label} prepared_at"
    )
    _require_string_sequence(
        rollback.get("source_refs"),
        label=f"{label} source_refs",
        allow_empty=False,
    )
    if (
        rollback.get("status") == "ready_if_needed"
        and rollback.get("post_rollback_review") != "required"
    ):
        raise ReceiptValidationError(
            f"{label} ready_if_needed requires post_rollback_review=required"
        )
    return prepared_at


def validate_rollout_cadence_chain(
    campaign: Mapping[str, Any],
    review: Mapping[str, Any],
    rollback: Mapping[str, Any],
) -> datetime:
    opened_at, _ = _validate_campaign(campaign)
    reviewed_at = _validate_review(review)
    prepared_at = _validate_rollback(rollback)

    campaign_ref = campaign["campaign_ref"]
    if review["campaign_ref"] != campaign_ref:
        raise ReceiptValidationError(
            "drift review window must reference the loaded campaign window"
        )
    if rollback["campaign_ref"] != campaign_ref:
        raise ReceiptValidationError(
            "rollback followthrough window must reference the loaded campaign window"
        )
    stable_ref = campaign["latest_stable_rollout_campaign_ref"]
    if review["rollback_anchor"] != stable_ref:
        raise ReceiptValidationError(
            "drift review rollback anchor must reference the campaign stable rollout"
        )
    if rollback["rollback_anchor"] != stable_ref:
        raise ReceiptValidationError(
            "rollback followthrough anchor must reference the campaign stable rollout"
        )
    if not opened_at <= reviewed_at <= prepared_at:
        raise ReceiptValidationError(
            "campaign, review, and rollback timestamps must follow the bounded flow"
        )
    return prepared_at


def _validate_source(
    source: Mapping[str, Any], *, latest_observed_at: datetime
) -> tuple[str, ...]:
    label = "rollout cadence generated_from"
    _require_fields(source, required=SOURCE_FIELDS, label=label)
    paths = _require_string_sequence(
        source.get("receipt_input_paths"),
        label=f"{label} receipt_input_paths",
        allow_empty=False,
    )
    if paths != ROLLOUT_CADENCE_INPUT_REFS:
        raise ReceiptValidationError(
            f"{label} must keep the canonical three owner-example refs"
        )
    total_receipts = source.get("total_receipts")
    if not isinstance(total_receipts, int) or isinstance(total_receipts, bool):
        raise ReceiptValidationError(f"{label} total_receipts must be an integer")
    if total_receipts != 1:
        raise ReceiptValidationError(f"{label} must describe one cadence chain")
    source_latest = _require_datetime(
        source.get("latest_observed_at"), label=f"{label} latest_observed_at"
    )
    if source_latest != latest_observed_at:
        raise ReceiptValidationError(
            f"{label} latest_observed_at must match the rollback preparation"
        )
    return paths


def build_rollout_campaign_summary(
    source: Mapping[str, Any],
    campaign: Mapping[str, Any],
    review: Mapping[str, Any],
    rollback: Mapping[str, Any],
) -> dict[str, Any]:
    latest_observed_at = validate_rollout_cadence_chain(campaign, review, rollback)
    source_paths = _validate_source(source, latest_observed_at=latest_observed_at)
    lineage = campaign.get("lineage_refs")
    lineage_mapping = lineage if isinstance(lineage, Mapping) else {}
    review_status = str(review["status"])
    rollback_status = str(rollback["status"])
    return {
        "schema_version": "aoa_stats_rollout_campaign_summary_v1",
        "generated_from": {
            "receipt_input_paths": list(source_paths),
            "total_receipts": 1,
            "latest_observed_at": latest_observed_at.isoformat().replace("+00:00", "Z"),
        },
        "campaign_ref": str(campaign["campaign_ref"]),
        "campaign_state": str(campaign["state"]),
        "open_batches": int(campaign["state"] == "open"),
        "pending_reviews": int(
            review_status in {"review_required", "reanchor", "rollback_considered"}
        ),
        "rollback_ready_windows": int(rollback_status in {"ready_if_needed", "armed"}),
        "stage_counts": {
            "candidate_refs": len(tuple(lineage_mapping.get("candidate_refs", ()))),
            "seed_refs": len(tuple(lineage_mapping.get("seed_refs", ()))),
            "object_refs": len(tuple(lineage_mapping.get("object_refs", ()))),
        },
        "source_refs": list(source_paths),
    }


def build_drift_review_summary(
    source: Mapping[str, Any],
    campaign: Mapping[str, Any],
    review: Mapping[str, Any],
    rollback: Mapping[str, Any],
) -> dict[str, Any]:
    latest_observed_at = validate_rollout_cadence_chain(campaign, review, rollback)
    source_paths = _validate_source(source, latest_observed_at=latest_observed_at)
    signals = review["signals"]
    decision = str(review["decision"])
    rollback_status = str(rollback["status"])
    return {
        "schema_version": "aoa_stats_drift_review_summary_v1",
        "generated_from": {
            "receipt_input_paths": list(source_paths),
            "total_receipts": 1,
            "latest_observed_at": latest_observed_at.isoformat().replace("+00:00", "Z"),
        },
        "campaign_ref": str(campaign["campaign_ref"]),
        "review_ref": str(review["review_ref"]),
        "review_status": str(review["status"]),
        "review_windows_total": 1,
        "signals_seen": {
            name: int(signals[name] is True) for name in sorted(DRIFT_SIGNAL_NAMES)
        },
        "decision_counts": {decision: 1},
        "rollback_ref": str(rollback["rollback_ref"]),
        "rollback_ready": rollback_status in {"ready_if_needed", "armed"},
        "source_refs": list(source_paths),
    }
