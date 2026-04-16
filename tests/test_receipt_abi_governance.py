from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aoa_stats_builder.receipt_abi import validate_receipt_abi_governance  # noqa: E402


def test_receipt_abi_governance_passes_for_current_repo() -> None:
    assert validate_receipt_abi_governance(repo_root=ROOT, workspace_root=ROOT.parent) == []


def test_receipt_abi_governance_detects_registry_drift(tmp_path: Path) -> None:
    repo = tmp_path / "aoa-stats"
    (repo / "schemas").mkdir(parents=True)
    (repo / "config").mkdir(parents=True)
    schema = json.loads((ROOT / "schemas" / "stats-event-envelope.schema.json").read_text(encoding="utf-8"))
    registry = json.loads((ROOT / "config" / "stats_event_kind_registry.json").read_text(encoding="utf-8"))
    registry["event_kinds"] = registry["event_kinds"][:-1]
    (repo / "schemas" / "stats-event-envelope.schema.json").write_text(
        json.dumps(schema, indent=2) + "\n",
        encoding="utf-8",
    )
    (repo / "config" / "stats_event_kind_registry.json").write_text(
        json.dumps(registry, indent=2) + "\n",
        encoding="utf-8",
    )

    errors = validate_receipt_abi_governance(repo_root=repo, workspace_root=tmp_path)

    assert any("active registry event kinds must match" in error for error in errors)
