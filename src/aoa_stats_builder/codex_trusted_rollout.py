from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from .read_model_values import is_nonempty_string, parse_iso_datetime
from .receipt_abi import ReceiptValidationError


ROLLOUT_REF_RE = re.compile(r"^ROLL-\d{8}-[a-z0-9-]+-\d{2}$")
DEPLOY_REF_RE = re.compile(r"^DEPLOY-\d{8}-[a-z0-9-]+-\d{2}$")
DRIFT_REF_RE = re.compile(r"^DRIFT-\d{8}-[a-z0-9-]+-\d{2}$")
ROLLBACK_REF_RE = re.compile(r"^RBK-\d{8}-[a-z0-9-]+-\d{2}$")

ROLLOUT_STATES = frozenset(
    {
        "prepared",
        "activated",
        "monitoring",
        "stabilized",
        "rollback_open",
        "rolled_back",
        "abandoned",
    }
)
DRIFT_STATES = frozenset(
    {
        "quiet",
        "watch",
        "material",
        "repairing",
        "resolved",
        "rolled_back",
    }
)
TRUSTED_ROLLOUT_LATEST_SOURCE_REFS = (
    "generated/codex/rollout/deploy_history.jsonl",
    "generated/codex/rollout/regeneration_campaigns.min.json",
    "generated/codex/rollout/rollback_windows.min.json",
)
CODEX_TRUSTED_ROLLOUT_INPUT_REFS = (
    "8Dionysus/generated/codex/rollout/deploy_history.jsonl",
    "8Dionysus/generated/codex/rollout/regeneration_campaigns.min.json",
    "8Dionysus/generated/codex/rollout/rollback_windows.min.json",
    "8Dionysus/generated/codex/rollout/rollout_latest.min.json",
)


def _require_mapping(value: Any, *, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ReceiptValidationError(f"{label} must be an object")
    return value


def _require_string(value: Any, *, label: str) -> str:
    if not is_nonempty_string(value):
        raise ReceiptValidationError(f"{label} must be a non-empty string")
    return str(value)


def _require_bool(value: Any, *, label: str) -> bool:
    if not isinstance(value, bool):
        raise ReceiptValidationError(f"{label} must be boolean")
    return value


def _require_ref(value: Any, *, label: str, pattern: re.Pattern[str]) -> str:
    ref = _require_string(value, label=label)
    if pattern.fullmatch(ref) is None:
        raise ReceiptValidationError(f"{label} must match {pattern.pattern}")
    return ref


def _require_sequence(
    value: Any,
    *,
    label: str,
    allow_empty: bool,
) -> tuple[Any, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ReceiptValidationError(f"{label} must be a list")
    items = tuple(value)
    if not allow_empty and not items:
        raise ReceiptValidationError(f"{label} must be a non-empty list")
    return items


def _require_ref_sequence(
    value: Any,
    *,
    label: str,
    pattern: re.Pattern[str],
    allow_empty: bool,
) -> tuple[str, ...]:
    return tuple(
        _require_ref(item, label=f"{label}[{index}]", pattern=pattern)
        for index, item in enumerate(
            _require_sequence(value, label=label, allow_empty=allow_empty)
        )
    )


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


def _suffix_after_prefix(value: str) -> str:
    return value.split("-", 1)[1]


def _require_optional_ref(
    value: Any,
    *,
    label: str,
    pattern: re.Pattern[str],
) -> str | None:
    if value is None:
        return None
    return _require_ref(value, label=label, pattern=pattern)


def _validate_history(
    deploy_history: Sequence[Mapping[str, Any]],
) -> tuple[list[str], set[str], set[str], set[str], list[datetime]]:
    rows = _require_sequence(
        deploy_history,
        label="Codex trusted rollout deploy history",
        allow_empty=False,
    )
    campaign_refs: list[str] = []
    drift_refs: set[str] = set()
    rollback_refs: set[str] = set()
    stabilized_refs: set[str] = set()
    observed_at: list[datetime] = []

    for index, raw_row in enumerate(rows):
        label = f"Codex trusted rollout deploy history[{index}]"
        row = _require_mapping(raw_row, label=label)
        if row.get("schema_version") != "8dionysus_codex_trusted_rollout_entry_v1":
            raise ReceiptValidationError(
                f"{label} must keep its published entry schema"
            )
        campaign_ref = _require_ref(
            row.get("rollout_campaign_ref"),
            label=f"{label} rollout_campaign_ref",
            pattern=ROLLOUT_REF_RE,
        )
        deploy_refs = _require_ref_sequence(
            row.get("deploy_receipt_refs"),
            label=f"{label} deploy_receipt_refs",
            pattern=DEPLOY_REF_RE,
            allow_empty=False,
        )
        row_drift_refs = _require_ref_sequence(
            row.get("drift_window_refs"),
            label=f"{label} drift_window_refs",
            pattern=DRIFT_REF_RE,
            allow_empty=False,
        )
        row_rollback_refs = _require_ref_sequence(
            row.get("rollback_window_refs"),
            label=f"{label} rollback_window_refs",
            pattern=ROLLBACK_REF_RE,
            allow_empty=True,
        )

        state = row.get("state")
        if state not in ROLLOUT_STATES:
            raise ReceiptValidationError(
                f"{label} state is outside the published rollout lifecycle"
            )
        drift_state = row.get("drift_state")
        if drift_state not in DRIFT_STATES:
            raise ReceiptValidationError(
                f"{label} drift_state is outside the published drift lifecycle"
            )
        _require_bool(
            row.get("repair_attempted"),
            label=f"{label} repair_attempted",
        )
        activated_at = row.get("activated_at")
        if activated_at is not None and activated_at != "":
            observed_at.append(
                _require_datetime(
                    activated_at,
                    label=f"{label} activated_at",
                )
            )

        if state in {"rollback_open", "rolled_back"} and not row_rollback_refs:
            raise ReceiptValidationError(
                f"{label} rollback_window_refs must not be empty for {state}"
            )
        if state == "stabilized" and row_rollback_refs:
            raise ReceiptValidationError(
                f"{label} rollback_window_refs must stay empty for stabilized entries"
            )

        expected_suffix = _suffix_after_prefix(campaign_ref)
        for field, refs in (
            ("deploy_receipt_refs", deploy_refs),
            ("drift_window_refs", row_drift_refs),
            ("rollback_window_refs", row_rollback_refs),
        ):
            if any(_suffix_after_prefix(ref) != expected_suffix for ref in refs):
                raise ReceiptValidationError(
                    f"{label} {field} must keep rollout suffix {expected_suffix}"
                )

        campaign_refs.append(campaign_ref)
        drift_refs.update(row_drift_refs)
        rollback_refs.update(row_rollback_refs)
        if state == "stabilized":
            stabilized_refs.add(campaign_ref)

    return campaign_refs, drift_refs, rollback_refs, stabilized_refs, observed_at


def _validate_regeneration(
    regeneration: Mapping[str, Any],
    *,
    history_campaign_refs: Sequence[str],
) -> None:
    label = "Codex trusted rollout regeneration campaigns"
    regeneration = _require_mapping(regeneration, label=label)
    if (
        regeneration.get("schema_version")
        != "8dionysus_codex_trusted_rollout_campaigns_v1"
    ):
        raise ReceiptValidationError(f"{label} must keep its published schema")
    if regeneration.get("owner_repo") != "8Dionysus":
        raise ReceiptValidationError(f"{label} must stay owned by 8Dionysus")
    campaigns = _require_sequence(
        regeneration.get("campaigns"),
        label=f"{label} campaigns",
        allow_empty=False,
    )
    campaign_refs = [
        _require_ref(
            _require_mapping(item, label=f"{label} campaigns[{index}]").get(
                "rollout_campaign_ref"
            ),
            label=f"{label} campaigns[{index}] rollout_campaign_ref",
            pattern=ROLLOUT_REF_RE,
        )
        for index, item in enumerate(campaigns)
    ]
    if sorted(campaign_refs) != sorted(history_campaign_refs):
        raise ReceiptValidationError(
            f"{label} must cover exactly the deploy-history campaign refs"
        )


def _validate_rollback_windows(
    rollback: Mapping[str, Any],
    *,
    history_rollback_refs: set[str],
) -> list[datetime]:
    label = "Codex trusted rollout rollback windows"
    rollback = _require_mapping(rollback, label=label)
    if rollback.get("schema_version") != "8dionysus_codex_trusted_rollback_windows_v1":
        raise ReceiptValidationError(f"{label} must keep its published schema")
    if rollback.get("owner_repo") != "8Dionysus":
        raise ReceiptValidationError(f"{label} must stay owned by 8Dionysus")
    windows = _require_sequence(
        rollback.get("rollback_windows"),
        label=f"{label} rollback_windows",
        allow_empty=True,
    )
    rollback_refs: set[str] = set()
    observed_at: list[datetime] = []
    for index, raw_window in enumerate(windows):
        item_label = f"{label} rollback_windows[{index}]"
        window = _require_mapping(raw_window, label=item_label)
        rollback_refs.add(
            _require_ref(
                window.get("rollback_window_ref"),
                label=f"{item_label} rollback_window_ref",
                pattern=ROLLBACK_REF_RE,
            )
        )
        opened_at = window.get("opened_at")
        if opened_at is not None:
            observed_at.append(
                _require_datetime(opened_at, label=f"{item_label} opened_at")
            )
        closed_at = window.get("closed_at")
        if closed_at is not None:
            observed_at.append(
                _require_datetime(closed_at, label=f"{item_label} closed_at")
            )
    if rollback_refs != history_rollback_refs:
        raise ReceiptValidationError(
            f"{label} must cover exactly the rollback refs named by deploy history"
        )
    return observed_at


def _validate_latest(
    latest: Mapping[str, Any],
    *,
    history_campaign_refs: Sequence[str],
    history_drift_refs: set[str],
    history_rollback_refs: set[str],
    stabilized_refs: set[str],
    final_history_state: Any,
) -> None:
    label = "Codex trusted rollout latest summary"
    latest = _require_mapping(latest, label=label)
    if latest.get("schema_version") != "8dionysus_codex_trusted_rollout_latest_v1":
        raise ReceiptValidationError(f"{label} must keep its published schema")
    if latest.get("owner_repo") != "8Dionysus":
        raise ReceiptValidationError(f"{label} must stay owned by 8Dionysus")
    latest_ref = _require_ref(
        latest.get("latest_rollout_campaign_ref"),
        label=f"{label} latest_rollout_campaign_ref",
        pattern=ROLLOUT_REF_RE,
    )
    if latest_ref != history_campaign_refs[-1]:
        raise ReceiptValidationError(
            f"{label} must point to the final deploy-history entry"
        )
    if latest.get("latest_state") != final_history_state:
        raise ReceiptValidationError(
            f"{label} latest_state must match the final deploy-history state"
        )
    stable_ref = _require_ref(
        latest.get("latest_stable_rollout_campaign_ref"),
        label=f"{label} latest_stable_rollout_campaign_ref",
        pattern=ROLLOUT_REF_RE,
    )
    if stable_ref not in stabilized_refs:
        raise ReceiptValidationError(
            f"{label} latest stable ref must resolve to a stabilized campaign"
        )

    active_drift_ref = _require_optional_ref(
        latest.get("active_drift_window_ref"),
        label=f"{label} active_drift_window_ref",
        pattern=DRIFT_REF_RE,
    )
    if active_drift_ref is not None and active_drift_ref not in history_drift_refs:
        raise ReceiptValidationError(
            f"{label} active drift ref must resolve inside deploy history"
        )
    active_rollback_ref = _require_optional_ref(
        latest.get("active_rollback_window_ref"),
        label=f"{label} active_rollback_window_ref",
        pattern=ROLLBACK_REF_RE,
    )
    if (
        active_rollback_ref is not None
        and active_rollback_ref not in history_rollback_refs
    ):
        raise ReceiptValidationError(
            f"{label} active rollback ref must resolve inside deploy history"
        )

    source_refs = _require_sequence(
        latest.get("source_refs"),
        label=f"{label} source_refs",
        allow_empty=False,
    )
    if tuple(source_refs) != TRUSTED_ROLLOUT_LATEST_SOURCE_REFS:
        raise ReceiptValidationError(
            f"{label} must keep the canonical source_refs order"
        )


def validate_codex_trusted_rollout_chain(
    deploy_history: Sequence[Mapping[str, Any]],
    regeneration: Mapping[str, Any],
    rollback: Mapping[str, Any],
    latest: Mapping[str, Any],
) -> datetime:
    (
        campaign_refs,
        drift_refs,
        rollback_refs,
        stabilized_refs,
        observed_at,
    ) = _validate_history(deploy_history)
    _validate_regeneration(
        regeneration,
        history_campaign_refs=campaign_refs,
    )
    observed_at.extend(
        _validate_rollback_windows(
            rollback,
            history_rollback_refs=rollback_refs,
        )
    )
    final_row = _require_mapping(
        deploy_history[-1],
        label="Codex trusted rollout final deploy-history entry",
    )
    _validate_latest(
        latest,
        history_campaign_refs=campaign_refs,
        history_drift_refs=drift_refs,
        history_rollback_refs=rollback_refs,
        stabilized_refs=stabilized_refs,
        final_history_state=final_row.get("state"),
    )
    if not observed_at:
        raise ReceiptValidationError(
            "Codex trusted rollout history must expose at least one parseable "
            "owner timestamp"
        )
    return max(observed_at)


def _validated_generated_from(
    source: Mapping[str, Any],
    *,
    history_count: int,
    latest_observed_at: datetime,
) -> dict[str, Any]:
    label = "Codex trusted rollout generated_from"
    source = _require_mapping(source, label=label)
    required_fields = {
        "receipt_input_paths",
        "total_receipts",
        "latest_observed_at",
    }
    if set(source) != required_fields:
        raise ReceiptValidationError(
            f"{label} fields must be exactly {sorted(required_fields)!r}"
        )
    input_paths = _require_sequence(
        source.get("receipt_input_paths"),
        label=f"{label} receipt_input_paths",
        allow_empty=False,
    )
    if tuple(input_paths) != CODEX_TRUSTED_ROLLOUT_INPUT_REFS:
        raise ReceiptValidationError(f"{label} must keep the canonical four input refs")
    total_receipts = source.get("total_receipts")
    if (
        not isinstance(total_receipts, int)
        or isinstance(total_receipts, bool)
        or total_receipts != history_count
    ):
        raise ReceiptValidationError(
            f"{label} total_receipts must match deploy-history length"
        )
    source_latest = _require_datetime(
        source.get("latest_observed_at"),
        label=f"{label} latest_observed_at",
    )
    if source_latest != latest_observed_at:
        raise ReceiptValidationError(
            f"{label} latest_observed_at must match the owner-history bundle"
        )
    return {
        "receipt_input_paths": list(input_paths),
        "total_receipts": total_receipts,
        "latest_observed_at": latest_observed_at.isoformat().replace("+00:00", "Z"),
    }


def latest_rollout_history_row(
    deploy_history: Sequence[Mapping[str, Any]],
    latest: Mapping[str, Any],
) -> Mapping[str, Any]:
    latest_ref = latest.get("latest_rollout_campaign_ref")
    for row in reversed(deploy_history):
        if row.get("rollout_campaign_ref") == latest_ref:
            return row
    raise ReceiptValidationError(
        "latest rollout campaign ref does not resolve inside deploy history"
    )


def build_codex_rollout_operations_summary(
    source: Mapping[str, Any],
    deploy_history: Sequence[Mapping[str, Any]],
    regeneration: Mapping[str, Any],
    rollback: Mapping[str, Any],
    latest: Mapping[str, Any],
) -> dict[str, Any]:
    latest_observed_at = validate_codex_trusted_rollout_chain(
        deploy_history,
        regeneration,
        rollback,
        latest,
    )
    generated_from = _validated_generated_from(
        source,
        history_count=len(deploy_history),
        latest_observed_at=latest_observed_at,
    )
    counts_by_state = Counter(str(row["state"]) for row in deploy_history)
    return {
        "schema_version": "aoa_stats_codex_rollout_operations_summary_v1",
        "generated_from": generated_from,
        "latest_rollout_campaign_ref": str(latest["latest_rollout_campaign_ref"]),
        "latest_state": str(latest["latest_state"]),
        "active_drift_window_ref": latest.get("active_drift_window_ref"),
        "active_rollback_window_ref": latest.get("active_rollback_window_ref"),
        "latest_stable_rollout_campaign_ref": str(
            latest["latest_stable_rollout_campaign_ref"]
        ),
        "counts_by_state": dict(sorted(counts_by_state.items())),
        "source_refs": list(latest["source_refs"]),
    }


def build_codex_rollout_drift_summary(
    source: Mapping[str, Any],
    deploy_history: Sequence[Mapping[str, Any]],
    regeneration: Mapping[str, Any],
    rollback: Mapping[str, Any],
    latest: Mapping[str, Any],
) -> dict[str, Any]:
    latest_observed_at = validate_codex_trusted_rollout_chain(
        deploy_history,
        regeneration,
        rollback,
        latest,
    )
    generated_from = _validated_generated_from(
        source,
        history_count=len(deploy_history),
        latest_observed_at=latest_observed_at,
    )
    latest_history = latest_rollout_history_row(deploy_history, latest)
    drift_refs = tuple(latest_history["drift_window_refs"])
    rollback_refs = tuple(latest_history["rollback_window_refs"])
    latest_state = str(latest["latest_state"])
    return {
        "schema_version": "aoa_stats_codex_rollout_drift_summary_v1",
        "generated_from": generated_from,
        "latest_rollout_campaign_ref": str(latest["latest_rollout_campaign_ref"]),
        "drift_window_ref": drift_refs[0] if drift_refs else None,
        "drift_state": str(latest_history["drift_state"]),
        "repair_attempted": bool(latest_history["repair_attempted"]),
        "rollback_required": bool(rollback_refs)
        or latest_state in {"rollback_open", "rolled_back"},
        "source_refs": [
            "8Dionysus/generated/codex/rollout/deploy_history.jsonl",
            "8Dionysus/generated/codex/rollout/rollback_windows.min.json",
        ],
    }
