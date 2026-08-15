from __future__ import annotations

from collections import Counter, defaultdict
import math
import re
from typing import Any


ACTOR_RESPONSIBILITY_EVENT_KIND = "actor_responsibility_execution_receipt"
REF_FIELDS = ("object_id", "owner_repo", "schema_version", "digest")
ACTOR_USAGE_UNKNOWN_FIELDS = [
    "model_slug",
    "reasoning_effort",
    "tokens.input",
    "tokens.cached_input",
    "tokens.output",
    "timing.active_wall_seconds",
    "timing.duration_seconds",
    "activity.turns",
    "activity.commands",
    "activity.attempts",
    "activity.start_invocations",
    "activity.resume_invocations",
    "runtime_outcome.status",
    "runtime_outcome.exit_code",
    "cost.metering_mode",
    "cost.active_cost_regime",
    "cost.usd",
]
ACTOR_USAGE_PROJECTION_SCHEMA = "aoa_actor_usage_observation_projection_v1"
ACTOR_USAGE_REASONING_EFFORTS = {"low", "medium", "high", "xhigh", "max"}
ACTOR_USAGE_COST_STATUSES = {"reported", "not_reported", "unknown"}
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def object_key(object_ref: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        object_ref["repo"],
        object_ref["kind"],
        object_ref["id"],
        object_ref.get("version", ""),
    )


def _valid_ref(value: Any) -> dict[str, str] | None:
    if not isinstance(value, dict):
        return None
    required = set(REF_FIELDS)
    if not required <= set(value):
        return None
    if not all(isinstance(value[field], str) and value[field] for field in required):
        return None
    if DIGEST_RE.fullmatch(value["digest"]) is None:
        return None
    return {field: value[field] for field in REF_FIELDS}


def _valid_optional_string(value: Any) -> bool:
    return value is None or (isinstance(value, str) and bool(value))


def _valid_optional_number(value: Any, *, integer: bool = False) -> bool:
    if value is None:
        return True
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    if not math.isfinite(value) or value < 0:
        return False
    return not integer or isinstance(value, int)


def _valid_actor_usage_projection(payload: dict[str, Any], projection: dict[str, Any]) -> bool:
    required = {
        "schema_version",
        "source_ref",
        "runtime_result_ref",
        "observation_status",
        "gap_reasons",
        "model_slug",
        "reasoning_effort",
        "input_tokens",
        "cached_input_tokens",
        "output_tokens",
        "active_wall_seconds",
        "duration_seconds",
        "turn_count",
        "executed_command_count",
        "attempt_count",
        "start_invocation_count",
        "resume_invocation_count",
        "runtime_status",
        "exit_code",
        "metering_mode",
        "active_cost_regime",
        "cost_usd",
        "cost_status",
        "unknown_fields",
    }
    if set(projection) != required:
        return False
    if projection["schema_version"] != ACTOR_USAGE_PROJECTION_SCHEMA:
        return False
    source_ref = _valid_ref(projection["source_ref"])
    runtime_result_ref = _valid_ref(projection["runtime_result_ref"])
    owner_evidence = payload.get("owner_evidence")
    owner_evidence = owner_evidence if isinstance(owner_evidence, dict) else {}
    runtime_state = owner_evidence.get("runtime_state")
    runtime_state = runtime_state if isinstance(runtime_state, dict) else {}
    owner_source_ref = _valid_ref(runtime_state.get("usage_observation_ref"))
    owner_runtime_result_ref = _valid_ref(runtime_state.get("runtime_result_ref"))
    if source_ref is None or runtime_result_ref is None:
        return False
    if source_ref != owner_source_ref or runtime_result_ref != owner_runtime_result_ref:
        return False
    if source_ref["owner_repo"] != "abyss-stack" or source_ref["schema_version"] != "abyss_stack_external_codex_usage_observation_v1":
        return False
    if runtime_result_ref["owner_repo"] != "abyss-stack" or runtime_result_ref["schema_version"] != "abyss_stack_external_codex_result_v2":
        return False
    if source_ref["object_id"] != f"{runtime_result_ref['object_id']}#/usage_observation":
        return False
    status = projection["observation_status"]
    if status not in {"complete", "partial"}:
        return False
    gaps = projection["gap_reasons"]
    if not isinstance(gaps, list):
        return False
    for gap in gaps:
        if not isinstance(gap, dict) or set(gap) != {"attempt_id", "reason", "event_sequence"}:
            return False
        if not isinstance(gap["attempt_id"], str) or not gap["attempt_id"]:
            return False
        if gap["reason"] != "controlled_interruption_before_turn_usage":
            return False
        if gap["event_sequence"] is None or not _valid_optional_number(
            gap["event_sequence"], integer=True
        ):
            return False
    if (status == "complete" and gaps) or (status == "partial" and not gaps):
        return False
    if not _valid_optional_string(projection["model_slug"]):
        return False
    if projection["reasoning_effort"] not in ACTOR_USAGE_REASONING_EFFORTS | {None}:
        return False
    for field in (
        "input_tokens",
        "cached_input_tokens",
        "output_tokens",
        "turn_count",
        "executed_command_count",
        "attempt_count",
        "start_invocation_count",
        "resume_invocation_count",
    ):
        if not _valid_optional_number(projection[field], integer=True):
            return False
    for field in ("active_wall_seconds", "duration_seconds", "cost_usd"):
        if not _valid_optional_number(projection[field]):
            return False
    if not _valid_optional_string(projection["runtime_status"]):
        return False
    if projection["exit_code"] is not None and (
        isinstance(projection["exit_code"], bool)
        or not isinstance(projection["exit_code"], int)
    ):
        return False
    if projection["metering_mode"] not in {"observe_only", None}:
        return False
    if not _valid_optional_string(projection["active_cost_regime"]):
        return False
    if projection["cost_status"] not in ACTOR_USAGE_COST_STATUSES:
        return False
    unknown_fields = projection["unknown_fields"]
    return (
        isinstance(unknown_fields, list)
        and len(unknown_fields) == len(set(unknown_fields))
        and all(isinstance(field, str) and bool(field) for field in unknown_fields)
    )


def _posture_and_remainder(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    authority = payload.get("authority_posture")
    authority = authority if isinstance(authority, dict) else {}
    execution = payload.get("execution")
    execution = execution if isinstance(execution, dict) else {}
    owner_evidence = payload.get("owner_evidence")
    owner_evidence = owner_evidence if isinstance(owner_evidence, dict) else {}
    return_validation = owner_evidence.get("return_validation")
    return_validation = return_validation if isinstance(return_validation, dict) else {}
    closeout = owner_evidence.get("closeout_handoff")
    closeout = closeout if isinstance(closeout, dict) else {}
    posture = {
        field: authority.get(field)
        if isinstance(authority.get(field), str)
        else None
        for field in (
            "benefit",
            "model_fit",
            "task_success",
            "proof",
            "review_approval",
            "owner_acceptance",
            "publication",
        )
    }
    posture["receipt_runtime_state"] = (
        execution.get("runtime_state")
        if isinstance(execution.get("runtime_state"), str)
        else None
    )
    posture["return_validation_accepted"] = (
        return_validation.get("accepted")
        if isinstance(return_validation.get("accepted"), bool)
        else None
    )
    remainder = {
        "residual_risk": (
            closeout.get("residual_risk")
            if isinstance(closeout.get("residual_risk"), str)
            else None
        ),
        "next_route": (
            closeout.get("next_route")
            if isinstance(closeout.get("next_route"), str)
            else None
        ),
    }
    return posture, remainder


def _unknown_actor_usage(payload: dict[str, Any]) -> dict[str, Any]:
    owner_evidence = payload.get("owner_evidence")
    owner_evidence = owner_evidence if isinstance(owner_evidence, dict) else {}
    runtime_state = owner_evidence.get("runtime_state")
    runtime_state = runtime_state if isinstance(runtime_state, dict) else {}
    posture, remainder = _posture_and_remainder(payload)
    return {
        "status": "unknown",
        "source_ref": _valid_ref(runtime_state.get("usage_observation_ref")),
        "runtime_result_ref": _valid_ref(runtime_state.get("runtime_result_ref")),
        "model": {"slug": None, "reasoning_effort": None},
        "tokens": {"input": None, "cached_input": None, "output": None},
        "timing": {"active_wall_seconds": None, "duration_seconds": None},
        "activity": {
            "turns": None,
            "commands": None,
            "attempts": None,
            "start_invocations": None,
            "resume_invocations": None,
        },
        "runtime_outcome": {"status": None, "exit_code": None},
        "cost": {
            "metering_mode": None,
            "active_cost_regime": None,
            "usd": None,
            "status": "unknown",
        },
        "review_acceptance_posture": posture,
        "open_remainder": remainder,
        "gap_reasons": [],
        "unknown_fields": list(ACTOR_USAGE_UNKNOWN_FIELDS),
    }


def _actor_usage_observation(payload: dict[str, Any]) -> dict[str, Any]:
    projection = payload.get("usage_observation")
    if not isinstance(projection, dict):
        return _unknown_actor_usage(payload)
    required = {
        "schema_version",
        "source_ref",
        "runtime_result_ref",
        "observation_status",
        "gap_reasons",
        "model_slug",
        "reasoning_effort",
        "input_tokens",
        "cached_input_tokens",
        "output_tokens",
        "active_wall_seconds",
        "duration_seconds",
        "turn_count",
        "executed_command_count",
        "attempt_count",
        "start_invocation_count",
        "resume_invocation_count",
        "runtime_status",
        "exit_code",
        "metering_mode",
        "active_cost_regime",
        "cost_usd",
        "cost_status",
        "unknown_fields",
    }
    if not required <= set(projection) or not _valid_actor_usage_projection(payload, projection):
        unknown = _unknown_actor_usage(payload)
        unknown["unknown_fields"] = sorted(
            set(unknown["unknown_fields"]) | {"usage_observation"}
        )
        return unknown
    posture, remainder = _posture_and_remainder(payload)
    return {
        "status": projection["observation_status"],
        "source_ref": _valid_ref(projection.get("source_ref")),
        "runtime_result_ref": _valid_ref(projection.get("runtime_result_ref")),
        "model": {
            "slug": projection["model_slug"],
            "reasoning_effort": projection["reasoning_effort"],
        },
        "tokens": {
            "input": projection["input_tokens"],
            "cached_input": projection["cached_input_tokens"],
            "output": projection["output_tokens"],
        },
        "timing": {
            "active_wall_seconds": projection["active_wall_seconds"],
            "duration_seconds": projection["duration_seconds"],
        },
        "activity": {
            "turns": projection["turn_count"],
            "commands": projection["executed_command_count"],
            "attempts": projection["attempt_count"],
            "start_invocations": projection["start_invocation_count"],
            "resume_invocations": projection["resume_invocation_count"],
        },
        "runtime_outcome": {
            "status": projection["runtime_status"],
            "exit_code": projection["exit_code"],
        },
        "cost": {
            "metering_mode": projection["metering_mode"],
            "active_cost_regime": projection["active_cost_regime"],
            "usd": projection["cost_usd"],
            "status": projection["cost_status"],
        },
        "review_acceptance_posture": posture,
        "open_remainder": remainder,
        "gap_reasons": projection["gap_reasons"],
        "unknown_fields": list(projection["unknown_fields"]),
    }


def build_object_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        grouped[object_key(receipt["object_ref"])].append(receipt)

    objects: list[dict[str, Any]] = []
    for key in sorted(grouped):
        group = grouped[key]
        by_kind = Counter(receipt["event_kind"] for receipt in group)
        latest = max(
            group,
            key=lambda receipt: (receipt["observed_at"], receipt["event_id"]),
        )
        latest_eval = None
        latest_progression = None
        automation_total = 0
        automation_seed_ready = 0
        automation_checkpoint_required = 0
        for receipt in group:
            payload = receipt["payload"]
            if receipt["event_kind"] == "eval_result_receipt":
                latest_eval = payload.get("verdict")
            if receipt["event_kind"] == "progression_delta_receipt":
                latest_progression = payload.get("verdict")
            if receipt["event_kind"] == "automation_candidate_receipt":
                automation_total += 1
                if payload.get("seed_ready") is True:
                    automation_seed_ready += 1
                if payload.get("checkpoint_required") is True:
                    automation_checkpoint_required += 1

        actor_receipts = [
            receipt
            for receipt in group
            if receipt["event_kind"] == ACTOR_RESPONSIBILITY_EVENT_KIND
        ]

        object_ref = dict(latest["object_ref"])
        object_summary = {
            "object_ref": object_ref,
            "receipt_count_total": len(group),
            "receipt_counts_by_event_kind": dict(sorted(by_kind.items())),
            "first_observed_at": group[0]["observed_at"],
            "last_observed_at": latest["observed_at"],
            "latest_session_ref": latest["session_ref"],
            "latest_run_ref": latest["run_ref"],
            "evidence_ref_count": sum(
                len(receipt["evidence_refs"]) for receipt in group
            ),
            "latest_eval_verdict": latest_eval,
            "latest_progression_verdict": latest_progression,
            "automation_candidate_counts": {
                "total": automation_total,
                "seed_ready": automation_seed_ready,
                "checkpoint_required": automation_checkpoint_required,
            },
        }
        if actor_receipts:
            latest_actor = max(
                actor_receipts,
                key=lambda receipt: (receipt["observed_at"], receipt["event_id"]),
            )
            object_summary["actor_usage_observation"] = _actor_usage_observation(
                latest_actor["payload"]
            )
        objects.append(object_summary)

    return {
        "schema_version": "aoa_stats_object_summary_v1",
        "generated_from": source,
        "objects": objects,
    }
