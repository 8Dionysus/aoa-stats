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

from build_views import build_all_views, load_receipts, stable_json  # noqa: E402


DEFAULT_REGISTRY = REPO_ROOT / "config" / "live_receipt_sources.example.json"
DEFAULT_FEDERATION_ROOT = REPO_ROOT.parent
DEFAULT_FEED_OUTPUT = REPO_ROOT / "state" / "live_receipts.min.json"
DEFAULT_SUMMARY_OUTPUT_DIR = REPO_ROOT / "state" / "generated"


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
        if not path.exists():
            raise FileNotFoundError(f"missing live receipt source: {path}")
        source_labels.append(label)
        source_paths.append(path)

    receipts = load_receipts(source_paths)
    if not receipts:
        raise ValueError("no receipts were loaded from the configured live sources")

    write_receipt_feed(feed_output, receipts)
    outputs = build_all_views(receipts, source_labels)
    summary_output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in outputs.items():
        (summary_output_dir / name).write_text(stable_json(payload), encoding="utf-8")
    return source_labels, len(receipts)


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
    print(
        f"[ok] refreshed live stats from {len(source_labels)} sources and {receipt_count} receipts"
    )
    print(f"[feed] {feed_output}")
    print(f"[summaries] {summary_output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
