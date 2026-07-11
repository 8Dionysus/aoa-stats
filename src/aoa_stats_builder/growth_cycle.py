from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .read_model_values import (
    is_nonempty_string,
    normalize_string_list,
    string_count_map,
    summary_window_ref,
)

FOLLOWTHROUGH_SKILL_NAMES = frozenset(
    {
        "aoa-session-route-forks",
        "aoa-session-self-diagnose",
        "aoa-session-self-repair",
        "aoa-session-progression-lift",
        "aoa-automation-opportunity-scan",
        "aoa-quest-harvest",
    }
)


def automation_pipeline_ref(receipt: dict[str, Any]) -> str:
    payload = receipt["payload"]
    for key in ("pipeline_ref", "manual_route_ref"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return receipt["session_ref"]


def fork_option_count(payload: dict[str, Any]) -> int:
    option_count = payload.get("branch_options_count")
    if isinstance(option_count, int) and option_count > 0:
        return option_count
    branch_ids = payload.get("branch_ids")
    if isinstance(branch_ids, list):
        return len(
            [
                branch_id
                for branch_id in branch_ids
                if isinstance(branch_id, str) and branch_id
            ]
        )
    return 0


def normalized_code_list(value: Any) -> list[str]:
    return [
        item.strip()
        for item in normalize_string_list(value)
        if is_nonempty_string(item) and item.strip()
    ]


def followthrough_recommended_next_skill(payload: dict[str, Any]) -> str | None:
    recommended = payload.get("recommended_next_skill")
    if isinstance(recommended, str) and recommended in FOLLOWTHROUGH_SKILL_NAMES:
        return recommended
    chosen_branch = payload.get("chosen_branch")
    if isinstance(chosen_branch, str) and chosen_branch in FOLLOWTHROUGH_SKILL_NAMES:
        return chosen_branch
    return None


def automation_blocker_codes(payload: dict[str, Any]) -> list[str]:
    blocker_codes = normalized_code_list(payload.get("blocker_codes"))
    if blocker_codes:
        return blocker_codes
    return normalized_code_list(payload.get("blockers"))


def build_fork_calibration_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != "decision_fork_receipt":
            continue
        route_ref = receipt["payload"].get("route_ref") or receipt["session_ref"]
        grouped[route_ref].append(receipt)

    routes: list[dict[str, Any]] = []
    for route_ref in sorted(grouped):
        group = grouped[route_ref]
        latest = max(
            group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"])
        )
        branch_counts: Counter[str] = Counter()
        max_options = 0
        realized_outcome_link_count = 0
        for receipt in group:
            payload = receipt["payload"]
            branch = payload.get("chosen_branch") or "unrecorded"
            branch_counts[str(branch)] += 1
            option_count = fork_option_count(payload)
            if option_count > max_options:
                max_options = option_count
            realized_refs = payload.get("realized_outcome_refs", [])
            if isinstance(realized_refs, list):
                realized_outcome_link_count += len(realized_refs)
        routes.append(
            {
                "route_ref": route_ref,
                "decision_count": len(group),
                "chosen_branch_counts": dict(sorted(branch_counts.items())),
                "max_option_count": max_options,
                "realized_outcome_link_count": realized_outcome_link_count,
                "evidence_ref_count": sum(
                    len(receipt["evidence_refs"]) for receipt in group
                ),
                "latest_observed_at": latest["observed_at"],
            }
        )

    return {
        "schema_version": "aoa_stats_fork_calibration_summary_v1",
        "generated_from": source,
        "routes": routes,
    }


def build_session_growth_branch_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    recommended_next_skill_counts: Counter[str] = Counter()
    owner_target_counts: Counter[str] = Counter()
    status_posture_counts: Counter[str] = Counter()
    reason_code_aggregates: Counter[str] = Counter()
    defer_count = 0

    for receipt in receipts:
        if receipt["event_kind"] != "decision_fork_receipt":
            continue
        payload = receipt["payload"]
        recommended_next_skill = followthrough_recommended_next_skill(payload)
        if is_nonempty_string(recommended_next_skill):
            recommended_next_skill_counts[recommended_next_skill] += 1
        owner_target = payload.get("owner_hypothesis") or payload.get("owner_target")
        if is_nonempty_string(owner_target):
            owner_target_counts[str(owner_target)] += 1
        status_posture = payload.get("status_posture")
        if is_nonempty_string(status_posture):
            status_posture_counts[str(status_posture)] += 1
        for reason_code in normalized_code_list(payload.get("reason_codes")):
            reason_code_aggregates[reason_code] += 1
        if payload.get("defer_allowed") is True or payload.get("defer_recommended") is True:
            defer_count += 1

    return {
        "schema_version": "aoa_stats_session_growth_branch_summary_v1",
        "generated_from": source,
        "window_ref": summary_window_ref(receipts),
        "counts_by_recommended_next_skill": string_count_map(
            recommended_next_skill_counts
        ),
        "defer_count": defer_count,
        "counts_by_owner_target": string_count_map(owner_target_counts),
        "counts_by_status_posture": string_count_map(status_posture_counts),
        "reason_code_aggregates": string_count_map(reason_code_aggregates),
    }


def build_automation_pipeline_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != "automation_candidate_receipt":
            continue
        pipeline_ref = automation_pipeline_ref(receipt)
        grouped[pipeline_ref].append(receipt)

    pipelines: list[dict[str, Any]] = []
    for pipeline_ref in sorted(grouped):
        group = grouped[pipeline_ref]
        latest = max(
            group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"])
        )
        next_artifact_hints: set[str] = set()
        seed_ready_count = 0
        checkpoint_required_count = 0
        deterministic_ready_count = 0
        reversible_ready_count = 0
        for receipt in group:
            payload = receipt["payload"]
            if payload.get("seed_ready") is True:
                seed_ready_count += 1
            if payload.get("checkpoint_required") is True:
                checkpoint_required_count += 1
            if payload.get("deterministic_ready") is True:
                deterministic_ready_count += 1
            if payload.get("reversible_ready") is True:
                reversible_ready_count += 1
            next_hint = payload.get("next_artifact_hint")
            if isinstance(next_hint, str) and next_hint:
                next_artifact_hints.add(next_hint)
        pipelines.append(
            {
                "pipeline_ref": pipeline_ref,
                "candidate_count": len(group),
                "seed_ready_count": seed_ready_count,
                "checkpoint_required_count": checkpoint_required_count,
                "deterministic_ready_count": deterministic_ready_count,
                "reversible_ready_count": reversible_ready_count,
                "next_artifact_hints": sorted(next_artifact_hints),
                "evidence_ref_count": sum(
                    len(receipt["evidence_refs"]) for receipt in group
                ),
                "latest_observed_at": latest["observed_at"],
            }
        )

    return {
        "schema_version": "aoa_stats_automation_pipeline_summary_v1",
        "generated_from": source,
        "pipelines": pipelines,
    }


def build_automation_followthrough_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    automation_candidate_count = 0
    seed_ready_count = 0
    not_now_count = 0
    checkpoint_required_count = 0
    playbook_seed_candidate_count = 0
    real_run_reviewed_count = 0
    blocker_aggregates: Counter[str] = Counter()

    for receipt in receipts:
        if receipt["event_kind"] != "automation_candidate_receipt":
            continue
        payload = receipt["payload"]
        automation_candidate_count += 1
        if payload.get("seed_ready") is True:
            seed_ready_count += 1
        else:
            not_now_count += 1
        if payload.get("checkpoint_required") is True:
            checkpoint_required_count += 1
        if is_nonempty_string(payload.get("playbook_seed_candidate")):
            playbook_seed_candidate_count += 1
        if payload.get("real_run_reviewed") is True:
            real_run_reviewed_count += 1
        for blocker_code in automation_blocker_codes(payload):
            blocker_aggregates[blocker_code] += 1

    return {
        "schema_version": "aoa_stats_automation_followthrough_summary_v1",
        "generated_from": source,
        "window_ref": summary_window_ref(receipts),
        "automation_candidate_count": automation_candidate_count,
        "seed_ready_count": seed_ready_count,
        "not_now_count": not_now_count,
        "checkpoint_required_count": checkpoint_required_count,
        "playbook_seed_candidate_count": playbook_seed_candidate_count,
        "real_run_reviewed_count": real_run_reviewed_count,
        "defer_count": not_now_count,
        "blocker_aggregates": string_count_map(blocker_aggregates),
    }
