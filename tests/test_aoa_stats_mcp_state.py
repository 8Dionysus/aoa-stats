from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aoa_stats_mcp.repo_state import (  # noqa: E402
    RepoState,
    RepoStateError,
    build_surface_payload,
    find_repo_root,
    preview_json,
    safe_repo_path,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_fake_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "aoa-stats"
    _write(repo / "docs/BOUNDARIES.md", "# Boundaries\nsource repos own meaning")
    _write(repo / "docs/ARCHITECTURE.md", "# Architecture\nderived views only")
    _write(
        repo / "config/live_receipt_sources.json",
        json.dumps({"schema_version": 1, "sources": [{"name": "skills"}]}, indent=2),
    )
    _write(
        repo / "generated/object_summary.min.json",
        json.dumps({"objects": [{"id": 1}, {"id": 2}, {"id": 3}]}, indent=2),
    )
    _write(
        repo / "generated/summary_surface_catalog.min.json",
        json.dumps(
            {
                "schema_version": "aoa_stats_summary_surface_catalog_v2",
                "surfaces": [
                    {
                        "name": "object_summary",
                        "surface_ref": "generated/object_summary.min.json",
                        "schema_ref": "schemas/object-summary.schema.json",
                    }
                ],
            },
            indent=2,
        ),
    )
    return repo


def test_find_repo_root_from_nested_path(tmp_path: Path) -> None:
    repo = make_fake_repo(tmp_path)
    nested = repo / "src" / "aoa_stats_mcp"
    nested.mkdir(parents=True)
    assert find_repo_root(nested) == repo.resolve()


def test_safe_repo_path_rejects_escape(tmp_path: Path) -> None:
    repo = make_fake_repo(tmp_path)
    with pytest.raises(RepoStateError):
        safe_repo_path(repo, "../../etc/passwd")


def test_build_surface_payload_preview(tmp_path: Path) -> None:
    repo = make_fake_repo(tmp_path)
    state = RepoState(repo)
    payload = build_surface_payload(state, surface_name="object_summary", mode="preview", limit=2)
    assert payload["surface_ref"] == "generated/object_summary.min.json"
    assert payload["mode"] == "preview"
    assert payload["payload"]["objects_total_items"] == 3
    assert len(payload["payload"]["objects"]) == 2


def test_build_surface_payload_full(tmp_path: Path) -> None:
    repo = make_fake_repo(tmp_path)
    state = RepoState(repo)
    payload = build_surface_payload(state, surface_name="object_summary", mode="full")
    assert payload["payload"]["objects"][2]["id"] == 3


def test_preview_json_requires_positive_limit() -> None:
    with pytest.raises(RepoStateError):
        preview_json({"objects": [1, 2]}, limit=0)
