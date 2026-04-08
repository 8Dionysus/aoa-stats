#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[0]

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_views import build_all_views, load_receipts, resolve_active_receipts, stable_json  # noqa: E402


DEFAULT_REGISTRY = REPO_ROOT / "config" / "live_receipt_sources.json"
DEFAULT_FEDERATION_ROOT = REPO_ROOT.parent
DEFAULT_FEED_OUTPUT = REPO_ROOT / "state" / "live_receipts.min.json"
DEFAULT_SUMMARY_OUTPUT_DIR = REPO_ROOT / "state" / "generated"
SUMMARY_OUTPUT_NAMES = (
    "object_summary.min.json",
    "core_skill_application_summary.min.json",
    "repeated_window_summary.min.json",
    "route_progression_summary.min.json",
    "fork_calibration_summary.min.json",
    "automation_pipeline_summary.min.json",
    "runtime_closeout_summary.min.json",
    "stress_recovery_window_summary.min.json",
    "surface_detection_summary.min.json",
    "summary_surface_catalog.min.json",
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Refresh local aoa-stats state from owner-local receipt feeds."
    )
    parser.add_argument(
        "--registry",
        default=str(DEFAULT_REGISTRY),
        help="Path to the JSON registry that lists owner-local receipt sources.",
    )
    parser.add_argument(
        "--federation-root",
        default=str(DEFAULT_FEDERATION_ROOT),
        help="Federation root used to resolve repo-relative receipt source paths.",
    )
    parser.add_argument(
        "--feed-output",
        default=str(DEFAULT_FEED_OUTPUT),
        help="Where to write the combined live receipt feed JSON array.",
    )
    parser.add_argument(
        "--summary-output-dir",
        default=str(DEFAULT_SUMMARY_OUTPUT_DIR),
        help="Directory where live derived summaries should be written.",
    )
    return parser.parse_args(argv)


def load_registry(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: registry must be a JSON object")
    if payload.get("schema_version") != 1:
        raise ValueError(f"{path}: unsupported schema_version {payload.get('schema_version')!r}")
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError(f"{path}: sources must be a non-empty list")
    return payload


def resolve_source_path(
    source: dict,
    *,
    registry_path: Path,
    federation_root: Path,
) -> tuple[str, Path]:
    name = str(source.get("name") or "unnamed-source")
    repo = source.get("repo")
    relative_path = source.get("relative_path")
    direct_path = source.get("path")

    if isinstance(repo, str) and isinstance(relative_path, str):
        label = f"{repo}/{relative_path}"
        return label, (federation_root / repo / relative_path).resolve()

    if isinstance(direct_path, str):
        resolved = (registry_path.parent / direct_path).resolve()
        return direct_path, resolved

    raise ValueError(
        f"{registry_path}: source {name!r} must define either repo+relative_path or path"
    )


def write_receipt_feed(path: Path, receipts: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipts, indent=2) + "\n", encoding="utf-8")


def clear_live_state(*, feed_output: Path, summary_output_dir: Path) -> None:
    if feed_output.exists():
        feed_output.unlink()
    for name in SUMMARY_OUTPUT_NAMES:
        target = summary_output_dir / name
        if target.exists():
            target.unlink()


def refresh_live_state(
    *,
    registry_path: Path,
    federation_root: Path,
    feed_output: Path,
    summary_output_dir: Path,
) -> tuple[list[str], int]:
    registry = load_registry(registry_path)
    source_labels: list[str] = []
    source_paths: list[Path] = []

    for source in registry["sources"]:
        if not isinstance(source, dict):
            raise ValueError(f"{registry_path}: each source must be an object")
        label, path = resolve_source_path(
            source, registry_path=registry_path, federation_root=federation_root
        )
        required = source.get("required", True)
        if not isinstance(required, bool):
            raise ValueError(f"{registry_path}: source {source.get('name')!r} required must be boolean")
        if not path.exists():
            if required is False:
                continue
            raise FileNotFoundError(f"missing live receipt source: {path}")
        source_labels.append(label)
        source_paths.append(path)

    if not source_paths:
        raise ValueError("no live receipt sources were resolved from the configured registry")

    receipts = load_receipts(source_paths)
    active_receipts = resolve_active_receipts(receipts)
    if not active_receipts:
        clear_live_state(feed_output=feed_output, summary_output_dir=summary_output_dir)
        return source_labels, 0

    write_receipt_feed(feed_output, active_receipts)
    outputs = build_all_views(receipts, source_labels)
    summary_output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in outputs.items():
        (summary_output_dir / name).write_text(stable_json(payload), encoding="utf-8")
    return source_labels, len(active_receipts)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    registry_path = Path(args.registry).expanduser().resolve()
    federation_root = Path(args.federation_root).expanduser().resolve()
    feed_output = Path(args.feed_output).expanduser().resolve()
    summary_output_dir = Path(args.summary_output_dir).expanduser().resolve()

    source_labels, receipt_count = refresh_live_state(
        registry_path=registry_path,
        federation_root=federation_root,
        feed_output=feed_output,
        summary_output_dir=summary_output_dir,
    )
    if receipt_count == 0:
        print(f"[ok] cleared live stats because no receipts were found across {len(source_labels)} sources")
        print(f"[feed-cleared] {feed_output}")
        print(f"[summaries-cleared] {summary_output_dir}")
        return 0
    print(
        f"[ok] refreshed live stats from {len(source_labels)} sources and {receipt_count} receipts"
    )
    print(f"[feed] {feed_output}")
    print(f"[summaries] {summary_output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
