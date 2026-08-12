from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aoa_stats_builder.receipt_abi import validate_receipt_abi_governance  # noqa: E402


def test_receipt_abi_governance_passes_for_current_repo() -> None:
    assert validate_receipt_abi_governance(repo_root=ROOT, workspace_root=ROOT.parent) == []


def test_receipt_abi_governance_detects_registry_drift(tmp_path: Path) -> None:
    repo = tmp_path / "aoa-stats"
    (repo / "schemas").mkdir(parents=True)
    (repo / "stats" / "intake-contract").mkdir(parents=True)
    schema = json.loads((ROOT / "schemas" / "stats-event-envelope.schema.json").read_text(encoding="utf-8"))
    registry = json.loads(
        (ROOT / "stats" / "intake-contract" / "event-kind-registry.json").read_text(
            encoding="utf-8"
        )
    )
    registry["event_kinds"] = registry["event_kinds"][:-1]
    (repo / "schemas" / "stats-event-envelope.schema.json").write_text(
        json.dumps(schema, indent=2) + "\n",
        encoding="utf-8",
    )
    (repo / "stats" / "intake-contract" / "event-kind-registry.json").write_text(
        json.dumps(registry, indent=2) + "\n",
        encoding="utf-8",
    )

    errors = validate_receipt_abi_governance(repo_root=repo, workspace_root=tmp_path)

    assert any("active registry event kinds must match" in error for error in errors)


def test_receipt_abi_governance_rejects_non_string_schema_enum_members(tmp_path: Path) -> None:
    repo = tmp_path / "aoa-stats"
    (repo / "schemas").mkdir(parents=True)
    (repo / "stats" / "intake-contract").mkdir(parents=True)
    schema = json.loads((ROOT / "schemas" / "stats-event-envelope.schema.json").read_text(encoding="utf-8"))
    registry = json.loads(
        (ROOT / "stats" / "intake-contract" / "event-kind-registry.json").read_text(
            encoding="utf-8"
        )
    )
    schema["properties"]["event_kind"]["enum"].append(123)
    (repo / "schemas" / "stats-event-envelope.schema.json").write_text(
        json.dumps(schema, indent=2) + "\n",
        encoding="utf-8",
    )
    (repo / "stats" / "intake-contract" / "event-kind-registry.json").write_text(
        json.dumps(registry, indent=2) + "\n",
        encoding="utf-8",
    )

    errors = validate_receipt_abi_governance(repo_root=repo, workspace_root=tmp_path)

    assert any("event_kind.enum must contain only non-empty strings" in error for error in errors)


def test_receipt_abi_governance_checks_current_evals_mirror_route(tmp_path: Path) -> None:
    repo = tmp_path / "aoa-stats"
    (repo / "schemas").mkdir(parents=True)
    (repo / "stats" / "intake-contract").mkdir(parents=True)
    schema = json.loads(
        (ROOT / "schemas" / "stats-event-envelope.schema.json").read_text(encoding="utf-8")
    )
    registry = json.loads(
        (ROOT / "stats" / "intake-contract" / "event-kind-registry.json").read_text(
            encoding="utf-8"
        )
    )
    (repo / "schemas" / "stats-event-envelope.schema.json").write_text(
        json.dumps(schema, indent=2) + "\n",
        encoding="utf-8",
    )
    (repo / "stats" / "intake-contract" / "event-kind-registry.json").write_text(
        json.dumps(registry, indent=2) + "\n",
        encoding="utf-8",
    )

    mirror_path = (
        tmp_path
        / "aoa-evals"
        / "mechanics"
        / "publication-receipts"
        / "parts"
        / "stats-envelope-mirror"
        / "schemas"
        / "stats-event-envelope.schema.json"
    )
    mirror_path.parent.mkdir(parents=True)
    mirror = dict(schema)
    mirror["$id"] = "https://aoa-evals/current-stats-envelope-mirror"
    mirror["title"] = "aoa-evals stats event envelope"
    mirror["description"] = "Local subordinate mirror used only for validation."
    mirror["x-canonical_schema_ref"] = (
        "repo:aoa-stats/schemas/stats-event-envelope.schema.json"
    )
    mirror["properties"]["event_kind"]["enum"] = mirror["properties"]["event_kind"][
        "enum"
    ][1:]
    mirror_path.write_text(json.dumps(mirror, indent=2) + "\n", encoding="utf-8")

    errors = validate_receipt_abi_governance(repo_root=repo, workspace_root=tmp_path)

    assert any(str(mirror_path) in error and "drifted" in error for error in errors)
