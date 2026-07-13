from __future__ import annotations

import importlib.util
from copy import deepcopy
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


def reference_packet() -> dict[str, object]:
    return {
        "schema_version": "aoa_stats_measurement_packet_v1",
        "contract_ref": "stats/port.manifest.json#/measurements/0",
        "contract_version": "1.0.0",
        "measurement_id": "aoa-evals/run-count",
        "writer_repo": "aoa-evals",
        "observation_id": "aoa-evals:run-count:reference",
        "observed_at": "2026-07-12T12:00:00Z",
        "object_ref": {
            "kind": "eval-run",
            "id": "bounded-eval-runs:reference",
            "version": "reference",
        },
        "population": {
            "id": "bounded-eval-runs:reference",
            "definition_ref": "stats/port.manifest.json#/measurements/0/population",
            "size": 3,
        },
        "sample": {"size": 3, "selection": "owner census"},
        "cohort": None,
        "window": {
            "id": "source-revision:reference",
            "start": "2026-07-12T12:00:00Z",
            "end": "2026-07-12T12:00:00Z",
            "temporality": "interval",
        },
        "dimensions": {},
        "value": {
            "status": "observed",
            "kind": "count",
            "unit": "run",
            "number": 3,
        },
        "uncertainty": {
            "status": "not_applicable",
            "sample_size": 3,
            "method": "not_applicable",
            "reason": "The reference packet is a census.",
        },
        "provenance": {
            "evidence_refs": [
                {"kind": "owner-report-index", "ref": "reports/index.json"}
            ],
            "derivation_ref": "stats/README.md#run-count",
            "source_revision": "reference",
        },
        "reporting_rule": {
            "id": "aoa-evals/run-count/reference-census",
            "version": "1.0.0",
        },
        "posture": {
            "freshness": "current",
            "live_state": "reference",
            "privacy": "public",
            "raw_content_included": False,
        },
        "progress": {"state": "terminal", "completed": 3, "total": 3},
    }


def write_reference_port(
    tmp_path: Path,
    *,
    packet: dict[str, object] | None = None,
    packet_ref: str = "stats/packets/run-count.reference.json",
) -> Path:
    owner_root = tmp_path / "aoa-evals"
    stats_root = owner_root / "stats"
    packet_path = owner_root / packet_ref
    stats_root.mkdir(parents=True)
    port = local_port()
    port["exports"][0] = {
        "measurement_id": "aoa-evals/run-count",
        "posture": "reference",
        "packet_refs": [packet_ref],
        "evidence_refs": ["reports/index.json"],
    }
    port_path = stats_root / "port.manifest.json"
    port_path.write_text(json.dumps(port), encoding="utf-8")
    if packet is not None:
        packet_path.parent.mkdir(parents=True, exist_ok=True)
        packet_path.write_text(json.dumps(packet), encoding="utf-8")
    return port_path


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


def test_port_validation_resolves_and_checks_reference_packets(tmp_path: Path) -> None:
    port_path = write_reference_port(tmp_path, packet=reference_packet())

    assert validator.validate(REPO_ROOT, port_paths=[port_path]) == []


def test_port_validation_rejects_missing_and_escaping_packet_refs(tmp_path: Path) -> None:
    missing = write_reference_port(tmp_path / "missing")
    missing_issues = validator.validate(REPO_ROOT, port_paths=[missing])
    assert any("run-count.reference.json: file is missing" in issue for issue in missing_issues)

    escaping = write_reference_port(
        tmp_path / "escaping",
        packet_ref="../outside.reference.json",
    )
    escaping_issues = validator.validate(REPO_ROOT, port_paths=[escaping])
    assert any("escapes owner root" in issue for issue in escaping_issues)


def test_port_validation_rejects_false_packet_semantics_and_contract_link(
    tmp_path: Path,
) -> None:
    packet = deepcopy(reference_packet())
    packet["contract_ref"] = "stats/port.manifest.json#/measurements/999"
    packet["writer_repo"] = "aoa-stats"
    packet["value"]["number"] = -1
    packet["posture"]["live_state"] = "live"
    packet["provenance"]["evidence_refs"][0]["ref"] = "/home/operator/raw.json"
    port_path = write_reference_port(tmp_path, packet=packet)

    issues = validator.validate(REPO_ROOT, port_paths=[port_path])

    assert any("contract_ref must equal" in issue for issue in issues)
    assert any("writer_repo does not match contract owner_repo" in issue for issue in issues)
    assert any("observed count requires a non-negative integer number" in issue for issue in issues)
    assert any("reference-only contract cannot produce a live packet" in issue for issue in issues)
    assert any("posture.live_state must match export posture" in issue for issue in issues)
    assert any("uses a host-local path" in issue for issue in issues)
