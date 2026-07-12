# Receipt ABI crossing validation

## Current focused checks

Run from the repository root:

```bash
python scripts/validate_receipt_abi.py
python -m pytest -q mechanics/boundary-bridge/parts/receipt-abi-crossing/tests
```

The checks cover canonical envelope structure, active registry parity, the
declared downstream mirror when available, root-facade alias parity,
JSON/JSONL loading, latest-event deduplication, and conservative supersedes
resolution.

The canonical public envelope and repo-wide build facade remain at root;
focused crossing behavior is owned here.
