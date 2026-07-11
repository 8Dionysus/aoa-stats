from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


CORE_SKILL_APPLICATION_EVENT_KIND = "core_skill_application_receipt"
FINISH_APPLICATION_STAGE = "finish"


def core_skill_identity(receipt: dict[str, Any]) -> tuple[str, str]:
    payload = receipt["payload"]
    kernel_id = payload.get("kernel_id")
    skill_name = payload.get("skill_name")
    if (
        isinstance(kernel_id, str)
        and kernel_id
        and isinstance(skill_name, str)
        and skill_name
    ):
        return kernel_id, skill_name
    object_id = receipt["object_ref"].get("id")
    if isinstance(object_id, str) and object_id:
        return "unknown-kernel", object_id
    return "unknown-kernel", "unknown-skill"


def surface_detection_context(receipt: dict[str, Any]) -> dict[str, Any]:
    payload = receipt["payload"]
    context = payload.get("surface_detection_context")
    if not isinstance(context, dict):
        return {}
    return context


def finished_core_skill_application_receipts(
    receipts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for receipt in receipts:
        if receipt["event_kind"] != CORE_SKILL_APPLICATION_EVENT_KIND:
            continue
        payload = receipt.get("payload")
        if (
            not isinstance(payload, dict)
            or payload.get("application_stage") != FINISH_APPLICATION_STAGE
        ):
            continue
        selected.append(receipt)
    return selected


def build_core_skill_application_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for receipt in finished_core_skill_application_receipts(receipts):
        grouped[core_skill_identity(receipt)].append(receipt)

    skills: list[dict[str, Any]] = []
    for key in sorted(grouped):
        kernel_id, skill_name = key
        group = grouped[key]
        latest = max(
            group,
            key=lambda receipt: (receipt["observed_at"], receipt["event_id"]),
        )
        detail_counts: Counter[str] = Counter()
        for receipt in group:
            detail_event_kind = receipt["payload"].get("detail_event_kind")
            if isinstance(detail_event_kind, str) and detail_event_kind:
                detail_counts[detail_event_kind] += 1
        skills.append(
            {
                "kernel_id": kernel_id,
                "skill_name": skill_name,
                "application_count": len(group),
                "latest_observed_at": latest["observed_at"],
                "latest_session_ref": latest["session_ref"],
                "latest_run_ref": latest["run_ref"],
                "detail_event_kind_counts": dict(sorted(detail_counts.items())),
            }
        )

    return {
        "schema_version": "aoa_stats_core_skill_application_summary_v1",
        "generated_from": source,
        "skills": skills,
    }


def build_surface_detection_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in finished_core_skill_application_receipts(receipts):
        grouped[receipt["observed_at"][:10]].append(receipt)

    windows: list[dict[str, Any]] = []
    for window_date in sorted(grouped):
        group = grouped[window_date]
        activation_counts: Counter[str] = Counter()
        adjacent_owner_repo_counts: Counter[str] = Counter()
        handoff_target_counts: Counter[str] = Counter()
        candidate_now_count = 0
        candidate_later_count = 0
        owner_layer_ambiguity_count = 0
        repeated_pattern_signal_count = 0
        promotion_discussion_count = 0
        family_entry_ref_count = 0

        for receipt in group:
            context = surface_detection_context(receipt)
            activation_truth = context.get("activation_truth")
            if (
                isinstance(activation_truth, str)
                and activation_truth == "manual-equivalent-adjacent"
            ):
                activation_counts["manual-equivalent-adjacent"] += 1
            else:
                activation_counts["activated"] += 1

            candidate_counts = context.get("candidate_counts")
            if isinstance(candidate_counts, dict):
                candidate_now_count += int(
                    candidate_counts.get("candidate_now") or 0
                )
                candidate_later_count += int(
                    candidate_counts.get("candidate_later") or 0
                )

            if bool(context.get("owner_layer_ambiguity")):
                owner_layer_ambiguity_count += 1

            adjacent_owner_repos = context.get("adjacent_owner_repos")
            if isinstance(adjacent_owner_repos, list):
                for repo in adjacent_owner_repos:
                    if isinstance(repo, str) and repo:
                        adjacent_owner_repo_counts[repo] += 1

            handoff_targets = context.get("suggested_handoff_targets")
            if isinstance(handoff_targets, list):
                for target in handoff_targets:
                    if isinstance(target, str) and target:
                        handoff_target_counts[target] += 1

            if bool(context.get("repeated_pattern_signal")):
                repeated_pattern_signal_count += 1
            if bool(context.get("promotion_discussion_required")):
                promotion_discussion_count += 1

            family_entry_refs = context.get("family_entry_refs")
            if isinstance(family_entry_refs, list):
                family_entry_ref_count += len(
                    [
                        ref
                        for ref in family_entry_refs
                        if isinstance(ref, str) and ref
                    ]
                )

        windows.append(
            {
                "window_id": f"window:{window_date}",
                "window_date": window_date,
                "core_skill_receipt_count": len(group),
                "activated_count": activation_counts["activated"],
                "manual_equivalent_adjacent_count": activation_counts[
                    "manual-equivalent-adjacent"
                ],
                "candidate_now_count": candidate_now_count,
                "candidate_later_count": candidate_later_count,
                "owner_layer_ambiguity_count": owner_layer_ambiguity_count,
                "adjacent_owner_repo_counts": dict(
                    sorted(adjacent_owner_repo_counts.items())
                ),
                "handoff_target_counts": dict(sorted(handoff_target_counts.items())),
                "repeated_pattern_signal_count": repeated_pattern_signal_count,
                "promotion_discussion_count": promotion_discussion_count,
                "family_entry_ref_count": family_entry_ref_count,
                "evidence_ref_count": sum(
                    len(receipt["evidence_refs"]) for receipt in group
                ),
                "first_observed_at": group[0]["observed_at"],
                "last_observed_at": group[-1]["observed_at"],
            }
        )

    return {
        "schema_version": "aoa_stats_surface_detection_summary_v1",
        "generated_from": source,
        "windows": windows,
    }
