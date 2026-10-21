# Supplemental local TD 1 experiment

This is a separate Windows experiment, not a replacement for the group results at the repository root. It contains 123 batch attempts and 100 final cells: 71 correct, 27 incorrect, one invalid SQL, and one rate-limited cell. References remain pending peer/instructor validation. All five batches were operated locally by one person; both OpenRouter batches used the same account. See reports/td1.md for limitations and AI assistance.

## Files

- td1/: references, original per-batch traces/state, combined results, comparison and model summary.
- reports/td1.md: review draft with unresolved contribution/validation details.
- kit-td1/: scripts, configuration, supplied database/CSV and dated metadata needed to reproduce this run.

No API keys, passwords, credentials, account screenshots or Python environments are included. Organization IDs in API error messages are redacted; numerical measurements and SQL are unchanged. The portable launcher uses a local .venv or python from PATH. The original launcher on the author's computer used an absolute interpreter path.

## Reproduce offline

From this directory, with Python 3.10 or later:

```text
python kit-td1/verify-data.py
python td1/build_references.py kit-td1
python td1/consolidate.py
python kit-td1/skeleton-multi-llm-en.py --replay td1/state-A.jsonl --reference td1/reference-td1.csv --state replay-A.jsonl --out replay-A.csv
```

Repeat the replay for B through E if needed. Replay rows are labelled replay and do not replace real-call evidence. Consolidation regenerates the report draft; preserve subsequent manual edits first. Historical metadata is not a live price verification. Member identities/contributions and instructor validation are not claimed.

Real runs require private process environment variables and remaining free account allowance. Do not rerun exhausted experiment cells or replace raw state files. The modified runner permits one explicit access-recovery attempt and stops on new access failures when requested.
