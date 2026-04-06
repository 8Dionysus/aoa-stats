#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
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


def install_units(*, user_unit_dir: Path, overwrite: bool) -> list[Path]:
    installed_paths: list[Path] = []
    source_dir = REPO_ROOT / "systemd"
    user_unit_dir.mkdir(parents=True, exist_ok=True)
    for unit_name in UNIT_NAMES:
        source_path = source_dir / unit_name
        target_path = user_unit_dir / unit_name
        source_text = source_path.read_text(encoding="utf-8")
        if target_path.exists():
            target_text = target_path.read_text(encoding="utf-8")
            if target_text == source_text:
                installed_paths.append(target_path)
                continue
            if not overwrite:
                raise FileExistsError(
                    f"{target_path} already exists with different contents; rerun with --overwrite"
                )
        shutil.copyfile(source_path, target_path)
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

    installed_paths = install_units(user_unit_dir=user_unit_dir, overwrite=args.overwrite)
    touched_paths: list[Path] = []
    if not args.skip_touch_sources:
        touched_paths = ensure_live_sources(
            registry_path=registry_path, federation_root=federation_root
        )
    _, receipt_count = refresh_live_state(
        registry_path=registry_path,
        federation_root=federation_root,
        feed_output=DEFAULT_FEED_OUTPUT,
        summary_output_dir=DEFAULT_SUMMARY_OUTPUT_DIR,
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
