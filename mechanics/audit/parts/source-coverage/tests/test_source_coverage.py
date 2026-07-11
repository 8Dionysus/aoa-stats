from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import random
import sys
from typing import Any

from jsonschema import Draft202012Validator
import pytest


REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.receipt_abi import (  # noqa: E402
    generated_from,
    load_receipts,
    resolve_active_receipts,
)
from aoa_stats_builder.source_coverage import (  # noqa: E402
    build_source_coverage_summary,
)


FIXTURE_REF = "stats/intake-contract/examples/session_harvest_family.receipts.example.json"
FIXTURE_PATH = REPO_ROOT / FIXTURE_REF
REGISTRY_REF = (
    "mechanics/recurrence/parts/live-receipt-refresh/config/"
    "live_receipt_sources.json"
)
REGISTRY_PATH = REPO_ROOT / REGISTRY_REF


def committed_inputs() -> tuple[
    list[dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
]:
    active = resolve_active_receipts(load_receipts([FIXTURE_PATH]))
    source = generated_from(active, [FIXTURE_REF])
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return active, source, registry


def build_committed() -> dict[str, Any]:
    active, source, registry = committed_inputs()
    return build_source_coverage_summary(
        active,
        source,
        source_registry=registry,
        source_registry_ref=REGISTRY_REF,
    )


def stable_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def synthetic_receipts(
    owner_counts: tuple[tuple[str, int], ...],
    event_counts: tuple[tuple[str, int], ...],
) -> list[dict[str, Any]]:
    owners = [owner for owner, count in owner_counts for _ in range(count)]
    events = [event for event, count in event_counts for _ in range(count)]
    assert len(owners) == len(events)
    return [
        {
            "object_ref": {"repo": owner},
            "event_kind": event,
            "observed_at": f"2026-07-11T00:{index:02d}:00Z",
        }
        for index, (owner, event) in enumerate(zip(owners, events, strict=True))
    ]


def test_committed_source_coverage_matches_schema_and_public_bytes() -> None:
    summary = build_committed()
    schema = json.loads(
        (REPO_ROOT / "schemas/source-coverage-summary.schema.json").read_text(
            encoding="utf-8"
        )
    )

    Draft202012Validator(schema).validate(summary)
    assert stable_json(summary) == (
        REPO_ROOT / "generated/source_coverage_summary.min.json"
    ).read_text(encoding="utf-8")
    assert summary["source_mode"] == "registry_backed_receipt_feed"
    assert summary["missing_owner_repos"] == [
        "aoa-memo",
        "aoa-playbooks",
        "aoa-techniques",
    ]
    assert summary["unexpected_owner_repos"] == ["Dionysus", "abyss-stack"]
    assert summary["thin_signal_flags"] == [
        "missing_owner_repos",
        "unexpected_owner_repos",
        "owner_share_dominant",
    ]


@pytest.mark.parametrize("seed", [0, 1, 7, 23])
def test_receipt_order_does_not_change_source_coverage(seed: int) -> None:
    active, source, registry = committed_inputs()
    shuffled = deepcopy(active)
    random.Random(seed).shuffle(shuffled)

    assert build_source_coverage_summary(
        shuffled,
        source,
        source_registry=registry,
        source_registry_ref=REGISTRY_REF,
    ) == build_committed()


def test_registry_order_and_duplicate_routes_do_not_change_owner_baseline() -> None:
    active, source, registry = committed_inputs()
    varied_registry = deepcopy(registry)
    varied_registry["sources"] = [
        *reversed(varied_registry["sources"]),
        deepcopy(varied_registry["sources"][0]),
    ]

    assert build_source_coverage_summary(
        active,
        source,
        source_registry=varied_registry,
        source_registry_ref=REGISTRY_REF,
    ) == build_committed()


def test_counts_conserve_owner_addressable_receipts_without_mutation() -> None:
    active, source, registry = committed_inputs()
    original_active = deepcopy(active)
    original_source = deepcopy(source)
    original_registry = deepcopy(registry)

    summary = build_source_coverage_summary(
        active,
        source,
        source_registry=registry,
        source_registry_ref=REGISTRY_REF,
    )

    assert sum(summary["owner_repo_counts"].values()) == summary[
        "active_receipt_total"
    ]
    assert sum(summary["event_kind_counts"].values()) == summary[
        "active_receipt_total"
    ]
    assert sum(owner["receipt_count"] for owner in summary["owners"]) == summary[
        "active_receipt_total"
    ]
    assert all(
        sum(owner["event_kind_counts"].values()) == owner["receipt_count"]
        for owner in summary["owners"]
    )
    assert active == original_active
    assert source == original_source
    assert registry == original_registry


def test_missing_registry_does_not_invent_owner_comparisons() -> None:
    active, source, _ = committed_inputs()

    summary = build_source_coverage_summary(active, source, source_registry=None)

    assert summary["source_mode"] == "receipt_feed_only"
    assert summary["input_registry_ref"] is None
    assert summary["expected_owner_repos"] == []
    assert summary["missing_owner_repos"] == []
    assert summary["unexpected_owner_repos"] == []
    assert "registry_not_provided" in summary["thin_signal_flags"]
    assert "unexpected_owner_repos" not in summary["thin_signal_flags"]


def test_dominance_flags_begin_at_seventy_percent() -> None:
    dominant = synthetic_receipts(
        (("owner-a", 7), ("owner-b", 3)),
        (("event-a", 7), ("event-b", 3)),
    )
    balanced = synthetic_receipts(
        (("owner-a", 6), ("owner-b", 4)),
        (("event-a", 6), ("event-b", 4)),
    )

    dominant_summary = build_source_coverage_summary(dominant, {"kind": "test"})
    balanced_summary = build_source_coverage_summary(balanced, {"kind": "test"})

    assert "owner_share_dominant" in dominant_summary["thin_signal_flags"]
    assert "event_kind_dominant" in dominant_summary["thin_signal_flags"]
    assert "owner_share_dominant" not in balanced_summary["thin_signal_flags"]
    assert "event_kind_dominant" not in balanced_summary["thin_signal_flags"]


def test_coverage_classes_preserve_sparse_active_and_rich_boundaries() -> None:
    receipts = synthetic_receipts(
        (("rich", 5), ("active", 2), ("sparse", 1)),
        (("event", 8),),
    )

    summary = build_source_coverage_summary(receipts, {"kind": "test"})

    assert {
        owner["owner_repo"]: owner["coverage_class"] for owner in summary["owners"]
    } == {"active": "active", "rich": "rich", "sparse": "sparse"}


def test_source_coverage_carries_no_verdict_or_route_authority() -> None:
    summary = build_committed()
    prohibited_authority_fields = {
        "canonical_truth",
        "decision",
        "proof_passed",
        "recommended_route",
        "score",
        "verdict",
        "workflow_activation",
    }

    assert prohibited_authority_fields.isdisjoint(summary)
