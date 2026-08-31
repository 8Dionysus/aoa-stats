#!/usr/bin/env python3
"""Validate nested AGENTS.md guidance for aoa-stats."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_NAME = 'aoa-stats'

REQUIRED_AGENTS_DOCS: dict[str, tuple[str, ...]] = {
    '.github/AGENTS.md': ('GitHub platform surface', 'Repo Validation'),
    'docs/decisions/AGENTS.md': ('AOST-D-####-short-slug.md', 'Stats surfaces'),
    'evals/AGENTS.md': ('stats-layer eval pressure', 'aoa-evals'),
    'examples/AGENTS.md': ('Examples demonstrate derived stats contracts', 'without becoming canonical evidence'),
    'generated/AGENTS.md': ('Source repos own meaning', 'Do not hand-edit generated outputs'),
    'kag/AGENTS.md': (
        'local KAG provider home',
        'source-linked records',
        'stats/source_home.manifest.json',
        'supporting projections',
    ),
    'mechanics/AGENTS.md': ('source meaning', 'repeatable operation payload'),
    'mechanics/recurrence/parts/live-receipt-refresh/config/AGENTS.md': (
        'live_receipt_sources.json',
        'stats/intake-contract/event-kind-registry.json',
    ),
    'mechanics/recurrence/parts/live-receipt-refresh/systemd/AGENTS.md': (
        'user-service templates',
        'free of secrets',
    ),
    'schemas/AGENTS.md': ('Schema changes are contract changes', 'shared receipt envelope'),
    'scripts/AGENTS.md': ('build_views.py', 'derived-only'),
    'skills/AGENTS.md': (
        'canonical `aoa-stats/skills/` home',
        'managed OS user-profile copy',
    ),
    'src/AGENTS.md': ('aoa_stats_builder', 'workflow, proof, route, or quest authority'),
    'stats/AGENTS.md': ('source-authored meaning of stats families', 'source_home.manifest.json'),
    'stats/intake-contract/AGENTS.md': ('shared stats receipt envelope', 'Mechanics crosswalk'),
    'stats/measurement-contract/AGENTS.md': (
        'portable statistical grammar',
        'one writer owner',
    ),
    'stats/federation/AGENTS.md': (
        'compatibility shape',
        'host-specific paths',
    ),
    'stats/operation-contracts/AGENTS.md': (
        'part-local stats operations',
        'Do not add a public surface profile',
    ),
    'stats/read-models/AGENTS.md': ('source-authored surface profiles', 'surface-profile.schema.json'),
    'stats/surface-catalog/AGENTS.md': ('catalog entry shape', 'Mechanics crosswalk'),
    'tests/AGENTS.md': ('deterministic derivation', 'boundary integrity'),
}
ADVISORY_AGENT_DIRS: tuple[str, ...] = ('.agents/skills', 'docs', 'manifests/artifact_bundles')
HEADING_PREFIXES = ("# AGENTS.md", "# AGENTS")
IGNORED_DIRS = {
    ".deps",
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}
FENCE_MARKER = "`" * 3
RUNNABLE_FENCE_LANGS = {
    "bash",
    "console",
    "fish",
    "powershell",
    "pwsh",
    "sh",
    "shell",
    "shell-session",
    "zsh",
}
SHELL_FENCE_PATTERN = re.compile(
    r"^ {0,3}```(?:bash|console|fish|powershell|pwsh|sh|shell|shell-session|zsh)(?:\s+.*)?$",
    re.IGNORECASE,
)
FENCE_OPEN_PATTERN = re.compile(
    r"^ {0,3}" + re.escape(FENCE_MARKER) + r".*$"
)
COMMAND_NAME_PATTERN = (
    r"(?:python(?:\d+(?:\.\d+)*)?|pytest|uv(?:\s+run)?|pip(?:\d+)?|"
    r"ruff|mypy|tox|hatch|poetry|aoa|git|make|bash|sh|zsh|fish|"
    r"powershell|pwsh|systemctl|curl|jq|rg|grep|sed|awk|find|chmod|"
    r"mkdir|cp|mv|rm|source(?=\s+[./$~]))"
)
COMMAND_PREFIX_PATTERN = (
    r"(?:[A-Z_][A-Z0-9_]*=(?:'[^'\n]*'|\"[^\"\n]*\"|\S+)[ \t]+)*"
    r"(?:\$[ \t]+)?"
)
COMMAND_START_PATTERN = re.compile(
    r"^[ \t]*(?:(?:[-*+]|\d+[.)])[ \t]+)?`?"
    + COMMAND_PREFIX_PATTERN
    + COMMAND_NAME_PATTERN
    + r"(?=\s|$)",
    re.MULTILINE,
)
INLINE_COMMAND_PATTERN = re.compile(
    r"`"
    + COMMAND_PREFIX_PATTERN
    + COMMAND_NAME_PATTERN
    + r"(?=\s|$)[^`\n]*`",
    0,
)
FENCE_PATTERN = re.compile(
    r"^ {0,3}```(?P<info>[^\n]*)\n(?P<body>.*?)^ {0,3}```[ \t]*$",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)
README_ROUTE_PATTERN = re.compile(
    r"\b(?:read|open|review|start\s+with|use)\b.*\bREADME(?:\.md)?\b",
    re.IGNORECASE,
)
README_CONDITIONAL_MARKERS = (
    "when ",
    "if ",
    "only ",
    "where ",
    "as needed",
    "needed",
    "relevant",
    "selected",
    "known",
    "target",
    "named",
    "for ",
)
PROCEDURAL_HEADING_PATTERN = re.compile(
    r"^#{1,6}\s+(?:validation|verify|verification|checks?|testing|"
    r"procedure|smoke)(?:\s|$)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ValidationResult:
    issues: tuple[str, ...]
    warnings: tuple[str, ...]


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _has_agents_heading(text: str) -> bool:
    stripped = text.lstrip()
    return any(stripped.startswith(prefix) for prefix in HEADING_PREFIXES)


def _relative(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _is_ignored(path: Path, repo_root: Path) -> bool:
    try:
        parts = path.relative_to(repo_root).parts
    except ValueError:
        return False
    return any(part in IGNORED_DIRS for part in parts)


def _active_agent_paths(repo_root: Path) -> list[Path]:
    """Return the root and nested active route cards in a deterministic order."""

    paths = [repo_root / "AGENTS.md"]
    paths.extend(
        repo_root / relative
        for relative in sorted(discover_nested_agents(repo_root))
    )
    return [path for path in paths if path.is_file()]


def _unconditional_readme_inventory_issues(path: Path, text: str) -> list[str]:
    issues: list[str] = []
    lines = text.splitlines()
    for line_number, line in enumerate(lines, start=1):
        if "readme" not in line.lower() or not README_ROUTE_PATTERN.search(line):
            continue
        normalized = line.lower()
        if not any(marker in normalized for marker in README_CONDITIONAL_MARKERS):
            issues.append(
                f"{path}:{line_number}: unconditional README inventory"
            )

    inventory_headings = {
        "start here",
        "read before editing",
        "reading order",
        "route stack",
        "route inventory",
        "read before editing",
        "reading order",
        "required reading",
    }
    for index, line in enumerate(lines):
        match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if not match or match.group(1).lower() not in inventory_headings:
            continue
        end = index + 1
        while end < len(lines) and not lines[end].lstrip().startswith("#"):
            end += 1
        section = lines[index + 1 : end]
        if any("readme" in item.lower() for item in section) and not any(
            any(marker in item.lower() for marker in README_CONDITIONAL_MARKERS)
            for item in section
        ):
            issues.append(
                f"{path}:{index + 1}: unconditional README inventory section"
            )
    return issues


def _procedural_structure_issues(path: Path, text: str) -> list[str]:
    """Reject executable residue while keeping semantic prose unconstrained."""

    issues: list[str] = []
    for match in FENCE_PATTERN.finditer(text):
        info_text = match.group("info").strip()
        info = info_text.split(None, 1)[0].lower() if info_text else ""
        if info in RUNNABLE_FENCE_LANGS or COMMAND_START_PATTERN.search(
            match.group("body")
        ):
            line_number = text.count(chr(10), 0, match.start()) + 1
            issues.append(f"{path}:{line_number}: executable fenced block")
    lines = text.splitlines()
    for line_number, line in enumerate(lines, start=1):
        if SHELL_FENCE_PATTERN.match(line):
            issues.append(f"{path}:{line_number}: executable fenced block")
        if COMMAND_START_PATTERN.match(line):
            issues.append(f"{path}:{line_number}: runnable command line")
        if INLINE_COMMAND_PATTERN.search(line):
            issues.append(f"{path}:{line_number}: inline runnable command")

    for index, line in enumerate(lines):
        match = PROCEDURAL_HEADING_PATTERN.match(line)
        if not match:
            continue
        end = index + 1
        while end < len(lines) and not lines[end].lstrip().startswith("#"):
            end += 1
        if not any(item.strip() for item in lines[index + 1 : end]):
            title = line.lstrip("#").strip()
            issues.append(f"{path}:{index + 1}: empty procedural section {title!r}")

    for index, line in enumerate(lines):
        if not line.rstrip().endswith(":"):
            continue
        next_index = index + 1
        while next_index < len(lines) and not lines[next_index].strip():
            next_index += 1
        next_line = lines[next_index] if next_index < len(lines) else ""
        if (
            next_index == len(lines)
            or next_line.lstrip().startswith("#")
            or FENCE_OPEN_PATTERN.match(next_line)
        ):
            issues.append(
                f"{path}:{index + 1}: orphan colon lead-in before structure or EOF"
            )
    issues.extend(_unconditional_readme_inventory_issues(path, text))
    return issues


def validate_active_agent_structure(repo_root: Path) -> tuple[str, ...]:
    """Return narrow prompt-light structural violations for active cards."""

    issues: list[str] = []
    for path in _active_agent_paths(repo_root):
        relative = _relative(path, repo_root)
        issues.extend(
            _procedural_structure_issues(
                relative, path.read_text(encoding="utf-8")
            )
        )
    return tuple(issues)


def discover_nested_agents(repo_root: Path) -> set[str]:
    found: set[str] = set()
    for path in repo_root.rglob("AGENTS.md"):
        if _is_ignored(path, repo_root):
            continue
        rel = _relative(path, repo_root)
        if rel != "AGENTS.md":
            found.add(rel)
    return found


def discover_topology_agents(repo_root: Path) -> tuple[set[str], list[str]]:
    """Derive package, parts-root, legacy, and part-local cards from topology."""

    topology_path = repo_root / "mechanics" / "topology.json"
    try:
        topology = json.loads(topology_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return set(), ["mechanics/topology.json: missing while deriving AGENTS routes"]
    except json.JSONDecodeError as exc:
        return set(), [f"mechanics/topology.json: invalid JSON: {exc}"]
    packages = topology.get("active_packages") if isinstance(topology, dict) else None
    if not isinstance(packages, list):
        return set(), ["mechanics/topology.json: active_packages must be a list"]

    expected: set[str] = set()
    issues: list[str] = []
    for package in packages:
        if not isinstance(package, dict) or not isinstance(package.get("path"), str):
            issues.append("mechanics/topology.json: every active package must name a path")
            continue
        package_name = package["path"]
        package_root = repo_root / "mechanics" / package_name
        expected.update(
            {
                f"mechanics/{package_name}/AGENTS.md",
                f"mechanics/{package_name}/parts/AGENTS.md",
            }
        )
        if (package_root / "legacy").is_dir():
            expected.add(f"mechanics/{package_name}/legacy/AGENTS.md")
        parts = package.get("active_part_routes")
        if not isinstance(parts, list):
            issues.append(f"mechanics/{package_name}: active_part_routes must be a list")
            continue
        for part in parts:
            if not isinstance(part, dict) or not isinstance(part.get("path"), str):
                issues.append(f"mechanics/{package_name}: every active part must name a path")
                continue
            part_root = package_root / "parts" / part["path"]
            if not part_root.is_dir():
                continue
            for agents_path in part_root.rglob("AGENTS.md"):
                expected.add(agents_path.relative_to(repo_root).as_posix())
    return expected, issues


def validate(
    repo_root: Path = REPO_ROOT,
    *,
    strict_advisory: bool = False,
    fail_on_untracked: bool = False,
) -> ValidationResult:
    repo_root = repo_root.resolve()
    issues: list[str] = []
    warnings: list[str] = []

    root_agents = repo_root / "AGENTS.md"
    if not root_agents.is_file():
        issues.append("AGENTS.md: root guidance file is missing")
    else:
        root_text = root_agents.read_text(encoding="utf-8")
        if not _has_agents_heading(root_text):
            issues.append("AGENTS.md: missing AGENTS heading")

    issues.extend(validate_active_agent_structure(repo_root))

    for rel_path, snippets in REQUIRED_AGENTS_DOCS.items():
        path = repo_root / rel_path
        if not path.is_file():
            issues.append(f"{rel_path}: required nested AGENTS.md is missing")
            continue
        text = path.read_text(encoding="utf-8")
        if not _has_agents_heading(text):
            issues.append(f"{rel_path}: missing AGENTS heading")
        normalized = _normalize(text)
        for snippet in snippets:
            if _normalize(snippet) not in normalized:
                issues.append(f"{rel_path}: missing required snippet {snippet!r}")

    topology_agents, topology_issues = discover_topology_agents(repo_root)
    issues.extend(topology_issues)
    for rel_path in sorted(topology_agents):
        path = repo_root / rel_path
        if not path.is_file():
            issues.append(f"{rel_path}: topology-owned nested AGENTS.md is missing")
            continue
        if not _has_agents_heading(path.read_text(encoding="utf-8")):
            issues.append(f"{rel_path}: missing AGENTS heading")

    required = set(REQUIRED_AGENTS_DOCS) | topology_agents
    actual = discover_nested_agents(repo_root)
    untracked = sorted(actual - required)
    if untracked:
        message = "untracked nested AGENTS.md not yet in validator map: " + ", ".join(untracked)
        warnings.append(message)
        if fail_on_untracked:
            issues.append(message)

    for rel_dir in ADVISORY_AGENT_DIRS:
        dir_path = repo_root / rel_dir
        agent_path = f"{rel_dir.rstrip('/')}/AGENTS.md"
        if not dir_path.is_dir():
            continue
        if agent_path in required or agent_path in actual:
            continue
        warnings.append(f"{rel_dir}: high-risk directory has no local AGENTS.md yet")

    if strict_advisory:
        issues.extend(warnings)

    return ValidationResult(tuple(issues), tuple(warnings))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--strict-advisory", action="store_true")
    parser.add_argument("--fail-on-untracked", action="store_true")
    args = parser.parse_args(argv)

    result = validate(
        args.repo_root,
        strict_advisory=args.strict_advisory,
        fail_on_untracked=args.fail_on_untracked,
    )
    if result.issues:
        print(f"Nested AGENTS validation failed for {REPOSITORY_NAME}.")
        for issue in result.issues:
            print(f"- {issue}")
        return 1
    print(
        f"Nested AGENTS validation passed for {REPOSITORY_NAME}: "
        f"{len(set(REQUIRED_AGENTS_DOCS) | discover_topology_agents(args.repo_root.resolve())[0])} "
        "required nested document(s)."
    )
    for warning in result.warnings:
        print(f"[advisory] {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
