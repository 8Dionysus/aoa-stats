from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


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
