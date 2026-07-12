from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys

import pytest
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.surface_catalog import (  # noqa: E402
    PUBLIC_DEFERRED_FIELDS,
    SurfaceProfileError,
    load_surface_profiles,
    public_surface_profiles,
)


PART_ROOT = REPO_ROOT / "mechanics/antifragility/parts/antifragility-vector"
PROFILE_REF = "stats/read-models/deferred/antifragility_vector.profile.json"
OWNER_TRUTH_INPUTS = [
    "ATM10-Agent/scripts/hybrid_query_demo.py",
    "ATM10-Agent/schemas/stressor_receipt_v1.json",
    "ATM10-Agent/examples/stressor_receipt.retrieval_only_fallback.example.json",
    "ATM10-Agent/schemas/adaptation_delta_v1.json",
    "ATM10-Agent/examples/adaptation_delta.retrieval_only_fallback.example.json",
    "aoa-evals/evals/stress/aoa-antifragility-posture/EVAL.md",
    "aoa-evals/evals/stress/aoa-antifragility-posture/reports/summary.schema.json",
    "aoa-evals/evals/stress/aoa-antifragility-posture/reports/example-report.json",
]
ACTIVATION_GAPS = [
    "ATM10-Agent runtime stressor receipts are not registered in the aoa-stats live receipt source registry.",
    "ATM10-Agent adaptation_delta_v1 remains schema-and-example only and has no runtime publisher.",
    "aoa-evals aoa-antifragility-posture remains draft and has no executed report chain over the current ATM10-Agent runtime receipts.",
    "No repeated owner/eval window demonstrates movement for the same ATM10-Agent stressor family.",
]


def load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_contract_example_is_valid_and_explicitly_suppressed() -> None:
    schema = load_json(PART_ROOT / "schemas/antifragility_vector_v1.json")
    payload = load_json(PART_ROOT / "examples/antifragility_vector.example.json")

    errors = list(Draft202012Validator(schema).iter_errors(payload))

    assert errors == []
    assert payload["inputs"]["adaptation_delta_refs"] == []
    assert payload["sample_size"]["adaptation_count"] == 0
    assert payload["suppression"]["status"] == "insufficient_evidence"
    assert set(payload["vector"].values()) == {None}


def test_schema_requires_nonempty_receipt_and_eval_refs() -> None:
    schema = load_json(PART_ROOT / "schemas/antifragility_vector_v1.json")
    payload = load_json(PART_ROOT / "examples/antifragility_vector.example.json")
    malformed = deepcopy(payload)
    malformed["inputs"]["receipt_refs"] = []
    malformed["inputs"]["eval_report_refs"] = []

    errors = list(Draft202012Validator(schema).iter_errors(malformed))

    assert any(
        list(error.absolute_path) == ["inputs", "receipt_refs"] for error in errors
    )
    assert any(
        list(error.absolute_path) == ["inputs", "eval_report_refs"]
        for error in errors
    )


def test_schema_requires_explicit_suppression() -> None:
    schema = load_json(PART_ROOT / "schemas/antifragility_vector_v1.json")
    payload = load_json(PART_ROOT / "examples/antifragility_vector.example.json")
    del payload["suppression"]

    errors = list(Draft202012Validator(schema).iter_errors(payload))

    assert any(
        error.validator == "required" and "suppression" in error.message
        for error in errors
    )


def test_deferred_profile_projects_grounding_without_active_publication() -> None:
    profile = load_json(REPO_ROOT / PROFILE_REF)
    _, public_deferred = public_surface_profiles(REPO_ROOT / "stats/read-models")
    catalog = load_json(REPO_ROOT / "generated/summary_surface_catalog.min.json")
    public_profile = {
        field: profile[field] for field in PUBLIC_DEFERRED_FIELDS
    }

    assert profile["input_posture"] == "partial_owner_runtime_draft_eval_chain"
    assert profile["owner_truth_inputs"] == OWNER_TRUTH_INPUTS
    assert profile["activation_gaps"] == ACTIVATION_GAPS
    assert profile["consumer_risk"] == "high"
    assert public_deferred == [public_profile]
    assert catalog["deferred_contract_surfaces"] == public_deferred
    assert "surface_ref" not in profile
    assert "catalog_order" not in profile
    assert "live_state_capable" not in profile
    assert "antifragility_vector" not in {
        surface["name"] for surface in catalog["surfaces"]
    }
    assert not (REPO_ROOT / "generated/antifragility_vector.min.json").exists()


@pytest.mark.parametrize("field", ["owner_truth_inputs", "activation_gaps"])
@pytest.mark.parametrize("invalid", [[], ["duplicate", "duplicate"]])
def test_deferred_profile_rejects_empty_or_duplicate_grounding(
    tmp_path: Path,
    field: str,
    invalid: list[str],
) -> None:
    profile_root = shutil.copytree(
        REPO_ROOT / "stats/read-models",
        tmp_path / "read-models",
    )
    profile_path = profile_root / "deferred/antifragility_vector.profile.json"
    profile = load_json(profile_path)
    profile[field] = invalid
    profile_path.write_text(
        json.dumps(profile, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(
        SurfaceProfileError,
        match=rf"{field} must be a non-empty unique string list",
    ):
        load_surface_profiles(profile_root)
