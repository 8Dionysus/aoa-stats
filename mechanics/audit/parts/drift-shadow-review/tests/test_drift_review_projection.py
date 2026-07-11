from __future__ import annotations

import hashlib
import json
import os
import sys
from copy import deepcopy
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
    load_rollout_cadence_reference_bundle,
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


def test_drift_review_projection_preserves_committed_bytes() -> None:
    bundle = load_rollout_cadence_reference_bundle(owner_root())

    projected = rollout_cadence.build_drift_review_summary(
        bundle.source,
        bundle.campaign,
        bundle.review,
        bundle.rollback,
    )
    committed_path = REPO_ROOT / "generated/drift_review_summary.min.json"
    example_path = (
        REPO_ROOT / "mechanics/audit/parts/drift-shadow-review/examples/"
        "drift_review_summary.example.json"
    )
    committed = json.loads(committed_path.read_text(encoding="utf-8"))
    example = json.loads(example_path.read_text(encoding="utf-8"))
    schema = json.loads(
        (REPO_ROOT / "schemas/drift-review-summary.schema.json").read_text(
            encoding="utf-8"
        )
    )

    assert projected == committed == example
    Draft202012Validator(schema).validate(projected)
    assert hashlib.sha256(committed_path.read_bytes()).hexdigest() == (
        "02318d6cc6840fb73375df845d844a8253e48f1a21a5b0e5e3c87ead55d7d96f"
    )


def test_drift_review_projection_does_not_mutate_inputs() -> None:
    inputs = mutable_inputs()
    original = deepcopy(inputs)

    rollout_cadence.build_drift_review_summary(*inputs)

    assert inputs == original


def test_missing_decision_is_rejected_instead_of_becoming_an_empty_count() -> None:
    source, campaign, review, rollback = mutable_inputs()
    review.pop("decision")

    with pytest.raises(
        rollout_cadence.ReceiptValidationError,
        match="drift review window is missing required fields: decision",
    ):
        rollout_cadence.build_drift_review_summary(source, campaign, review, rollback)


def test_review_requires_at_least_one_positive_drift_signal() -> None:
    source, campaign, review, rollback = mutable_inputs()
    review["signals"] = {name: False for name in rollout_cadence.DRIFT_SIGNAL_NAMES}

    with pytest.raises(
        rollout_cadence.ReceiptValidationError,
        match="must name at least one positive signal",
    ):
        rollout_cadence.build_drift_review_summary(source, campaign, review, rollback)


@pytest.mark.parametrize("bad_value", ("true", 1, None))
def test_review_rejects_non_boolean_signal_values(bad_value: object) -> None:
    source, campaign, review, rollback = mutable_inputs()
    review["signals"]["marketplace_drift"] = bad_value

    with pytest.raises(
        rollout_cadence.ReceiptValidationError,
        match="signals.marketplace_drift must be boolean",
    ):
        rollout_cadence.build_drift_review_summary(source, campaign, review, rollback)


def test_review_rejects_unsupported_signal_names() -> None:
    source, campaign, review, rollback = mutable_inputs()
    review["signals"]["doctor_clean"] = True

    with pytest.raises(
        rollout_cadence.ReceiptValidationError,
        match="signals has unsupported fields: doctor_clean",
    ):
        rollout_cadence.build_drift_review_summary(source, campaign, review, rollback)


@pytest.mark.parametrize("status", ("accepted", "closed", "rollback_considered"))
def test_reanchor_decision_requires_a_compatible_review_status(status: str) -> None:
    source, campaign, review, rollback = mutable_inputs()
    review["status"] = status

    with pytest.raises(
        rollout_cadence.ReceiptValidationError,
        match="reanchor_then_regenerate requires review_required or reanchor",
    ):
        rollout_cadence.build_drift_review_summary(source, campaign, review, rollback)


def test_ready_rollback_requires_post_rollback_review() -> None:
    source, campaign, review, rollback = mutable_inputs()
    rollback["post_rollback_review"] = "optional"

    with pytest.raises(
        rollout_cadence.ReceiptValidationError,
        match="ready_if_needed requires post_rollback_review=required",
    ):
        rollout_cadence.build_drift_review_summary(source, campaign, review, rollback)


def test_invalid_lineage_shape_is_rejected_instead_of_counted_as_zero() -> None:
    source, campaign, review, rollback = mutable_inputs()
    campaign["lineage_refs"]["candidate_refs"] = "candidate:not-a-list"

    with pytest.raises(
        rollout_cadence.ReceiptValidationError,
        match="lineage_refs.candidate_refs must be a string list",
    ):
        rollout_cadence.build_drift_review_summary(source, campaign, review, rollback)
