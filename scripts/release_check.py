#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_HOME_MANIFEST = REPO_ROOT / "stats" / "source_home.manifest.json"
MECHANICS_TOPOLOGY = REPO_ROOT / "mechanics" / "topology.json"
_REPO_ROOT_RESOLVED = REPO_ROOT.resolve()
_MANIFEST_ROUTE_FIELDS = (
    "source_routes",
    "public_contract_routes",
    "implementation_routes",
    "read_only_access_routes",
    "validator_routes",
    "generated_routes",
)
_FEEDBACK_FULL_FILES = {
    "mechanics/topology.json",
    "scripts/build_views.py",
    "scripts/release_check.py",
    "stats/source_home.manifest.json",
}


def _safe_repo_path(value: object) -> str | None:
    if not isinstance(value, str) or not value or "\x00" in value:
        return None
    if value.startswith("/") or "\\" in value or ":" in value or "//" in value:
        return None
    pieces = value.split("/")
    if any(piece in {"", ".", ".."} for piece in pieces):
        return None
    try:
        (REPO_ROOT / Path(*pieces)).resolve(strict=False).relative_to(_REPO_ROOT_RESOLVED)
    except ValueError:
        return None
    return "/".join(pieces)


def _metadata_route(value: object) -> str | None:
    directory = isinstance(value, str) and value.endswith("/")
    route = _safe_repo_path(value.rstrip("/") if isinstance(value, str) else value)
    if route is None or not (REPO_ROOT / route).exists():
        return None
    if directory and not (REPO_ROOT / route).is_dir():
        return None
    return route


def _checked_routes(values: object) -> list[str] | None:
    if not isinstance(values, list):
        return None
    routes = [_metadata_route(value) for value in values]
    return None if any(route is None for route in routes) else routes  # type: ignore[return-value]


def _is_test_file(route: str) -> bool:
    candidate = REPO_ROOT / route
    return candidate.is_file() and candidate.suffix == ".py" and candidate.name.startswith("test_")


def _part_test_files(part: dict[str, object]) -> list[str]:
    tests_root = REPO_ROOT / str(part["path"]) / "tests"
    if not tests_root.is_dir():
        return []
    return sorted(str(test.relative_to(REPO_ROOT)) for test in tests_root.rglob("test_*.py") if test.is_file())


def _load_feedback_catalog() -> tuple[list[dict[str, object]], list[dict[str, object]]] | None:
    try:
        manifest = json.loads(SOURCE_HOME_MANIFEST.read_text(encoding="utf-8"))
        topology = json.loads(MECHANICS_TOPOLOGY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(manifest, dict) or manifest.get("owner_repo") != "aoa-stats":
        return None
    raw_families = manifest.get("families")
    if not isinstance(raw_families, list) or not raw_families:
        return None
    families: list[dict[str, object]] = []
    family_ids: set[str] = set()
    for family in raw_families:
        family_id = family.get("id") if isinstance(family, dict) else None
        if not isinstance(family_id, str) or not family_id or family_id in family_ids:
            return None
        routes: list[str] = []
        validators: list[str] = []
        for field in _MANIFEST_ROUTE_FIELDS:
            checked = _checked_routes(family.get(field, []))
            if checked is None:
                return None
            routes.extend(checked)
            if field == "validator_routes":
                validators.extend(checked)
        mechanic_routes = family.get("mechanic_routes", [])
        if not isinstance(mechanic_routes, list):
            return None
        for mechanic_route in mechanic_routes:
            route = _metadata_route(mechanic_route.get("path")) if isinstance(mechanic_route, dict) else None
            if route is None:
                return None
            routes.append(route)
        family_ids.add(family_id)
        families.append({"id": family_id, "routes": routes, "validators": validators})

    packages = topology.get("active_packages") if isinstance(topology, dict) else None
    if not isinstance(packages, list) or not packages:
        return None
    parts: list[dict[str, object]] = []
    seen_parts: set[str] = set()
    for package in packages:
        if not isinstance(package, dict):
            return None
        package_name = _safe_repo_path(package.get("path"))
        active_parts = package.get("active_part_routes")
        package_root = _safe_repo_path(f"mechanics/{package_name}") if package_name else None
        if package_root is None or not (REPO_ROOT / package_root).is_dir() or not isinstance(active_parts, list):
            return None
        for part in active_parts:
            if not isinstance(part, dict):
                return None
            part_name = _safe_repo_path(part.get("path"))
            refs = part.get("stats_source_family_refs")
            part_path = _safe_repo_path(f"mechanics/{package_name}/parts/{part_name}") if package_name and part_name else None
            if (
                part_path is None
                or not (REPO_ROOT / part_path).is_dir()
                or part_path in seen_parts
                or not isinstance(refs, list)
                or not refs
                or any(not isinstance(ref, str) or ref not in family_ids for ref in refs)
            ):
                return None
            seen_parts.add(part_path)
            parts.append({"path": part_path, "families": tuple(refs)})
    return families, parts


def _route_matches(changed_path: str, route: str) -> bool:
    return changed_path == route or ((REPO_ROOT / route).is_dir() and changed_path.startswith(f"{route}/"))


def _feedback_full_reason(changed_path: str) -> str | None:
    if changed_path in _FEEDBACK_FULL_FILES:
        return "release, validator, mapping, or source-home input"
    if changed_path.startswith(".github/"):
        return "CI workflow input"
    if changed_path.startswith("scripts/") and Path(changed_path).name.startswith("validate_"):
        return "validator input"
    name = Path(changed_path).name
    if name == "conftest.py":
        return "pytest discovery input"
    return None


def _feedback_test_selection(changed_paths: list[str]) -> tuple[list[str] | None, str | None]:
    paths = []
    for value in changed_paths:
        safe = _safe_repo_path(value)
        if safe is None:
            print(f"changed path is not a safe repository-relative path: {value!r}", file=sys.stderr)
            raise SystemExit(2)
        paths.append(safe)
    catalog = _load_feedback_catalog()
    if catalog is None:
        return None, "malformed or unavailable authored mapping metadata"
    families, parts = catalog
    selected: set[str] = set()
    for changed_path in paths:
        if (reason := _feedback_full_reason(changed_path)) is not None:
            return None, f"{changed_path}: {reason}"
        part_matches = [part for part in parts if changed_path == part["path"] or changed_path.startswith(f"{part['path']}/")]
        if len(part_matches) > 1:
            return None, f"{changed_path}: ambiguous topology ownership"
        if part_matches:
            tests = _part_test_files(part_matches[0])
            if not tests:
                return None, f"{changed_path}: topology part has no local tests"
            selected.update(tests)
            continue
        matched = [family for family in families if any(_route_matches(changed_path, route) for route in family["routes"])]
        if len(matched) != 1:
            return None, f"{changed_path}: {'uncovered path' if not matched else 'shared family route'}"
        family = matched[0]
        family_id = str(family["id"])
        tests = {route for route in family["validators"] if _is_test_file(route)}
        tests.update(test for part in parts if family_id in part["families"] for test in _part_test_files(part))
        if not tests:
            return None, f"{changed_path}: family has no current validator tests"
        selected.update(tests)
    return (sorted(selected), None) if selected else (None, "no changed paths supplied")


def _usable_repo_candidate(candidate: str | None) -> bool:
    if not candidate:
        return False
    path = Path(candidate).expanduser()
    if not path.is_dir():
        return False
    git_marker = path / ".git"
    if not git_marker.exists():
        return True
    checked = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return checked.returncode == 0


def _env() -> dict[str, str]:
    env = os.environ.copy()
    repo_candidates = {
        "AOA_EVALS_ROOT": (
            env.get("AOA_EVALS_ROOT"),
            str((REPO_ROOT / "aoa-evals").resolve()),
            str((REPO_ROOT / ".deps" / "aoa-evals").resolve()),
            str((REPO_ROOT.parent / "aoa-evals").resolve()),
            "/srv/AbyssOS/aoa-evals",
        ),
        "AOA_AGENTS_ROOT": (
            env.get("AOA_AGENTS_ROOT"),
            str((REPO_ROOT / ".deps" / "aoa-agents").resolve()),
            str((REPO_ROOT.parent / "aoa-agents").resolve()),
            "/srv/AbyssOS/aoa-agents",
        ),
        "AOA_PLAYBOOKS_ROOT": (
            env.get("AOA_PLAYBOOKS_ROOT"),
            str((REPO_ROOT / ".deps" / "aoa-playbooks").resolve()),
            str((REPO_ROOT.parent / "aoa-playbooks").resolve()),
            "/srv/AbyssOS/aoa-playbooks",
        ),
        "AOA_MEMO_ROOT": (
            env.get("AOA_MEMO_ROOT"),
            str((REPO_ROOT / ".deps" / "aoa-memo").resolve()),
            str((REPO_ROOT.parent / "aoa-memo").resolve()),
            "/srv/AbyssOS/aoa-memo",
        ),
        "AOA_SDK_ROOT": (
            env.get("AOA_SDK_ROOT"),
            str((REPO_ROOT / ".deps" / "aoa-sdk").resolve()),
            str((REPO_ROOT.parent / "aoa-sdk").resolve()),
            "/srv/AbyssOS/aoa-sdk",
        ),
        "AOA_KAG_ROOT": (
            env.get("AOA_KAG_ROOT"),
            str((REPO_ROOT / ".deps" / "aoa-kag").resolve()),
            str((REPO_ROOT.parent / "aoa-kag").resolve()),
            "/srv/AbyssOS/aoa-kag",
        ),
        "AOA_8DIONYSUS_ROOT": (
            env.get("AOA_8DIONYSUS_ROOT"),
            str((REPO_ROOT / ".deps" / "8Dionysus").resolve()),
            str((REPO_ROOT.parent / "8Dionysus").resolve()),
            "/srv/AbyssOS/8Dionysus",
        ),
    }
    for env_name, candidates in repo_candidates.items():
        for candidate in candidates:
            if _usable_repo_candidate(candidate):
                assert candidate is not None
                env[env_name] = str(Path(candidate).resolve())
                break
    return env


COMMANDS = [
    ("check decision indexes", [sys.executable, "scripts/generate_decision_indexes.py", "--check"]),
    ("validate decision records", [sys.executable, "scripts/validate_decision_records.py"]),
    (
        "validate nested agent routes",
        [sys.executable, "scripts/validate_nested_agents.py", "--fail-on-untracked"],
    ),
    ("validate mechanics topology", [sys.executable, "scripts/validate_mechanics_topology.py"]),
    ("validate stats source home", [sys.executable, "scripts/validate_stats_source_home.py"]),
    ("check generated views", [sys.executable, "scripts/build_views.py", "--check"]),
    ("validate repo", [sys.executable, "scripts/validate_repo.py"]),
    (
        "validate OS Abyss summary catalog artifact bundle",
        [
            sys.executable,
            "scripts/validate_abyss_machine_summary_catalog_bundle.py",
            "--ephemeral",
        ],
    ),
    (
        "run root and mechanic tests",
        [sys.executable, "-m", "pytest", "-q", "tests", "mechanics",
         "-p", "xdist", "-n", "2", "--dist", "loadfile"],
    ),
]


def run_step(label: str, command: list[str], *, env: dict[str, str] | None = None) -> int:
    print(f"[run] {label}: {subprocess.list2cmdline(command)}", flush=True)
    completed = subprocess.run(command, cwd=REPO_ROOT, env=_env() if env is None else env, check=False)
    if completed.returncode != 0:
        print(f"[error] {label} failed with exit code {completed.returncode}", flush=True)
        return completed.returncode
    print(f"[ok] {label}", flush=True)
    return 0


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the complete or advisory aoa-stats validation gate.")
    parser.add_argument("--feedback", action="store_true", help="select affected tests from authored routes")
    parser.add_argument("--changed-path", action="append", dest="changed_paths", default=[])
    parser.add_argument("--lf", action="store_true", help="retry only pytest's last failures within feedback")
    args = parser.parse_args(argv)
    if args.feedback != bool(args.changed_paths):
        parser.error("--feedback and at least one --changed-path must be supplied together")
    if args.lf and not args.feedback:
        parser.error("--lf is available only with --feedback")
    return args


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.feedback:
        test_files, fallback_reason = _feedback_test_selection(args.changed_paths)
        if test_files is None:
            print(f"[feedback] fallback to complete release gate: {fallback_reason}", flush=True)
        else:
            print(f"[feedback] selected {len(test_files)} test files", flush=True)
            if args.lf:
                print("[feedback] --lf is a retry hint; run without --lf for the complete selected set", flush=True)
            env = _env()
            env["PYTEST_ADDOPTS"] = ""
            env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
            command = [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "-c",
                "/dev/null",
                "--rootdir",
                str(REPO_ROOT),
                "--confcutdir",
                str(REPO_ROOT),
            ]
            if args.lf:
                command.append("--lf")
            command.extend(test_files)
            return run_step(
                "run affected feedback tests",
                command,
                env=env,
            )
    for label, command in COMMANDS:
        exit_code = run_step(label, command)
        if exit_code != 0:
            return exit_code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
