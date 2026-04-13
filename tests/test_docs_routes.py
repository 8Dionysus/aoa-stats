from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REFRESH_LIVE_STATS_PATH = REPO_ROOT / "scripts" / "refresh_live_stats.py"


def load_refresh_live_stats_module():
    spec = importlib.util.spec_from_file_location("refresh_live_stats", REFRESH_LIVE_STATS_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_readme_and_docs_map_route_current_direction_through_roadmap() -> None:
    readme = read_text("README.md")
    docs_readme = read_text("docs/README.md")
    roadmap = read_text("ROADMAP.md")

    assert "ROADMAP.md" in readme
    assert "README.md#current-v0-surface" in readme
    assert "../ROADMAP.md" in docs_readme
    assert "../README.md#current-v0-surface" in docs_readme
    assert "current repo-owned direction surface" in roadmap
    assert "README.md#current-v0-surface" in roadmap
    assert "not to widen into a dashboard empire" in roadmap


def test_agents_reads_roadmap_before_boundaries() -> None:
    agents = read_text("AGENTS.md")

    roadmap_step = "2. `ROADMAP.md`"
    boundaries_step = "3. `docs/BOUNDARIES.md`"

    assert roadmap_step in agents
    assert boundaries_step in agents
    assert agents.index(roadmap_step) < agents.index(boundaries_step)


def test_live_session_docs_list_every_refresh_live_summary_output() -> None:
    refresh_live_stats = load_refresh_live_stats_module()
    docs = read_text("docs/LIVE_SESSION_USE.md")

    for output_name in refresh_live_stats.SUMMARY_OUTPUT_NAMES:
        assert f"`state/generated/{output_name}`" in docs
        assert f"`generated/{output_name}`" in docs
