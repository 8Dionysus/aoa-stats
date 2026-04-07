from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "check_live_publishers.py"


def load_check_live_publishers_module():
    spec = importlib.util.spec_from_file_location("check_live_publishers", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_registry(path: Path, sources: list[dict]) -> None:
    path.write_text(
        json.dumps({"schema_version": 1, "sources": sources}, indent=2) + "\n",
        encoding="utf-8",
    )


def test_audit_live_publishers_accepts_empty_required_sources_by_default(tmp_path: Path) -> None:
    module = load_check_live_publishers_module()
    federation_root = tmp_path / "srv"
    skills_log = federation_root / "aoa-skills" / ".aoa" / "live_receipts"
    evals_log = federation_root / "aoa-evals" / ".aoa" / "live_receipts"
    skills_log.mkdir(parents=True)
    evals_log.mkdir(parents=True)

    (skills_log / "session-harvest-family.jsonl").write_text(
        json.dumps(
            {
                "event_kind": "harvest_packet_receipt",
                "event_id": "evt-harvest-0001",
                "observed_at": "2026-04-06T20:00:00Z",
                "run_ref": "run-skill-001",
                "session_ref": "session:test-audit",
                "actor_ref": "aoa-skills:session-donor-harvest",
                "object_ref": {
                    "repo": "aoa-skills",
                    "kind": "skill",
                    "id": "aoa-session-donor-harvest",
                    "version": "main",
                },
                "evidence_refs": [{"kind": "packet", "ref": "repo:aoa-skills/examples/session_growth_artifacts/harvest_packet.alpha.json"}],
                "payload": {"route_ref": "route:test-audit"},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (evals_log / "eval-result-receipts.jsonl").write_text("", encoding="utf-8")

    registry_path = tmp_path / "live_receipt_sources.json"
    write_registry(
        registry_path,
        [
            {
                "name": "skills",
                "repo": "aoa-skills",
                "relative_path": ".aoa/live_receipts/session-harvest-family.jsonl",
                "required": True,
            },
            {
                "name": "evals",
                "repo": "aoa-evals",
                "relative_path": ".aoa/live_receipts/eval-result-receipts.jsonl",
                "required": True,
            },
        ],
    )

    audits, errors = module.audit_live_publishers(
        registry_path=registry_path,
        federation_root=federation_root,
        require_non_empty=False,
    )

    assert errors == []
    assert [audit["status"] for audit in audits] == ["ok", "empty"]
    assert audits[0]["event_kinds"] == ["harvest_packet_receipt"]
    assert audits[1]["receipt_count"] == 0


def test_audit_live_publishers_fails_on_missing_required_source(tmp_path: Path) -> None:
    module = load_check_live_publishers_module()
    federation_root = tmp_path / "srv"
    registry_path = tmp_path / "live_receipt_sources.json"
    write_registry(
        registry_path,
        [
            {
                "name": "skills",
                "repo": "aoa-skills",
                "relative_path": ".aoa/live_receipts/session-harvest-family.jsonl",
                "required": True,
            }
        ],
    )

    audits, errors = module.audit_live_publishers(
        registry_path=registry_path,
        federation_root=federation_root,
        require_non_empty=False,
    )

    assert audits[0]["status"] == "missing"
    assert "missing required live receipt source" in errors[0]


def test_audit_live_publishers_fails_on_unknown_event_kind(tmp_path: Path) -> None:
    module = load_check_live_publishers_module()
    federation_root = tmp_path / "srv"
    skills_log = federation_root / "aoa-skills" / ".aoa" / "live_receipts"
    skills_log.mkdir(parents=True)
    (skills_log / "session-harvest-family.jsonl").write_text(
        json.dumps(
            {
                "event_kind": "harvest_packet_receipt_typo",
                "event_id": "evt-harvest-0002",
                "observed_at": "2026-04-06T20:10:00Z",
                "run_ref": "run-skill-002",
                "session_ref": "session:test-audit-invalid",
                "actor_ref": "aoa-skills:session-donor-harvest",
                "object_ref": {
                    "repo": "aoa-skills",
                    "kind": "skill",
                    "id": "aoa-session-donor-harvest",
                    "version": "main",
                },
                "evidence_refs": [{"kind": "packet", "ref": "repo:aoa-skills/examples/session_growth_artifacts/harvest_packet.alpha.json"}],
                "payload": {"route_ref": "route:test-audit-invalid"},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    registry_path = tmp_path / "live_receipt_sources.json"
    write_registry(
        registry_path,
        [
            {
                "name": "skills",
                "repo": "aoa-skills",
                "relative_path": ".aoa/live_receipts/session-harvest-family.jsonl",
                "required": True,
            }
        ],
    )

    audits, errors = module.audit_live_publishers(
        registry_path=registry_path,
        federation_root=federation_root,
        require_non_empty=False,
    )

    assert audits[0]["status"] == "invalid"
    assert "schemas/stats-event-envelope.schema.json" in errors[0]
