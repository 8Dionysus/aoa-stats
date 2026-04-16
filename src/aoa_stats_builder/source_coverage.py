from __future__ import annotations

from collections import Counter
from typing import Any


def _coverage_class(receipt_count: int) -> str:
    if receipt_count >= 5:
        return "rich"
    if receipt_count >= 2:
        return "active"
    return "sparse"


def _share(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(count / total, 4)


def _expected_owner_repos(source_registry: dict[str, Any] | None) -> list[str]:
    if not isinstance(source_registry, dict):
        return []
    raw_sources = source_registry.get("sources")
    if not isinstance(raw_sources, list):
        return []
    repos = {
        source.get("repo")
        for source in raw_sources
        if isinstance(source, dict) and isinstance(source.get("repo"), str) and source.get("repo")
    }
    return sorted(repos)


def build_source_coverage_summary(
    receipts: list[dict[str, Any]],
    source: dict[str, Any],
    *,
    source_registry: dict[str, Any] | None = None,
    source_registry_ref: str | None = None,
) -> dict[str, Any]:
    owner_repo_counts: Counter[str] = Counter()
    event_kind_counts: Counter[str] = Counter()
    owner_event_kind_counts: dict[str, Counter[str]] = {}
    owner_first_seen: dict[str, str] = {}
    owner_last_seen: dict[str, str] = {}

    for receipt in receipts:
        object_ref = receipt.get("object_ref", {})
        if not isinstance(object_ref, dict):
            continue
        owner_repo = object_ref.get("repo")
        if not isinstance(owner_repo, str) or not owner_repo:
            continue
        owner_repo_counts[owner_repo] += 1
        event_kind = receipt.get("event_kind")
        if isinstance(event_kind, str) and event_kind:
            event_kind_counts[event_kind] += 1
            owner_event_kind_counts.setdefault(owner_repo, Counter())[event_kind] += 1
        observed_at = receipt["observed_at"]
        if owner_repo not in owner_first_seen or observed_at < owner_first_seen[owner_repo]:
            owner_first_seen[owner_repo] = observed_at
        if owner_repo not in owner_last_seen or observed_at > owner_last_seen[owner_repo]:
            owner_last_seen[owner_repo] = observed_at

    total_receipts = len(receipts)
    expected_owner_repos = _expected_owner_repos(source_registry)
    observed_owner_repos = sorted(owner_repo_counts)
    missing_owner_repos = sorted(set(expected_owner_repos) - set(observed_owner_repos))
    unexpected_owner_repos = sorted(set(observed_owner_repos) - set(expected_owner_repos))

    owners = [
        {
            "owner_repo": owner_repo,
            "receipt_count": owner_repo_counts[owner_repo],
            "share_of_total_receipts": _share(owner_repo_counts[owner_repo], total_receipts),
            "coverage_class": _coverage_class(owner_repo_counts[owner_repo]),
            "event_kind_counts": dict(sorted(owner_event_kind_counts.get(owner_repo, {}).items())),
            "first_observed_at": owner_first_seen[owner_repo],
            "last_observed_at": owner_last_seen[owner_repo],
        }
        for owner_repo in observed_owner_repos
    ]

    thin_signal_flags: list[str] = []
    if source_registry is None:
        thin_signal_flags.append("registry_not_provided")
    if missing_owner_repos:
        thin_signal_flags.append("missing_owner_repos")
    if unexpected_owner_repos:
        thin_signal_flags.append("unexpected_owner_repos")
    if len(observed_owner_repos) <= 1:
        thin_signal_flags.append("owner_diversity_low")
    if owner_repo_counts and max(owner_repo_counts.values()) / total_receipts >= 0.7:
        thin_signal_flags.append("owner_share_dominant")
    if event_kind_counts and max(event_kind_counts.values()) / total_receipts >= 0.7:
        thin_signal_flags.append("event_kind_dominant")

    source_mode = (
        "registry_backed_receipt_feed"
        if isinstance(source_registry, dict) and isinstance(source_registry.get("sources"), list)
        else "receipt_feed_only"
    )

    return {
        "schema_version": "aoa_stats_source_coverage_summary_v1",
        "generated_from": source,
        "source_mode": source_mode,
        "input_registry_ref": source_registry_ref,
        "expected_owner_repos": expected_owner_repos,
        "missing_owner_repos": missing_owner_repos,
        "unexpected_owner_repos": unexpected_owner_repos,
        "active_receipt_total": total_receipts,
        "observed_owner_repo_count": len(observed_owner_repos),
        "expected_owner_repo_count": len(expected_owner_repos),
        "owner_repo_counts": dict(sorted(owner_repo_counts.items())),
        "event_kind_counts": dict(sorted(event_kind_counts.items())),
        "owners": owners,
        "thin_signal_flags": thin_signal_flags,
    }
