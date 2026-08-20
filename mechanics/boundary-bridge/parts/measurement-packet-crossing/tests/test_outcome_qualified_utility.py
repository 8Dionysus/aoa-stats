from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.outcome import normalized_outcome_receipt_digest  # noqa: E402
from aoa_stats_builder.utility import (  # noqa: E402
    aggregate_episodic_utility,
    validate_episodic_utility_aggregate,
)


EXAMPLES_PATH = (
    REPO_ROOT
    / "mechanics"
    / "boundary-bridge"
    / "parts"
    / "measurement-packet-crossing"
    / "examples"
    / "active_organ_outcome_receipt_v1.examples.json"
)
SCHEMA_PATH = (
    REPO_ROOT
    / "mechanics"
    / "boundary-bridge"
    / "parts"
    / "measurement-packet-crossing"
    / "schemas"
    / "active_organ_episodic_utility_aggregate_v0.schema.json"
)


def load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def item_ref() -> dict[str, str]:
    return {
        "owner_repo": "aoa-memo",
        "artifact_ref": "memory:episode:test",
        "artifact_version": "1",
        "artifact_digest": "sha256:" + ("9" * 64),
    }


def test_utility_aggregate_is_descriptive_and_schema_valid() -> None:
    receipt = load_json(EXAMPLES_PATH)["valid_cases"][0]["payload"]
    aggregate = aggregate_episodic_utility(
        aggregate_id="aggregate:test:positive",
        item_ref=item_ref(),
        receipts=[receipt],
        produced_at="2026-07-29T12:00:00Z",
    )

    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = list(
        Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        ).iter_errors(aggregate)
    )
    assert errors == []
    assert validate_episodic_utility_aggregate(aggregate) == []
    assert aggregate["qualified_observation_count"] == 1
    assert aggregate["measurement"]["qualified_signed_outcome_mean"] == 1.0
    assert aggregate["access_count_used_as_utility"] is False
    assert aggregate["proof_verdict"] == "forbidden"
    assert aggregate["semantic_authority"] == "none"
    assert aggregate["effect_authority"] == "none"


def test_success_without_action_change_does_not_gain_qualified_utility() -> None:
    receipt = deepcopy(load_json(EXAMPLES_PATH)["valid_cases"][0]["payload"])
    receipt["action_after_memory"] = deepcopy(receipt["action_before_memory"])
    receipt["action_after_memory"]["phase"] = "after_memory"
    receipt["action_after_memory"]["observed_at"] = "2026-07-28T19:00:03-06:00"
    receipt["content_digest"] = normalized_outcome_receipt_digest(receipt)

    aggregate = aggregate_episodic_utility(
        aggregate_id="aggregate:test:no-action-change",
        item_ref=item_ref(),
        receipts=[receipt],
        produced_at="2026-07-29T12:00:00Z",
    )

    assert aggregate["action_change_count"] == 0
    assert aggregate["qualified_observation_count"] == 0
    assert aggregate["measurement"]["qualified_signed_outcome_mean"] == 0.0


def test_pending_delayed_outcome_keeps_aggregate_partial() -> None:
    receipt = load_json(EXAMPLES_PATH)["valid_cases"][1]["payload"]
    aggregate = aggregate_episodic_utility(
        aggregate_id="aggregate:test:pending",
        item_ref=item_ref(),
        receipts=[receipt],
        produced_at="2026-07-29T12:00:00Z",
    )

    assert aggregate["pending_or_overdue_delayed_count"] == 1
    assert aggregate["evidence_completeness"] == "partial"


def test_invalid_c10_receipt_is_rejected_before_aggregation() -> None:
    receipt = deepcopy(load_json(EXAMPLES_PATH)["valid_cases"][0]["payload"])
    receipt["memory_used"] = False

    try:
        aggregate_episodic_utility(
            aggregate_id="aggregate:test:invalid",
            item_ref=item_ref(),
            receipts=[receipt],
            produced_at="2026-07-29T12:00:00Z",
        )
    except ValueError as exc:
        assert "memory_used false forbids" in str(exc)
    else:
        raise AssertionError("invalid C10 receipt must be rejected")
