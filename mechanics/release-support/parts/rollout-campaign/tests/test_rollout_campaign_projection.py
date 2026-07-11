from __future__ import annotations

import hashlib
import inspect
import json
import os
import sys
from copy import deepcopy
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder import rollout_cadence  # noqa: E402
from aoa_stats_builder.rollout_cadence_sources import (  # noqa: E402
    RolloutCadenceInputBundle,
    load_rollout_cadence_reference_bundle,
    rollout_cadence_reference_paths,
)


def owner_root() -> Path:
    configured = os.environ.get("AOA_8DIONYSUS_ROOT")
    candidates = (
        Path(configured).expanduser() if configured else None,
        REPO_ROOT / ".deps" / "8Dionysus",
        Path("/srv/AbyssOS/8Dionysus"),
        REPO_ROOT.parent / "8Dionysus",
    )
    for candidate in candidates:
        if candidate is not None and candidate.is_dir():
            return candidate.resolve()
    raise AssertionError("could not resolve the pinned 8Dionysus owner checkout")


def mutable_inputs() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]
]:
    return load_rollout_cadence_reference_bundle(owner_root()).mutable_parts()


def test_reference_adapter_and_campaign_projection_preserve_committed_bytes() -> None:
    bundle = load_rollout_cadence_reference_bundle(owner_root())

    projected = rollout_cadence.build_rollout_campaign_summary(
        bundle.source,
        bundle.campaign,
        bundle.review,
        bundle.rollback,
    )
    committed_path = REPO_ROOT / "generated/rollout_campaign_summary.min.json"
    example_path = (
        REPO_ROOT / "mechanics/release-support/parts/rollout-campaign/examples/"
        "rollout_campaign_summary.example.json"
    )
    committed = json.loads(committed_path.read_text(encoding="utf-8"))
    example = json.loads(example_path.read_text(encoding="utf-8"))
    schema = json.loads(
        (REPO_ROOT / "schemas/rollout-campaign-summary.schema.json").read_text(
            encoding="utf-8"
        )
    )

    assert projected == committed == example
    Draft202012Validator(schema).validate(projected)
    assert hashlib.sha256(committed_path.read_bytes()).hexdigest() == (
        "26a608eb06db27a43338c9e11cdccd8cf5651f62ee64e63806fb4a9a8bb219d1"
    )
    assert projected["generated_from"]["receipt_input_paths"] == [
        "8Dionysus/examples/rollout_campaign_window.example.json",
        "8Dionysus/examples/drift_review_window.example.json",
        "8Dionysus/examples/rollback_followthrough_window.example.json",
    ]


def test_reference_paths_are_exactly_the_three_owner_examples() -> None:
    root = owner_root()

    assert rollout_cadence_reference_paths(root) == (
        root / "examples/rollout_campaign_window.example.json",
        root / "examples/drift_review_window.example.json",
        root / "examples/rollback_followthrough_window.example.json",
    )


def test_projection_core_has_no_filesystem_or_environment_dependency() -> None:
    source = inspect.getsource(rollout_cadence)

    assert "pathlib" not in source
    assert "os.environ" not in source
    assert "read_text(" not in source


def test_input_bundle_is_deeply_immutable_and_mutable_parts_are_detached() -> None:
    source, campaign, review, rollback = mutable_inputs()
    bundle = RolloutCadenceInputBundle(source, campaign, review, rollback)

    source["receipt_input_paths"].append("later")
    campaign["rollout_campaign_refs"].append("ROLL-20260413-later-03")
    review["signals"]["path_drift"] = True
    rollback["bounded_scope"]["paths"].append("later")

    assert len(bundle.source["receipt_input_paths"]) == 3
    assert len(bundle.campaign["rollout_campaign_refs"]) == 2
    assert bundle.review["signals"]["path_drift"] is False
    assert len(bundle.rollback["bounded_scope"]["paths"]) == 2
    with pytest.raises(TypeError):
        bundle.campaign["state"] = "closed"  # type: ignore[index]
    with pytest.raises(TypeError):
        bundle.review["signals"]["hook_drift"] = False  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        bundle.source = {}  # type: ignore[misc]

    detached = bundle.mutable_parts()
    detached[1]["state"] = "closed"
    assert bundle.campaign["state"] == "open"


def test_campaign_projection_does_not_mutate_inputs() -> None:
    inputs = mutable_inputs()
    original = deepcopy(inputs)

    rollout_cadence.build_rollout_campaign_summary(*inputs)

    assert inputs == original


@pytest.mark.parametrize(
    ("input_index", "field", "message"),
    (
        (1, "state", "rollout campaign window is missing required fields: state"),
        (2, "status", "drift review window is missing required fields: status"),
        (2, "decision", "drift review window is missing required fields: decision"),
        (
            3,
            "status",
            "rollback followthrough window is missing required fields: status",
        ),
    ),
)
def test_chain_rejects_missing_fields_instead_of_defaulting_them(
    input_index: int, field: str, message: str
) -> None:
    inputs = list(mutable_inputs())
    inputs[input_index].pop(field)

    with pytest.raises(rollout_cadence.ReceiptValidationError, match=message):
        rollout_cadence.build_rollout_campaign_summary(*inputs)


@pytest.mark.parametrize("target", ("review", "rollback"))
def test_chain_rejects_campaign_ref_mismatch(target: str) -> None:
    source, campaign, review, rollback = mutable_inputs()
    payload = review if target == "review" else rollback
    payload["campaign_ref"] = "CAMP-20260412-other-campaign-99"

    with pytest.raises(
        rollout_cadence.ReceiptValidationError,
        match="must reference the loaded campaign window",
    ):
        rollout_cadence.build_rollout_campaign_summary(
            source, campaign, review, rollback
        )


@pytest.mark.parametrize("target", ("review", "rollback"))
def test_chain_rejects_rollback_anchor_mismatch(target: str) -> None:
    source, campaign, review, rollback = mutable_inputs()
    payload = review if target == "review" else rollback
    payload["rollback_anchor"] = "ROLL-20260411-other-stable-99"

    with pytest.raises(
        rollout_cadence.ReceiptValidationError,
        match="anchor must reference the campaign stable rollout",
    ):
        rollout_cadence.build_rollout_campaign_summary(
            source, campaign, review, rollback
        )


def test_chain_rejects_latest_ref_outside_campaign_rollout_refs() -> None:
    source, campaign, review, rollback = mutable_inputs()
    campaign["latest_rollout_campaign_ref"] = "ROLL-20260413-not-listed-03"

    with pytest.raises(
        rollout_cadence.ReceiptValidationError,
        match="latest rollout ref must belong to rollout_campaign_refs",
    ):
        rollout_cadence.build_rollout_campaign_summary(
            source, campaign, review, rollback
        )


@pytest.mark.parametrize(
    ("target", "value"),
    (
        ("review", "2026-04-12T19:59:00Z"),
        ("rollback", "2026-04-12T20:09:00Z"),
    ),
)
def test_chain_rejects_out_of_order_flow_timestamps(target: str, value: str) -> None:
    source, campaign, review, rollback = mutable_inputs()
    if target == "review":
        review["reviewed_at"] = value
    else:
        rollback["prepared_at"] = value

    with pytest.raises(
        rollout_cadence.ReceiptValidationError,
        match="timestamps must follow the bounded flow",
    ):
        rollout_cadence.build_rollout_campaign_summary(
            source, campaign, review, rollback
        )


def test_chain_rejects_unparseable_required_timestamp() -> None:
    source, campaign, review, rollback = mutable_inputs()
    campaign["window_opened_at"] = "not-a-date"

    with pytest.raises(
        rollout_cadence.ReceiptValidationError,
        match="window_opened_at must be a date-time",
    ):
        rollout_cadence.build_rollout_campaign_summary(
            source, campaign, review, rollback
        )


def test_projection_rejects_generated_from_timestamp_drift() -> None:
    source, campaign, review, rollback = mutable_inputs()
    source["latest_observed_at"] = "2026-04-12T20:11:00Z"

    with pytest.raises(
        rollout_cadence.ReceiptValidationError,
        match="latest_observed_at must match the rollback preparation",
    ):
        rollout_cadence.build_rollout_campaign_summary(
            source, campaign, review, rollback
        )


def test_projection_rejects_noncanonical_input_provenance() -> None:
    source, campaign, review, rollback = mutable_inputs()
    source["receipt_input_paths"] = ["fake:a", "fake:b", "fake:c"]

    with pytest.raises(
        rollout_cadence.ReceiptValidationError,
        match="must keep the canonical three owner-example refs",
    ):
        rollout_cadence.build_rollout_campaign_summary(
            source, campaign, review, rollback
        )
