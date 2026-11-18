# TD2 / pair-A — k-of-n vote (Alexandre, Maya)

Pair A's files: `skeleton-multi-llm-en.py` with `vote_k_sur_n` implemented and `atelier-vote.py` with a `--compare` mode (uploaded by Maya). `atelier-vote.py` loads the skeleton, and the skeleton imports `sandbox_sqlite.py`; `--compare` reads `questions-td1.json` (kit file). All four files must stay in this folder.

```bash
cd TD2/pair-A
python3 atelier-vote.py                                                  # four synthetic examples, no network
python3 atelier-vote.py --traces ../../TD1/results/traces-td1.csv --case C02   # real traces of one question
python3 atelier-vote.py --traces ../../TD1/results/traces-td1.csv --compare --out vote-comparison.csv   # 2-of-3 vs 3-of-5, C01–C20
```

Without `--out`, `--compare` writes `vote-comparison.csv` next to the traces, i.e. inside `TD1/results/`: pass `--out` to keep TD 1 unchanged.

Expected deliverables (assignment, Step 1): the completed method, the outputs above, and the 2-of-3 vs 3-of-5 table for C01–C20 in [`../reports/td2.md`](../reports/td2.md) (section 2).
