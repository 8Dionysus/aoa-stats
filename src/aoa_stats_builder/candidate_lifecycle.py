from __future__ import annotations

from collections import Counter
from datetime import datetime
from statistics import median
from typing import Any

from .read_model_values import (
    duration_days_between,
    is_nonempty_string,
    normalize_string_list,
    parse_iso_datetime,
    parse_iso_datetime_or_min,
)

FUNNEL_STAGES = (
    "observed",
    "checkpointed",
    "reviewed",
    "harvested",
    "seeded",
    "planted",
    "proved",
    "promoted",
    "superseded_or_dropped",
)
TIME_TO_STAGE_KEYS = (
    "checkpointed",
    "reviewed",
    "harvested",
    "seeded",
    "planted",
    "proved",
    "promoted",
)
AMBIGUOUS_OWNER_TARGETS = {"hold", "unknown", "unresolved"}
OWNER_LANDING_OUTCOMES = (
    "landed_owner_status",
    "landed_owner_object",
    "reanchored",
    "merged",
    "deferred",
    "dropped",
)


def empty_stage_counts() -> dict[str, int]:
    return {stage: 0 for stage in FUNNEL_STAGES}


def empty_time_to_stage() -> dict[str, float | None]:
    return {stage: None for stage in TIME_TO_STAGE_KEYS}


def normalize_lineage_stages(
    raw_stages: Any, *, fallback_observed_at: str
) -> dict[str, str | None]:
    stages = {stage: None for stage in FUNNEL_STAGES}
    if isinstance(raw_stages, dict):
        for stage in FUNNEL_STAGES:
            timestamp = raw_stages.get(stage)
            if parse_iso_datetime(timestamp) is not None:
                stages[stage] = str(timestamp)
    if (
        stages["observed"] is None
        and parse_iso_datetime(fallback_observed_at) is not None
    ):
        stages["observed"] = fallback_observed_at
    return stages


def lineage_latest_datetime(entry: dict[str, Any]) -> datetime:
    latest = parse_iso_datetime(entry.get("receipt_observed_at"))
    for timestamp in entry["stages"].values():
        current = parse_iso_datetime(timestamp)
        if current is not None and (latest is None or current > latest):
            latest = current
    return latest or datetime.min


def collect_candidate_lineage_entries(
    receipts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    latest_by_candidate: dict[str, dict[str, Any]] = {}
    for receipt in receipts:
        if receipt["event_kind"] != "harvest_packet_receipt":
            continue
        payload = receipt["payload"]
        evidence_density = payload.get("evidence_density_summary") or payload.get(
            "evidence_density"
        )
        if evidence_density != "reviewed":
            continue
        raw_entries = payload.get("candidate_lineage_entries")
        if not isinstance(raw_entries, list):
            continue
        for item in raw_entries:
            if not isinstance(item, dict):
                continue
            candidate_ref = item.get("candidate_ref")
            if not is_nonempty_string(candidate_ref):
                continue
            owner_hypothesis = item.get("owner_hypothesis")
            owner_shape = item.get("owner_shape")
            status_posture = item.get("status_posture")
            if not (
                is_nonempty_string(owner_hypothesis)
                and is_nonempty_string(owner_shape)
                and is_nonempty_string(status_posture)
            ):
                continue
            normalized = {
                "candidate_ref": candidate_ref,
                "cluster_ref": (
                    item.get("cluster_ref")
                    if is_nonempty_string(item.get("cluster_ref"))
                    else None
                ),
                "owner_hypothesis": owner_hypothesis,
                "owner_shape": owner_shape,
                "nearest_wrong_target": (
                    item.get("nearest_wrong_target")
                    if is_nonempty_string(item.get("nearest_wrong_target"))
                    else None
                ),
                "status_posture": status_posture,
                "axis_pressure": normalize_string_list(item.get("axis_pressure")),
                "supersedes": normalize_string_list(item.get("supersedes")),
                "merged_into": (
                    item.get("merged_into")
                    if is_nonempty_string(item.get("merged_into"))
                    else None
                ),
                "drop_reason": (
                    item.get("drop_reason")
                    if is_nonempty_string(item.get("drop_reason"))
                    else None
                ),
                "evidence_refs": normalize_string_list(item.get("evidence_refs")),
                "stages": normalize_lineage_stages(
                    item.get("stages"), fallback_observed_at=receipt["observed_at"]
                ),
                "receipt_observed_at": receipt["observed_at"],
            }
            previous = latest_by_candidate.get(candidate_ref)
            if previous is None or lineage_latest_datetime(
                normalized
            ) >= lineage_latest_datetime(previous):
                latest_by_candidate[candidate_ref] = normalized
    return sorted(
        latest_by_candidate.values(),
        key=lambda entry: (lineage_latest_datetime(entry), entry["candidate_ref"]),
    )


def median_days(values: list[float]) -> float | None:
    if not values:
        return None
    return round(float(median(values)), 2)


def stage_duration_days(entry: dict[str, Any], stage: str) -> float | None:
    observed = parse_iso_datetime(entry["stages"].get("observed"))
    target = parse_iso_datetime(entry["stages"].get(stage))
    if observed is None or target is None or target < observed:
        return None
    return (target - observed).total_seconds() / 86400


def build_candidate_lineage_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    entries = collect_candidate_lineage_entries(receipts)
    stage_counts = empty_stage_counts()
    owner_target_counts: Counter[str] = Counter()
    owner_shape_counts: Counter[str] = Counter()
    status_posture_counts: Counter[str] = Counter()
    misroute_target_counts: Counter[str] = Counter()
    axis_pressure_counts: Counter[str] = Counter()
    time_to_stage_values: dict[str, list[float]] = {
        stage: [] for stage in TIME_TO_STAGE_KEYS
    }
    owner_ambiguity_total = 0
    superseded_total = 0
    dropped_total = 0

    for entry in entries:
        for stage in FUNNEL_STAGES:
            if entry["stages"].get(stage) is not None:
                stage_counts[stage] += 1

        owner_target_counts[entry["owner_hypothesis"]] += 1
        owner_shape_counts[entry["owner_shape"]] += 1
        status_posture_counts[entry["status_posture"]] += 1
        if entry["owner_hypothesis"] in AMBIGUOUS_OWNER_TARGETS:
            owner_ambiguity_total += 1

        if entry["drop_reason"] is not None:
            dropped_total += 1
            if entry["nearest_wrong_target"] is not None:
                misroute_target_counts[entry["nearest_wrong_target"]] += 1
        if entry["merged_into"] is not None or entry["supersedes"]:
            superseded_total += 1

        for axis in entry["axis_pressure"]:
            axis_pressure_counts[axis] += 1
        for stage in TIME_TO_STAGE_KEYS:
            duration = stage_duration_days(entry, stage)
            if duration is not None:
                time_to_stage_values[stage].append(duration)

    return {
        "schema_version": "aoa_stats_candidate_lineage_summary_v1",
        "generated_from": source,
        "stage_counts": stage_counts,
        "owner_target_counts": dict(sorted(owner_target_counts.items())),
        "owner_shape_counts": dict(sorted(owner_shape_counts.items())),
        "status_posture_counts": dict(sorted(status_posture_counts.items())),
        "time_to_stage_median_days": {
            stage: median_days(values) for stage, values in time_to_stage_values.items()
        },
        "misroute_counts": {
            "total": sum(misroute_target_counts.values()),
            "by_target": dict(sorted(misroute_target_counts.items())),
            "owner_ambiguity_total": owner_ambiguity_total,
        },
        "supersession_counts": {
            "superseded_total": superseded_total,
            "dropped_total": dropped_total,
        },
        "axis_pressure_counts": dict(sorted(axis_pressure_counts.items())),
    }


def normalize_owner_landing_bundle(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    candidate_ref = payload.get("candidate_ref")
    owner_repo = payload.get("owner_repo")
    owner_shape = payload.get("owner_shape")
    status_posture = payload.get("status_posture")
    reviewed_at = payload.get("reviewed_at")
    evidence_refs = normalize_string_list(payload.get("evidence_refs"))
    if not (
        is_nonempty_string(candidate_ref)
        and is_nonempty_string(owner_repo)
        and is_nonempty_string(owner_shape)
        and is_nonempty_string(status_posture)
        and parse_iso_datetime(reviewed_at) is not None
        and evidence_refs
    ):
        return None
    return {
        "candidate_ref": candidate_ref,
        "cluster_ref": (
            payload.get("cluster_ref")
            if is_nonempty_string(payload.get("cluster_ref"))
            else None
        ),
        "owner_repo": owner_repo,
        "owner_shape": owner_shape,
        "nearest_wrong_target": (
            payload.get("nearest_wrong_target")
            if is_nonempty_string(payload.get("nearest_wrong_target"))
            else None
        ),
        "status_posture": status_posture,
        "reviewed_at": reviewed_at,
        "evidence_refs": evidence_refs,
        "status_note": (
            payload.get("status_note")
            if is_nonempty_string(payload.get("status_note"))
            else None
        ),
        "supersedes": normalize_string_list(payload.get("supersedes")),
        "superseded_by": (
            payload.get("superseded_by")
            if is_nonempty_string(payload.get("superseded_by"))
            else None
        ),
        "merged_into": (
            payload.get("merged_into")
            if is_nonempty_string(payload.get("merged_into"))
            else None
        ),
        "drop_reason": (
            payload.get("drop_reason")
            if is_nonempty_string(payload.get("drop_reason"))
            else None
        ),
        "drop_stage": (
            payload.get("drop_stage")
            if is_nonempty_string(payload.get("drop_stage"))
            else None
        ),
        "drop_evidence_refs": normalize_string_list(payload.get("drop_evidence_refs")),
    }


def collect_owner_landing_bundles(
    receipts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged_by_candidate: dict[str, dict[str, Any]] = {}
    earliest_reviewed_by_candidate: dict[str, str] = {}
    latest_reviewed_by_candidate: dict[str, datetime] = {}
    for receipt in receipts:
        if receipt["event_kind"] != "reviewed_owner_landing_receipt":
            continue
        normalized = normalize_owner_landing_bundle(receipt.get("payload"))
        if normalized is None:
            continue
        candidate_ref = normalized["candidate_ref"]
        previous = merged_by_candidate.get(candidate_ref)
        current_reviewed_at = parse_iso_datetime_or_min(normalized["reviewed_at"])
        if previous is None:
            merged_by_candidate[candidate_ref] = normalized
            earliest_reviewed_by_candidate[candidate_ref] = normalized["reviewed_at"]
            latest_reviewed_by_candidate[candidate_ref] = current_reviewed_at
            continue

        earliest_reviewed_at = earliest_reviewed_by_candidate[candidate_ref]
        if current_reviewed_at < parse_iso_datetime_or_min(earliest_reviewed_at):
            earliest_reviewed_at = normalized["reviewed_at"]
            earliest_reviewed_by_candidate[candidate_ref] = earliest_reviewed_at

        if current_reviewed_at >= latest_reviewed_by_candidate[candidate_ref]:
            merged = dict(normalized)
            merged["reviewed_at"] = earliest_reviewed_at
            merged_by_candidate[candidate_ref] = merged
            latest_reviewed_by_candidate[candidate_ref] = current_reviewed_at
        else:
            previous["reviewed_at"] = earliest_reviewed_at
    return sorted(
        merged_by_candidate.values(),
        key=lambda item: (
            parse_iso_datetime_or_min(item["reviewed_at"]),
            item["candidate_ref"],
        ),
    )


def normalize_seed_owner_landing_trace(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    candidate_ref = payload.get("candidate_ref")
    seed_ref = payload.get("seed_ref")
    owner_repo = payload.get("owner_repo")
    owner_shape = payload.get("owner_shape")
    outcome = payload.get("outcome")
    observed_at = payload.get("observed_at")
    evidence_refs = normalize_string_list(payload.get("evidence_refs"))
    if not (
        is_nonempty_string(candidate_ref)
        and is_nonempty_string(seed_ref)
        and is_nonempty_string(owner_repo)
        and is_nonempty_string(owner_shape)
        and is_nonempty_string(outcome)
        and parse_iso_datetime(observed_at) is not None
        and evidence_refs
    ):
        return None
    return {
        "candidate_ref": candidate_ref,
        "cluster_ref": (
            payload.get("cluster_ref")
            if is_nonempty_string(payload.get("cluster_ref"))
            else None
        ),
        "seed_ref": seed_ref,
        "owner_repo": owner_repo,
        "owner_shape": owner_shape,
        "outcome": outcome,
        "owner_status_ref": (
            payload.get("owner_status_ref")
            if is_nonempty_string(payload.get("owner_status_ref"))
            else None
        ),
        "object_ref": (
            payload.get("object_ref")
            if is_nonempty_string(payload.get("object_ref"))
            else None
        ),
        "merged_into": (
            payload.get("merged_into")
            if is_nonempty_string(payload.get("merged_into"))
            else None
        ),
        "superseded_by": (
            payload.get("superseded_by")
            if is_nonempty_string(payload.get("superseded_by"))
            else None
        ),
        "drop_reason": (
            payload.get("drop_reason")
            if is_nonempty_string(payload.get("drop_reason"))
            else None
        ),
        "observed_at": observed_at,
        "evidence_refs": evidence_refs,
    }


def collect_seed_owner_landing_traces(
    receipts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    latest_by_candidate: dict[str, dict[str, Any]] = {}
    for receipt in receipts:
        if receipt["event_kind"] != "seed_owner_landing_trace_receipt":
            continue
        normalized = normalize_seed_owner_landing_trace(receipt.get("payload"))
        if normalized is None:
            continue
        candidate_ref = normalized["candidate_ref"]
        previous = latest_by_candidate.get(candidate_ref)
        if previous is None or parse_iso_datetime_or_min(
            normalized["observed_at"]
        ) >= parse_iso_datetime_or_min(previous["observed_at"]):
            latest_by_candidate[candidate_ref] = normalized
    return sorted(
        latest_by_candidate.values(),
        key=lambda item: (
            parse_iso_datetime_or_min(item["observed_at"]),
            item["candidate_ref"],
        ),
    )


def empty_owner_landing_time_to_outcome() -> dict[str, float | None]:
    return {outcome: None for outcome in OWNER_LANDING_OUTCOMES}


def build_owner_landing_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    bundle_states = collect_owner_landing_bundles(receipts)
    trace_states = collect_seed_owner_landing_traces(receipts)
    states: dict[str, dict[str, Any]] = {}

    for bundle in bundle_states:
        state = states.setdefault(
            bundle["candidate_ref"],
            {
                "owner_repo": None,
                "owner_shape": None,
                "status_posture": None,
                "first_reviewed_at": None,
                "landing_outcome": None,
                "landing_observed_at": None,
            },
        )
        state["owner_repo"] = bundle["owner_repo"]
        state["owner_shape"] = bundle["owner_shape"]
        state["status_posture"] = bundle["status_posture"]
        first_reviewed_at = state["first_reviewed_at"]
        if first_reviewed_at is None or parse_iso_datetime_or_min(
            bundle["reviewed_at"]
        ) < parse_iso_datetime_or_min(first_reviewed_at):
            state["first_reviewed_at"] = bundle["reviewed_at"]

    for trace in trace_states:
        state = states.setdefault(
            trace["candidate_ref"],
            {
                "owner_repo": None,
                "owner_shape": None,
                "status_posture": None,
                "first_reviewed_at": None,
                "landing_outcome": None,
                "landing_observed_at": None,
            },
        )
        state["owner_repo"] = trace["owner_repo"]
        state["owner_shape"] = trace["owner_shape"]
        state["landing_outcome"] = trace["outcome"]
        state["landing_observed_at"] = trace["observed_at"]

    owner_repo_counts: Counter[str] = Counter()
    owner_shape_counts: Counter[str] = Counter()
    status_posture_counts: Counter[str] = Counter()
    landing_outcome_counts: Counter[str] = Counter()
    time_to_outcome_values: dict[str, list[float]] = {
        outcome: [] for outcome in OWNER_LANDING_OUTCOMES
    }

    for state in states.values():
        owner_repo = state["owner_repo"]
        owner_shape = state["owner_shape"]
        status_posture = state["status_posture"]
        landing_outcome = state["landing_outcome"]
        if is_nonempty_string(owner_repo):
            owner_repo_counts[owner_repo] += 1
        if is_nonempty_string(owner_shape):
            owner_shape_counts[owner_shape] += 1
        if is_nonempty_string(status_posture):
            status_posture_counts[status_posture] += 1
        if is_nonempty_string(landing_outcome):
            landing_outcome_counts[landing_outcome] += 1
            duration = duration_days_between(
                state["first_reviewed_at"], state["landing_observed_at"]
            )
            if duration is not None and landing_outcome in time_to_outcome_values:
                time_to_outcome_values[landing_outcome].append(duration)

    return {
        "schema_version": "aoa_stats_owner_landing_summary_v1",
        "generated_from": source,
        "owner_repo_counts": dict(sorted(owner_repo_counts.items())),
        "owner_shape_counts": dict(sorted(owner_shape_counts.items())),
        "status_posture_counts": dict(sorted(status_posture_counts.items())),
        "landing_outcome_counts": dict(sorted(landing_outcome_counts.items())),
        "time_to_outcome_median_days": {
            outcome: median_days(values)
            for outcome, values in time_to_outcome_values.items()
        },
    }


def collect_turnover_records(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for entry in collect_candidate_lineage_entries(receipts):
        records.append(
            {
                "candidate_ref": entry["candidate_ref"],
                "owner_repo": entry["owner_hypothesis"],
                "owner_shape": entry["owner_shape"],
                "status_posture": entry["status_posture"],
                "drop_reason": entry["drop_reason"],
                "merged_into": entry["merged_into"],
                "superseded_by": None,
                "supersedes": entry["supersedes"],
                "outcome": None,
                "timestamp": entry["stages"].get("superseded_or_dropped")
                or entry["stages"].get("harvested")
                or entry["receipt_observed_at"],
            }
        )
    for bundle in collect_owner_landing_bundles(receipts):
        records.append(
            {
                "candidate_ref": bundle["candidate_ref"],
                "owner_repo": bundle["owner_repo"],
                "owner_shape": bundle["owner_shape"],
                "status_posture": bundle["status_posture"],
                "drop_reason": bundle["drop_reason"],
                "merged_into": bundle["merged_into"],
                "superseded_by": bundle["superseded_by"],
                "supersedes": bundle["supersedes"],
                "outcome": None,
                "timestamp": bundle["reviewed_at"],
            }
        )
    for trace in collect_seed_owner_landing_traces(receipts):
        records.append(
            {
                "candidate_ref": trace["candidate_ref"],
                "owner_repo": trace["owner_repo"],
                "owner_shape": trace["owner_shape"],
                "status_posture": None,
                "drop_reason": trace["drop_reason"],
                "merged_into": trace["merged_into"],
                "superseded_by": trace["superseded_by"],
                "supersedes": [],
                "outcome": trace["outcome"],
                "timestamp": trace["observed_at"],
            }
        )
    return sorted(
        records,
        key=lambda item: (
            parse_iso_datetime_or_min(item["timestamp"]),
            item["candidate_ref"],
        ),
    )


def build_supersession_drop_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    states: dict[str, dict[str, Any]] = {}
    for record in collect_turnover_records(receipts):
        state = states.setdefault(
            record["candidate_ref"],
            {
                "owner_repo": None,
                "owner_shape": None,
                "status_posture": None,
                "drop_reason": None,
                "merged_into": None,
                "superseded_by": None,
                "supersedes": set(),
                "reanchor_after_drop": False,
            },
        )
        state["owner_repo"] = record["owner_repo"]
        state["owner_shape"] = record["owner_shape"]
        if is_nonempty_string(record["status_posture"]):
            state["status_posture"] = record["status_posture"]
        if is_nonempty_string(record["drop_reason"]):
            state["drop_reason"] = record["drop_reason"]
        if is_nonempty_string(record["merged_into"]):
            state["merged_into"] = record["merged_into"]
        if is_nonempty_string(record["superseded_by"]):
            state["superseded_by"] = record["superseded_by"]
        state["supersedes"].update(record["supersedes"])
        if is_nonempty_string(record["drop_reason"]) and (
            record["status_posture"] == "reanchor" or record["outcome"] == "reanchored"
        ):
            state["reanchor_after_drop"] = True

    drop_reason_counts: Counter[str] = Counter()
    owner_repo_counts: Counter[str] = Counter()
    merge_owner_repo_counts: Counter[str] = Counter()
    reanchor_after_drop_counts: Counter[str] = Counter()
    superseded_total = 0
    replacing_total = 0
    dropped_total = 0
    merge_total = 0

    for state in states.values():
        has_turnover = bool(
            state["drop_reason"]
            or state["merged_into"]
            or state["superseded_by"]
            or state["supersedes"]
            or state["reanchor_after_drop"]
        )
        if not has_turnover:
            continue
        owner_repo = state["owner_repo"]
        if is_nonempty_string(owner_repo):
            owner_repo_counts[owner_repo] += 1
        if is_nonempty_string(state["drop_reason"]):
            drop_reason_counts[state["drop_reason"]] += 1
            dropped_total += 1
        if is_nonempty_string(state["superseded_by"]):
            superseded_total += 1
        if state["supersedes"]:
            replacing_total += 1
        if is_nonempty_string(state["merged_into"]):
            merge_total += 1
            if is_nonempty_string(owner_repo):
                merge_owner_repo_counts[owner_repo] += 1
        if state["reanchor_after_drop"] and is_nonempty_string(owner_repo):
            reanchor_after_drop_counts[owner_repo] += 1

    return {
        "schema_version": "aoa_stats_supersession_drop_summary_v1",
        "generated_from": source,
        "drop_reason_counts": dict(sorted(drop_reason_counts.items())),
        "supersession_counts": {
            "superseded_total": superseded_total,
            "replacing_total": replacing_total,
            "dropped_total": dropped_total,
        },
        "merge_counts": {
            "total": merge_total,
            "by_owner_repo": dict(sorted(merge_owner_repo_counts.items())),
        },
        "owner_repo_counts": dict(sorted(owner_repo_counts.items())),
        "reanchor_after_drop_counts": dict(sorted(reanchor_after_drop_counts.items())),
    }
