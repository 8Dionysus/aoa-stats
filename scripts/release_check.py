#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _env() -> dict[str, str]:
    env = os.environ.copy()
    repo_candidates = {
        "AOA_EVALS_ROOT": (
            env.get("AOA_EVALS_ROOT"),
            str((REPO_ROOT / "aoa-evals").resolve()),
            str((REPO_ROOT / ".deps" / "aoa-evals").resolve()),
            str((REPO_ROOT.parent / "aoa-evals").resolve()),
        ),
        "AOA_AGENTS_ROOT": (
            env.get("AOA_AGENTS_ROOT"),
            str((REPO_ROOT / ".deps" / "aoa-agents").resolve()),
            str((REPO_ROOT.parent / "aoa-agents").resolve()),
        ),
        "AOA_PLAYBOOKS_ROOT": (
            env.get("AOA_PLAYBOOKS_ROOT"),
            str((REPO_ROOT / ".deps" / "aoa-playbooks").resolve()),
            str((REPO_ROOT.parent / "aoa-playbooks").resolve()),
        ),
        "AOA_MEMO_ROOT": (
            env.get("AOA_MEMO_ROOT"),
            str((REPO_ROOT / ".deps" / "aoa-memo").resolve()),
            str((REPO_ROOT.parent / "aoa-memo").resolve()),
        ),
        "AOA_SDK_ROOT": (
            env.get("AOA_SDK_ROOT"),
            str((REPO_ROOT / ".deps" / "aoa-sdk").resolve()),
            str((REPO_ROOT.parent / "aoa-sdk").resolve()),
        ),
        "AOA_8DIONYSUS_ROOT": (
            env.get("AOA_8DIONYSUS_ROOT"),
            str((REPO_ROOT / ".deps" / "8Dionysus").resolve()),
            str((REPO_ROOT.parent / "8Dionysus").resolve()),
        ),
    }
    for env_name, candidates in repo_candidates.items():
        for candidate in candidates:
            if candidate and Path(candidate).exists():
                env[env_name] = str(Path(candidate).resolve())
                break
    return env


COMMANDS = [
    ("check generated views", [sys.executable, "scripts/build_views.py", "--check"]),
    ("validate repo", [sys.executable, "scripts/validate_repo.py"]),
    ("run tests", [sys.executable, "-m", "pytest", "-q", "tests"]),
]


def run_step(label: str, command: list[str]) -> int:
    print(f"[run] {label}: {subprocess.list2cmdline(command)}", flush=True)
    completed = subprocess.run(command, cwd=REPO_ROOT, env=_env(), check=False)
    if completed.returncode != 0:
        print(f"[error] {label} failed with exit code {completed.returncode}", flush=True)
        return completed.returncode
    print(f"[ok] {label}", flush=True)
    return 0


def main() -> int:
    for label, command in COMMANDS:
        exit_code = run_step(label, command)
        if exit_code != 0:
            return exit_code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
