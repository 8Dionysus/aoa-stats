from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.inference_economy import (  # noqa: E402
    AUTHORITY_CEILING,
    COUNT_METRIC_PATHS,
    DURATION_METRIC_PATHS,
    INFERENCE_ECONOMY_OBSERVATION_SCHEMA,
    LIFECYCLE_PATHS,
    validate_inference_economy_observation,
)


SCHEMA_PATH = (
    REPO_ROOT
    / "stats"
    / "measurement-contract"
    / "inference-economy-observation.schema.json"
)


def content_ref(object_id: str, schema_version: str) -> dict[str, str]:
    return {
        "object_id": object_id,
        "owner_repo": "owner-source",
        "schema_version": schema_version,
        "digest": "sha256:" + "a" * 64,
    }


def evidence_ref(kind: str = "runtime") -> dict[str, str]:
    return {"kind": kind, "ref": f"owner-source:{kind}/observation-1"}


def metric(
    value: int | float | None,
    *,
    basis: str = "provider_reported",
    uncertainty: str = "exact",
    status: str = "observed",
    reason: str | None = None,
) -> dict[str, object]:
    return {
        "status": status,
        "basis": basis,
        "uncertainty": uncertainty,
        "value": value,
        "evidence_refs": [evidence_ref("metric")] if status == "observed" else [],
        "reason": reason,
    }


def lifecycle(
    value_field: str,
    value: str | None,
    *,
    status: str = "observed",
    ref_field: str | None = None,
) -> dict[str, object]:
    result: dict[str, object] = {
        "observation_status": status,
        value_field: value,
        "evidence_refs": [evidence_ref(value_field)] if status == "observed" else [],
        "reason": None if status == "observed" else f"{value_field} not available",
    }
    if ref_field is not None:
        result[ref_field] = (
            content_ref(f"{value_field}-1", f"owner_{value_field}_v1")
            if status == "observed"
            else None
        )
    return result


def observation() -> dict[str, object]:
    counts = {
        path: metric(1 if path != "activity.intermediate_volume.bytes" else 32)
        for path in COUNT_METRIC_PATHS
    }
    payload: dict[str, object] = {
        "schema_version": INFERENCE_ECONOMY_OBSERVATION_SCHEMA,
        "contract_version": "1.0.0",
        "observation_id": "economy-observation-1",
        "observed_at": "2026-08-26T14:00:00Z",
        "source_ref": content_ref("source-observation-1", "owner_source_v1"),
        "runtime_ref": content_ref("runtime-result-1", "owner_runtime_result_v1"),
        "observation_status": "complete",
        "tokens": {
            "input": counts["tokens.input"],
            "cached_input": metric(2, basis="exact_tokenizer"),
            "output": metric(3, basis="estimated", uncertainty="estimated"),
        },
        "activity": {
            "turns": counts["activity.turns"],
            "model_calls": counts["activity.model_calls"],
            "intermediate_volume": {
                "items": counts["activity.intermediate_volume.items"],
                "bytes": counts["activity.intermediate_volume.bytes"],
                "tokens": counts["activity.intermediate_volume.tokens"],
            },
            "compactions": counts["activity.compactions"],
            "losses": counts["activity.losses"],
            "retries": counts["activity.retries"],
            "rework": counts["activity.rework"],
        },
        "tools": {
            "schema_bytes": counts["tools.schema_bytes"],
            "schema_tokens": counts["tools.schema_tokens"],
            "calls": counts["tools.calls"],
        },
        "wall_time_seconds": metric(4.5),
        "runtime_outcome": {
            **lifecycle(
                "outcome",
                "success",
            ),
            "exit_code": 0,
        },
        "eval_verdict": lifecycle(
            "verdict",
            "not_reviewable",
            ref_field="verdict_ref",
        ),
        "closeout": lifecycle("state", "closed", ref_field="closeout_ref"),
        "owner_acceptance": lifecycle(
            "state",
            "accepted",
            ref_field="acceptance_ref",
        ),
        "provenance": {
            "evidence_refs": [evidence_ref("source")],
            "derivation_ref": "aoa-stats:inference-economy-observation-v1",
            "source_revision": "owner-source@revision-1",
        },
        "progress": {"state": "terminal", "completed": 1, "total": 1},
        "unknown_fields": [],
        "authority_ceiling": AUTHORITY_CEILING,
    }
    return payload


def path_set(payload: dict[str, object], path: str, value: object) -> None:
    parts = path.split(".")
    current: object = payload
    for part in parts[:-1]:
        assert isinstance(current, dict)
        current = current[part]
    assert isinstance(current, dict)
    current[parts[-1]] = value


def unresolved_fields(payload: dict[str, object]) -> list[str]:
    result: list[str] = []
    for path in (*COUNT_METRIC_PATHS, *DURATION_METRIC_PATHS):
        parts = path.split(".")
        current: object = payload
        for part in parts:
            assert isinstance(current, dict)
            current = current[part]
        assert isinstance(current, dict)
        if current["status"] != "observed":
            result.append(path)
    for path in LIFECYCLE_PATHS:
        current = payload[path]
        assert isinstance(current, dict)
        if current["observation_status"] != "observed":
            result.append(path)
    return sorted(result)


def test_schema_and_complete_observation_preserve_all_economy_axes() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    payload = observation()

    assert list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload)
    ) == []
    assert validate_inference_economy_observation(payload) == []
    assert payload["runtime_outcome"]["outcome"] == "success"
    assert payload["eval_verdict"]["verdict"] == "not_reviewable"
    assert payload["closeout"]["state"] == "closed"
    assert payload["owner_acceptance"]["state"] == "accepted"


def test_protocol_cli_accepts_an_observation_file(tmp_path: Path) -> None:
    observation_path = tmp_path / "inference-economy-observation.json"
    observation_path.write_text(
        json.dumps(observation()),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "validate_stats_protocol.py"),
            "--inference-economy-observation",
            str(observation_path),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "[ok] federated stats protocol and requested artifacts"


def test_partial_observation_keeps_missingness_and_unknown_fields_explicit() -> None:
    payload = observation()
    path_set(
        payload,
        "tokens.cached_input",
        metric(
            None,
            basis="unknown",
            uncertainty="not_estimated",
            status="unknown",
            reason="provider did not report cache usage",
        ),
    )
    path_set(
        payload,
        "activity.intermediate_volume.tokens",
        metric(
            None,
            basis="provider_reported",
            uncertainty="not_estimated",
            status="stale",
            reason="only an older observation is available",
        ),
    )
    payload["eval_verdict"] = lifecycle(
        "verdict", None, status="missing", ref_field="verdict_ref"
    )
    payload["closeout"] = lifecycle(
        "state", None, status="unknown", ref_field="closeout_ref"
    )
    payload["owner_acceptance"] = lifecycle(
        "state", None, status="missing", ref_field="acceptance_ref"
    )
    payload["observation_status"] = "partial"
    payload["progress"] = {"state": "partial", "completed": 1, "total": 3}
    payload["unknown_fields"] = unresolved_fields(payload)

    assert validate_inference_economy_observation(payload) == []


def test_semantics_reject_numeric_forgery_incomplete_status_and_private_refs() -> None:
    payload = observation()
    payload["tokens"]["input"]["value"] = None
    assert any(
        "tokens.input.value must be numeric" in issue
        for issue in validate_inference_economy_observation(payload)
    )

    payload = observation()
    payload["activity"]["retries"]["status"] = "unknown"
    payload["activity"]["retries"]["value"] = 1
    payload["activity"]["retries"]["reason"] = "not available"
    payload["unknown_fields"] = unresolved_fields(payload)
    assert any(
        "activity.retries.value must remain null" in issue
        for issue in validate_inference_economy_observation(payload)
    )

    payload = observation()
    payload["provenance"]["evidence_refs"][0]["ref"] = "/srv/private/transcript.jsonl"
    assert any(
        "portable evidence ref" in issue
        for issue in validate_inference_economy_observation(payload)
    )

    payload = observation()
    payload["provider"] = "provider-name"
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert list(Draft202012Validator(schema).iter_errors(payload))


def test_complete_observation_cannot_hide_unresolved_fields() -> None:
    payload = observation()
    payload["activity"]["losses"] = metric(
        None,
        basis="unknown",
        uncertainty="not_estimated",
        status="unknown",
        reason="loss events were not emitted",
    )
    payload["unknown_fields"] = unresolved_fields(payload)
    assert any(
        "complete observation cannot contain unresolved fields" in issue
        for issue in validate_inference_economy_observation(payload)
    )
