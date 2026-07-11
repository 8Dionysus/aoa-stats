# Receipt ABI crossing validation

## Current focused checks

Run from the repository root:

```bash
python scripts/validate_receipt_abi.py
python -m pytest -q mechanics/boundary-bridge/parts/receipt-abi-crossing/tests/test_receipt_abi_governance.py
```

The command checks canonical envelope structure, active registry parity, and
the declared downstream mirror when its sibling repository is available.

The canonical public envelope remains at root; the focused governance test is
owned here with the crossing operation.
