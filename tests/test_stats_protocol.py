from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_stats_protocol.py"
SPEC = importlib.util.spec_from_file_location("validate_stats_protocol", SCRIPT_PATH)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


def load_json(relative_path: str) -> dict[str, object]:
    payload = json.loads((REPO_ROOT / relative_path).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def local_port() -> dict[str, object]:
    measurement = {
        "schema_version": "aoa_stats_measurement_contract_v1",
        "measurement_id": "aoa-evals/run-count",
        "contract_version": "1.0.0",
        "owner_repo": "aoa-evals",
        "question_ref": "question:run-coverage",
        "semantic_class": "measure",
        "statistic": "count",
        "object_kind": "eval-run",
        "unit": {"symbol": "run", "quantity": "count"},
        "population": {
            "subject": "bounded eval runs",
            "definition": "runs admitted by one owner eval contract",
            "inclusion_rule": "run has an owner report",
            "exclusion_rule": "draft example without execution evidence",
            "sampling": "census",
        },
        "window": {"temporality": "interval", "clock": "event_time"},
        "dimensions": {"allowed": [], "prohibited": ["prompt", "session_id"]},
        "aggregation": {"operator": "sum", "across": ["window"]},
        "missingness": {
            "states": ["missing", "unknown", "stale"],
            "zero_is_observation": True,
        },
        "uncertainty": {"required": False, "methods": ["not_applicable"]},
        "provenance": {
            "evidence_refs_required": True,
            "source_revision_required": True,
        },
        "lifecycle": {"status": "active", "compatible_with": []},
        "privacy": {
            "classification": "public",
            "raw_content_allowed": False,
            "sensitive_dimensions_allowed": False,
        },
        "live_state": {"capability": "reference_only"},
        "authority_ceiling": "Weaker than aoa-evals run reports and verdicts.",
    }
    return {
        "schema_version": "aoa_stats_local_port_v1",
        "contract_version": "1.0.0",
        "owner_repo": "aoa-evals",
        "status": "active",
        "owner_boundary_ref": "AGENTS.md",
        "central_contract_refs": [
            "aoa-stats:stats/measurement-contract/measurement-contract.schema.json",
            "aoa-stats:stats/measurement-contract/measurement-packet.schema.json",
        ],
        "evidence_posture": {
            "live_state": "reference_only",
            "privacy": "public",
            "raw_content_allowed": False,
        },
        "questions": [
            {
                "id": "question:run-coverage",
                "question": "How many bounded eval runs have inspectable owner reports?",
                "consumer_refs": ["evals/README.md"],
            }
        ],
        "measurements": [measurement],
        "exports": [
            {
                "measurement_id": "aoa-evals/run-count",
                "posture": "declaration_only",
                "packet_refs": [],
                "evidence_refs": ["evals/README.md"],
            }
        ],
    }


def test_central_protocol_and_inventory_validate() -> None:
    assert validator.validate(REPO_ROOT) == []


def test_protocol_cli_has_reviewable_success_and_failure_contract(tmp_path: Path) -> None:
    success = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert success.returncode == 0
    assert success.stdout.strip() == "[ok] federated stats protocol and requested artifacts"

    missing_port = tmp_path / "missing-port.json"
    failure = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--port", str(missing_port)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert failure.returncode == 1
    assert f"[error] {missing_port}: file is missing" in failure.stderr


def test_local_port_contract_accepts_owner_meaning_without_live_claim() -> None:
    schemas, issues = validator._load_schemas(REPO_ROOT)
    assert issues == []
    registry = validator._registry(schemas)

    assert validator.validate_port_payload(
        local_port(),
        label="aoa-evals:stats/port.manifest.json",
        port_schema=schemas[validator.PORT_SCHEMA_PATH.as_posix()],
        registry=registry,
    ) == []


def test_local_port_rejects_foreign_writer_false_live_and_session_path() -> None:
    schemas, issues = validator._load_schemas(REPO_ROOT)
    assert issues == []
    registry = validator._registry(schemas)
    port = local_port()
    port["measurements"][0]["owner_repo"] = "aoa-stats"
    port["exports"][0] = {
        "measurement_id": "aoa-evals/run-count",
        "posture": "live",
        "packet_refs": ["/home/user/.aoa/sessions/transcript.jsonl"],
        "evidence_refs": ["/home/user/.aoa/sessions/transcript.jsonl"],
    }

    found = validator.validate_port_payload(
        port,
        label="aoa-evals:stats/port.manifest.json",
        port_schema=schemas[validator.PORT_SCHEMA_PATH.as_posix()],
        registry=registry,
    )

    assert any("owner_repo must match" in issue for issue in found)
    assert any("live export requires live-capable" in issue for issue in found)
    assert any("non-portable ref" in issue for issue in found)
