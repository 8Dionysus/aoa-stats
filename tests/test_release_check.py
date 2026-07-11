from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "release_check.py"


def load_release_check_module():
    spec = importlib.util.spec_from_file_location("release_check", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_repo_candidate_rejects_broken_git_worktree_but_accepts_vendored_tree(
    tmp_path: Path,
) -> None:
    release_check = load_release_check_module()
    broken = tmp_path / "broken-worktree"
    broken.mkdir()
    (broken / ".git").write_text(
        "gitdir: /missing/repository/.git/worktrees/broken\n",
        encoding="utf-8",
    )
    vendored = tmp_path / "vendored-repo"
    vendored.mkdir()

    assert release_check._usable_repo_candidate(str(broken)) is False
    assert release_check._usable_repo_candidate(str(vendored)) is True
    assert release_check._usable_repo_candidate(str(REPO_ROOT)) is True


def test_release_gate_runs_artifact_roundtrip_without_writing_dist() -> None:
    release_check = load_release_check_module()
    command = next(
        command
        for label, command in release_check.COMMANDS
        if label == "validate OS Abyss summary catalog artifact bundle"
    )

    assert command[-1] == "--ephemeral"
