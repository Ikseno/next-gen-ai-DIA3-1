# TD1 / state

JSONL state file of each operator's batch: `state-X.jsonl` (X = A to E), one line per attempt. It is what the skeleton reads to resume a batch without exceeding one retry per cell, and what `--replay` re-executes offline.

Concatenated version: [`../results/traces-td1.jsonl`](../results/traces-td1.jsonl).
