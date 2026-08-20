from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import hashlib
import json
from typing import Any

from aoa_stats_builder.outcome import validate_outcome_receipt_semantics


ZERO_DIGEST = "sha256:" + ("0" * 64)
OBSERVED_OUTCOME_STATES = frozenset(
    {"success", "failure", "partial", "no_effect", "harm"}
)


def canonical_digest(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def normalized_utility_aggregate_digest(aggregate: Mapping[str, Any]) -> str:
    normalized = dict(aggregate)
    normalized["content_digest"] = ZERO_DIGEST
    return canonical_digest(normalized)


def _action_changed(receipt: Mapping[str, Any]) -> bool:
    before = receipt.get("action_before_memory")
    after = receipt.get("action_after_memory")
    if not isinstance(before, Mapping) or not isinstance(after, Mapping):
        return False
    fields = (
        "decision_state",
        "operation_id",
        "parameters_digest",
        "snapshot_digest",
    )
    return any(before.get(field) != after.get(field) for field in fields)


def _state_value(state: object) -> float:
    return {
        "success": 1.0,
        "partial": 0.25,
        "no_effect": 0.0,
        "failure": -1.0,
        "harm": -1.0,
    }.get(state, 0.0)


def _harm_penalty(harm: object) -> float:
    if not isinstance(harm, Mapping) or harm.get("observed") is not True:
        return 0.0
    return {
        "low": 0.25,
        "medium": 0.5,
        "high": 1.0,
        "critical": 2.0,
    }.get(harm.get("severity"), 0.0)


def _receipt_ref(receipt: Mapping[str, Any]) -> dict[str, str]:
    return {
        "owner_repo": str(receipt["producer_owner"]),
        "artifact_ref": str(receipt["receipt_id"]),
        "artifact_version": str(receipt["receipt_version"]),
        "artifact_digest": str(receipt["content_digest"]),
    }


def _counter(values: Sequence[object]) -> dict[str, int]:
    counts = Counter(str(value) for value in values)
    return dict(sorted(counts.items()))


def aggregate_episodic_utility(
    *,
    aggregate_id: str,
    item_ref: Mapping[str, str],
    receipts: Sequence[Mapping[str, Any]],
    produced_at: str,
) -> dict[str, Any]:
    """Build a descriptive aggregate over valid C10 receipts.

    The result is measurement evidence only. It does not decide proof,
    ranking, policy, lifecycle, retention, or any semantic transition.
    """

    if not receipts:
        raise ValueError("episodic utility aggregation requires C10 receipts")

    issues: list[str] = []
    for index, receipt in enumerate(receipts):
        receipt_issues = validate_outcome_receipt_semantics(receipt)
        issues.extend(f"receipt[{index}]: {issue}" for issue in receipt_issues)
    if issues:
        raise ValueError("; ".join(issues))

    receipt_ids: set[str] = set()
    idempotency_keys: set[str] = set()
    for receipt in receipts:
        receipt_id = str(receipt["receipt_id"])
        idempotency_key = str(receipt["idempotency_key"])
        if receipt_id in receipt_ids:
            raise ValueError("utility aggregate cannot contain duplicate receipt_id")
        if idempotency_key in idempotency_keys:
            raise ValueError(
                "utility aggregate cannot contain duplicate idempotency_key"
            )
        receipt_ids.add(receipt_id)
        idempotency_keys.add(idempotency_key)

    tenants = {receipt.get("tenant_id") for receipt in receipts}
    consumers = {receipt.get("consumer_id") for receipt in receipts}
    policy_pins = {
        canonical_digest(receipt.get("policy_pin")) for receipt in receipts
    }
    if len(tenants) != 1:
        raise ValueError("utility aggregate cannot mix tenants")
    if len(consumers) != 1:
        raise ValueError("utility aggregate cannot mix consumers")
    if len(policy_pins) != 1:
        raise ValueError("utility aggregate cannot mix policy pins")

    action_change_flags = [_action_changed(receipt) for receipt in receipts]
    terminal_states = [
        receipt["terminal_outcome"]["state"] for receipt in receipts
    ]
    delayed_states = [
        item["state"]
        for receipt in receipts
        for item in receipt.get("delayed_outcomes", ())
        if isinstance(item, Mapping)
    ]
    attribution_states = [
        receipt["attribution"]["status"] for receipt in receipts
    ]

    qualified_flags: list[bool] = []
    signed_values: list[float] = []
    delayed_adjustments: list[float] = []
    for receipt, action_changed in zip(
        receipts,
        action_change_flags,
        strict=True,
    ):
        terminal = receipt["terminal_outcome"]
        attribution = receipt["attribution"]
        evaluation = receipt["evaluation_posture"]
        accidental = receipt["accidental_success"]["value"] is True
        counterfactual_present = (
            attribution.get("counterfactual_ref") is not None
            or receipt["experiment_assignment"].get(
                "always_shadow_counterfactual_ref"
            )
            is not None
        )
        qualified = (
            receipt["memory_used"] is True
            and action_changed
            and terminal["state"] in OBSERVED_OUTCOME_STATES
            and terminal.get("task_owner_acceptance") is True
            and attribution["status"] in {"possible", "supported"}
            and evaluation["eval_plane_status"] == "available"
            and counterfactual_present
            and receipt["accidental_success"]["value"] is False
        )
        qualified_flags.append(qualified)

        terminal_value = _state_value(terminal["state"])
        if accidental and terminal_value > 0:
            terminal_value = 0.0
        delayed_value = sum(
            _state_value(item.get("state"))
            for item in receipt.get("delayed_outcomes", ())
            if isinstance(item, Mapping)
            and item.get("task_owner_acceptance") is True
        )
        delayed_adjustments.append(delayed_value)
        signed_values.append(
            terminal_value + delayed_value - _harm_penalty(receipt["harm"])
            if qualified
            else 0.0
        )

    pending_delayed = sum(
        receipt["delayed_outcome_posture"] in {"pending", "overdue"}
        for receipt in receipts
    )
    accidental_success = sum(
        receipt["accidental_success"]["value"] is True for receipt in receipts
    )
    observed_harm = sum(
        receipt["harm"]["observed"] is True for receipt in receipts
    )
    critical_events = sum(
        receipt["harm"].get("severity") == "critical" for receipt in receipts
    )
    reward_hacking_evidence = sum(
        receipt["evaluation_posture"].get("reward_hacking_check_ref") is not None
        for receipt in receipts
    )
    counterfactual_evidence = sum(
        receipt["attribution"].get("counterfactual_ref") is not None
        or receipt["experiment_assignment"].get(
            "always_shadow_counterfactual_ref"
        )
        is not None
        for receipt in receipts
    )

    qualified_count = sum(qualified_flags)
    signed_sum = sum(signed_values)
    aggregate = {
        "schema_version": "aoa_stats_episodic_utility_aggregate_v0",
        "aggregate_id": aggregate_id,
        "aggregate_version": 1,
        "stats_owner": "aoa-stats",
        "item_ref": dict(item_ref),
        "tenant_id": next(iter(tenants)),
        "consumer_id": next(iter(consumers)),
        "policy_pin": dict(receipts[0]["policy_pin"]),
        "outcome_receipt_refs": [_receipt_ref(receipt) for receipt in receipts],
        "observation_count": len(receipts),
        "memory_used_count": sum(
            receipt["memory_used"] is True for receipt in receipts
        ),
        "action_change_count": sum(action_change_flags),
        "qualified_observation_count": qualified_count,
        "terminal_state_counts": _counter(terminal_states),
        "delayed_state_counts": _counter(delayed_states),
        "pending_or_overdue_delayed_count": pending_delayed,
        "accidental_success_count": accidental_success,
        "observed_harm_count": observed_harm,
        "critical_event_count": critical_events,
        "counterfactual_evidence_count": counterfactual_evidence,
        "reward_hacking_evidence_count": reward_hacking_evidence,
        "attribution_state_counts": _counter(attribution_states),
        "measurement": {
            "qualified_signed_outcome_sum": signed_sum,
            "qualified_signed_outcome_mean": (
                signed_sum / qualified_count if qualified_count else 0.0
            ),
            "action_change_rate": sum(action_change_flags) / len(receipts),
            "delayed_adjustment_sum": sum(delayed_adjustments),
        },
        "evidence_completeness": (
            "partial"
            if pending_delayed
            else "complete"
        ),
        "access_count_used_as_utility": False,
        "proof_verdict": "forbidden",
        "semantic_authority": "none",
        "effect_authority": "none",
        "produced_at": produced_at,
        "content_digest": ZERO_DIGEST,
    }
    aggregate["content_digest"] = normalized_utility_aggregate_digest(aggregate)
    return aggregate


def validate_episodic_utility_aggregate(
    aggregate: Mapping[str, Any],
) -> list[str]:
    issues: list[str] = []
    if aggregate.get("schema_version") != "aoa_stats_episodic_utility_aggregate_v0":
        issues.append("unknown utility aggregate schema version")
    if aggregate.get("stats_owner") != "aoa-stats":
        issues.append("utility aggregate stats owner must be aoa-stats")
    if aggregate.get("access_count_used_as_utility") is not False:
        issues.append("access count cannot be used as utility")
    if aggregate.get("proof_verdict") != "forbidden":
        issues.append("stats utility aggregate cannot carry a proof verdict")
    if aggregate.get("semantic_authority") != "none":
        issues.append("stats utility aggregate cannot carry semantic authority")
    if aggregate.get("effect_authority") != "none":
        issues.append("stats utility aggregate cannot carry effect authority")
    observation_count = aggregate.get("observation_count")
    refs = aggregate.get("outcome_receipt_refs")
    if (
        not isinstance(observation_count, int)
        or observation_count < 1
        or not isinstance(refs, list)
        or len(refs) != observation_count
    ):
        issues.append("utility aggregate observation count must match receipt refs")
    if aggregate.get("content_digest") != normalized_utility_aggregate_digest(
        aggregate
    ):
        issues.append("utility aggregate normalized digest mismatch")
    return issues


def validate_agent_local_federation_aggregate(
    aggregate: Mapping[str, Any],
) -> list[str]:
    """Validate cross-field facts for the agent-local aggregate.

    The schema owns shape and authority constants. This function only checks
    arithmetic and reconciliation; it does not judge promotion, isolation,
    portability, consumer-zero, or operator outcomes.
    """

    issues: list[str] = []
    if aggregate.get("schema_version") != (
        "active_organ_agent_local_federation_aggregate_v0"
    ):
        issues.append("unknown agent-local aggregate schema version")
    if aggregate.get("measurement_authority") != "aoa-stats":
        issues.append("agent-local aggregate measurement authority must be aoa-stats")
    if aggregate.get("promotion_authority") != "forbidden":
        issues.append("agent-local aggregate promotion authority must be forbidden")
    if aggregate.get("proof_authority") != "forbidden":
        issues.append("agent-local aggregate proof authority must be forbidden")

    promotion = aggregate.get("promotion")
    if isinstance(promotion, Mapping):
        nominated = promotion.get("nominated")
        result_keys = (
            "memo_candidates",
            "duplicate_no_write",
            "conflict_quarantine",
            "rejected",
            "deferred",
        )
        result_values = [promotion.get(key) for key in result_keys]
        if isinstance(nominated, int) and all(
            isinstance(value, int) and not isinstance(value, bool)
            for value in result_values
        ):
            if nominated != sum(result_values):
                issues.append("promotion result counts must reconcile")

    portability = aggregate.get("portability")
    if isinstance(portability, Mapping):
        tested = portability.get("model_pins_tested")
        portable = portability.get("portable_result_count")
        nonportable = portability.get("nonportable_result_count")
        if all(
            isinstance(value, int) and not isinstance(value, bool)
            for value in (tested, portable, nonportable)
        ) and tested != portable + nonportable:
            issues.append("portability result counts must reconcile")

    operator = aggregate.get("operator")
    if isinstance(operator, Mapping):
        review = operator.get("review_minutes")
        saved = operator.get("saved_re_grounding_minutes")
        net = operator.get("net_minutes_saved")
        budget = operator.get("review_budget_minutes")
        benefit = operator.get("promotion_benefit_exceeds_burden")
        if all(isinstance(value, (int, float)) and not isinstance(value, bool)
               for value in (review, saved, net)):
            if net != saved - review:
                issues.append("operator net minutes must reconcile")
            if isinstance(budget, (int, float)) and not isinstance(budget, bool):
                expected_benefit = net > 0 and review <= budget
                if benefit != expected_benefit:
                    issues.append("promotion burden verdict does not match minutes")
    return issues
