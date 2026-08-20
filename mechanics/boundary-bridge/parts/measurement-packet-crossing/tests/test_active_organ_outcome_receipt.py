from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.outcome import (  # noqa: E402
    normalized_outcome_receipt_digest,
    validate_outcome_receipt_semantics,
)


SCHEMA_PATH = (
    REPO_ROOT / "stats" / "measurement-contract" / "outcome-receipt.schema.json"
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


def load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def apply_mutation(payload: dict, mutation: dict) -> None:
    tokens = mutation["path"].lstrip("/").split("/")
    target = payload
    for token in tokens[:-1]:
        target = target[int(token)] if isinstance(target, list) else target[token]
    leaf = tokens[-1]
    if mutation["op"] == "remove":
        target.pop(int(leaf)) if isinstance(target, list) else target.pop(leaf)
    elif isinstance(target, list):
        target[int(leaf)] = mutation["value"]
    else:
        target[leaf] = mutation["value"]


def test_active_organ_outcome_examples_and_negative_corpus() -> None:
    schema = load_json(SCHEMA_PATH)
    suite = load_json(EXAMPLES_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    valid_by_id = {case["case_id"]: case["payload"] for case in suite["valid_cases"]}

    Draft202012Validator.check_schema(schema)
    assert schema["$id"].endswith("/outcome-receipt.schema.json")
    assert schema["properties"]["schema_version"]["const"] == "1.0.0"

    for case in suite["valid_cases"]:
        schema_errors = list(validator.iter_errors(case["payload"]))
        semantic_issues = validate_outcome_receipt_semantics(case["payload"])
        assert schema_errors == [], (case["case_id"], schema_errors)
        assert semantic_issues == [], (case["case_id"], semantic_issues)

    for case in suite["invalid_cases"]:
        payload = deepcopy(valid_by_id[case["base_case"]])
        apply_mutation(payload, case["mutation"])
        schema_errors = list(validator.iter_errors(payload))
        semantic_issues = validate_outcome_receipt_semantics(payload)
        if case["expected_failure"] == "schema":
            assert schema_errors, case["case_id"]
        else:
            assert any(
                case["expected_failure"] in issue for issue in semantic_issues
            ), (case["case_id"], semantic_issues)


def test_supported_attribution_requires_owner_external_proof() -> None:
    suite = load_json(EXAMPLES_PATH)
    payload = deepcopy(suite["valid_cases"][0]["payload"])
    payload["attribution"] = {
        "status": "supported",
        "confidence": "medium",
        "basis": "paired_evidence",
        "eval_verdict_ref": {
            "owner_repo": "aoa-evals",
            "artifact_ref": "receipt:aoa-evals/verdicts/run-a",
            "artifact_version": "1.0.0",
            "artifact_digest": "sha256:"
            "3535353535353535353535353535353535353535353535353535353535353535",
        },
        "counterfactual_ref": {
            "owner_repo": "aoa-evals",
            "artifact_ref": "receipt:aoa-evals/counterfactuals/run-a",
            "artifact_version": "1.0.0",
            "artifact_digest": "sha256:"
            "3636363636363636363636363636363636363636363636363636363636363636",
        },
        "causal_claim": "forbidden",
    }
    payload["content_digest"] = normalized_outcome_receipt_digest(payload)

    assert validate_outcome_receipt_semantics(payload) == []

    payload["attribution"]["confidence"] = "high"
    payload["attribution"]["counterfactual_ref"] = None
    payload["content_digest"] = normalized_outcome_receipt_digest(payload)
    issues = validate_outcome_receipt_semantics(payload)
    assert any("high confidence requires" in issue for issue in issues)


def test_outcome_receipt_never_becomes_action_or_training_authority() -> None:
    schema = load_json(SCHEMA_PATH)
    properties = schema["properties"]

    assert properties["semantic_authority"]["const"] == "none"
    assert properties["effect_authority"]["const"] == "none"
    assert properties["training_use"]["const"] == "forbidden"
    assert properties["raw_content_included"]["const"] is False
    assert properties["payload_refs_only"]["const"] is True
    assert properties["evaluation_posture"]["$ref"].endswith(
        "/evaluation_posture"
    )
    posture = schema["$defs"]["evaluation_posture"]["properties"]
    assert posture["access_count_used_as_utility"]["const"] is False
    assert posture["semantic_memory_transition_allowed"]["const"] is False


def test_phase6_supported_attribution_binds_holdout_judge_and_host_evidence() -> None:
    suite = load_json(EXAMPLES_PATH)
    payload = deepcopy(suite["valid_cases"][0]["payload"])

    assert payload["experiment_assignment"] == {
        "design": "randomized_holdout",
        "arm_id": "B",
        "assignment_digest": (
            "sha256:"
            "7373737373737373737373737373737373737373737373737373737373737373"
        ),
        "holdout": False,
        "always_shadow_counterfactual_ref": payload["attribution"][
            "counterfactual_ref"
        ],
    }
    assert payload["host_observation_refs"]
    assert payload["evaluator"]["role"] == "independent_judge"
    assert payload["evaluation_posture"]["eval_plane_status"] == "available"
    assert payload["evaluation_posture"]["policy_update_state"] == "proposal_only"
    assert validate_outcome_receipt_semantics(payload) == []


def test_unavailable_eval_plane_keeps_attribution_unknown_and_policy_frozen() -> None:
    suite = load_json(EXAMPLES_PATH)
    payload = deepcopy(suite["valid_cases"][2]["payload"])

    assert payload["evaluation_posture"]["eval_plane_status"] == "unavailable"
    assert payload["evaluation_posture"]["policy_update_state"] == "frozen"
    assert payload["attribution"]["status"] == "unknown"
    assert validate_outcome_receipt_semantics(payload) == []


def test_outcome_receipt_self_digest_detects_content_drift() -> None:
    suite = load_json(EXAMPLES_PATH)
    payload = deepcopy(suite["valid_cases"][0]["payload"])

    assert payload["content_digest"] == normalized_outcome_receipt_digest(payload)
    payload["consumer_id"] = "different-consumer"
    issues = validate_outcome_receipt_semantics(payload)
    assert any("normalized outcome receipt digest" in issue for issue in issues)


def test_public_protocol_validator_accepts_one_receipt_and_rejects_drift(
    tmp_path: Path,
) -> None:
    suite = load_json(EXAMPLES_PATH)
    valid_path = tmp_path / "valid-outcome.json"
    invalid_path = tmp_path / "invalid-outcome.json"
    valid = suite["valid_cases"][0]["payload"]
    invalid = deepcopy(valid)
    invalid["memory_used"] = False
    valid_path.write_text(json.dumps(valid), encoding="utf-8")
    invalid_path.write_text(json.dumps(invalid), encoding="utf-8")
    command = REPO_ROOT / "scripts" / "validate_stats_protocol.py"

    accepted = subprocess.run(
        [sys.executable, str(command), "--outcome-receipt", str(valid_path)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    rejected = subprocess.run(
        [sys.executable, str(command), "--outcome-receipt", str(invalid_path)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert accepted.returncode == 0, accepted.stderr
    assert rejected.returncode == 1
    assert "memory_used false forbids" in rejected.stderr
