#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[0]

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from refresh_live_stats import (  # noqa: E402
    DEFAULT_FEDERATION_ROOT,
    DEFAULT_FEED_OUTPUT,
    DEFAULT_REGISTRY,
    DEFAULT_SUMMARY_OUTPUT_DIR,
    load_registry,
    refresh_live_state,
    resolve_source_path,
)


UNIT_NAMES = ("aoa-stats-live-refresh.service", "aoa-stats-live-refresh.path")
DEFAULT_USER_UNIT_DIR = Path.home() / ".config" / "systemd" / "user"
TEMPLATE_DIR = REPO_ROOT / "systemd"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install and optionally enable the aoa-stats live refresh user units."
    )
    parser.add_argument(
        "--registry",
        default=str(DEFAULT_REGISTRY),
        help="Path to the live receipt registry used to resolve watched sources.",
    )
    parser.add_argument(
        "--federation-root",
        default=str(DEFAULT_FEDERATION_ROOT),
        help="Federation root used to resolve repo-relative live receipt paths.",
    )
    parser.add_argument(
        "--user-unit-dir",
        default=str(DEFAULT_USER_UNIT_DIR),
        help="Target directory for user-level systemd units.",
    )
    parser.add_argument(
        "--feed-output",
        default=str(DEFAULT_FEED_OUTPUT),
        help="Live receipt feed output path passed to refresh_live_stats.py.",
    )
    parser.add_argument(
        "--summary-output-dir",
        default=str(DEFAULT_SUMMARY_OUTPUT_DIR),
        help="Live summary output directory passed to refresh_live_stats.py.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing unit files when their contents differ.",
    )
    parser.add_argument(
        "--enable",
        action="store_true",
        help="Enable and start the path unit after installation.",
    )
    parser.add_argument(
        "--start",
        action="store_true",
        help="Start the path unit after installation without enabling it.",
    )
    parser.add_argument(
        "--skip-touch-sources",
        action="store_true",
        help="Do not create the watched owner-local live receipt files during installation.",
    )
    return parser.parse_args(argv)


def systemd_arg(value: Path, *, escape_dollar: bool = False) -> str:
    text = str(value)
    escaped = (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("%", "%%")
    )
    if escape_dollar:
        escaped = escaped.replace("$", "$$")
    return f'"{escaped}"'


def systemd_exec_arg(value: Path) -> str:
    return systemd_arg(value, escape_dollar=True)


def render_template(unit_name: str, replacements: dict[str, str]) -> str:
    text = (TEMPLATE_DIR / unit_name).read_text(encoding="utf-8")
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


def build_service_unit(
    *,
    registry_path: Path,
    federation_root: Path,
    feed_output: Path,
    summary_output_dir: Path,
) -> str:
    return render_template(
        "aoa-stats-live-refresh.service",
        {
            "@AOA_STATS_REPO_ROOT@": systemd_arg(REPO_ROOT),
            "@AOA_STATS_REFRESH_SCRIPT@": systemd_exec_arg(
                REPO_ROOT / "scripts" / "refresh_live_stats.py"
            ),
            "@AOA_STATS_REGISTRY@": systemd_exec_arg(registry_path),
            "@AOA_FEDERATION_ROOT@": systemd_exec_arg(federation_root),
            "@AOA_STATS_FEED_OUTPUT@": systemd_exec_arg(feed_output),
            "@AOA_STATS_SUMMARY_OUTPUT_DIR@": systemd_exec_arg(summary_output_dir),
        },
    )


def watched_source_paths(*, registry_path: Path, federation_root: Path) -> list[Path]:
    registry = load_registry(registry_path)
    paths: list[Path] = []
    for source in registry["sources"]:
        if not isinstance(source, dict):
            raise ValueError(f"{registry_path}: each source must be an object")
        _, path = resolve_source_path(
            source, registry_path=registry_path, federation_root=federation_root
        )
        paths.append(path)
    return paths


def build_path_unit(*, watched_paths: list[Path]) -> str:
    return render_template(
        "aoa-stats-live-refresh.path",
        {
            "@AOA_STATS_PATH_MODIFIED@": "\n".join(
                f"PathModified={systemd_arg(path)}" for path in watched_paths
            ),
        },
    )


def render_units(
    *,
    registry_path: Path,
    federation_root: Path,
    feed_output: Path,
    summary_output_dir: Path,
) -> dict[str, str]:
    return {
        "aoa-stats-live-refresh.service": build_service_unit(
            registry_path=registry_path,
            federation_root=federation_root,
            feed_output=feed_output,
            summary_output_dir=summary_output_dir,
        ),
        "aoa-stats-live-refresh.path": build_path_unit(
            watched_paths=watched_source_paths(
                registry_path=registry_path,
                federation_root=federation_root,
            )
        ),
    }


def install_units(
    *,
    user_unit_dir: Path,
    overwrite: bool,
    registry_path: Path,
    federation_root: Path,
    feed_output: Path,
    summary_output_dir: Path,
) -> list[Path]:
    installed_paths: list[Path] = []
    user_unit_dir.mkdir(parents=True, exist_ok=True)
    rendered_units = render_units(
        registry_path=registry_path,
        federation_root=federation_root,
        feed_output=feed_output,
        summary_output_dir=summary_output_dir,
    )
    for unit_name in UNIT_NAMES:
        target_path = user_unit_dir / unit_name
        source_text = rendered_units[unit_name]
        if target_path.exists():
            target_text = target_path.read_text(encoding="utf-8")
            if target_text == source_text:
                installed_paths.append(target_path)
                continue
            if not overwrite:
                raise FileExistsError(
                    f"{target_path} already exists with different contents; rerun with --overwrite"
                )
        target_path.write_text(source_text, encoding="utf-8")
        installed_paths.append(target_path)
    return installed_paths


def ensure_live_sources(*, registry_path: Path, federation_root: Path) -> list[Path]:
    registry = load_registry(registry_path)
    touched: list[Path] = []
    for source in registry["sources"]:
        if not isinstance(source, dict):
            continue
        _, path = resolve_source_path(
            source, registry_path=registry_path, federation_root=federation_root
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)
        touched.append(path)
    return touched


def run_systemctl(*args: str) -> None:
    subprocess.run(["systemctl", "--user", *args], check=True)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    registry_path = Path(args.registry).expanduser().resolve()
    federation_root = Path(args.federation_root).expanduser().resolve()
    user_unit_dir = Path(args.user_unit_dir).expanduser().resolve()
    feed_output = Path(args.feed_output).expanduser().resolve()
    summary_output_dir = Path(args.summary_output_dir).expanduser().resolve()

    installed_paths = install_units(
        user_unit_dir=user_unit_dir,
        overwrite=args.overwrite,
        registry_path=registry_path,
        federation_root=federation_root,
        feed_output=feed_output,
        summary_output_dir=summary_output_dir,
    )
    touched_paths: list[Path] = []
    if not args.skip_touch_sources:
        touched_paths = ensure_live_sources(
            registry_path=registry_path, federation_root=federation_root
        )
    _, receipt_count = refresh_live_state(
        registry_path=registry_path,
        federation_root=federation_root,
        feed_output=feed_output,
        summary_output_dir=summary_output_dir,
    )

    run_systemctl("daemon-reload")
    if args.enable:
        run_systemctl("enable", "--now", "aoa-stats-live-refresh.path")
    elif args.start:
        run_systemctl("start", "aoa-stats-live-refresh.path")

    print(f"[ok] installed {len(installed_paths)} user units into {user_unit_dir}")
    for path in installed_paths:
        print(f"[unit] {path}")
    if touched_paths:
        print(f"[ok] ensured {len(touched_paths)} watched live receipt files exist")
        for path in touched_paths:
            print(f"[watch] {path}")
    if receipt_count == 0:
        print("[sync] live state cleared because watched receipt logs are still empty")
    else:
        print(f"[sync] live state refreshed from {receipt_count} receipts during install")
    if args.enable:
        print("[status] aoa-stats-live-refresh.path enabled and started")
    elif args.start:
        print("[status] aoa-stats-live-refresh.path started")
    else:
        print("[status] units installed; run systemctl --user enable --now aoa-stats-live-refresh.path when ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
