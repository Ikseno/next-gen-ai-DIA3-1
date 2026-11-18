# TD2 / pair-A — k-of-n vote (Alexandre, Maya)

<<<<<<< HEAD
Pair A's files: `skeleton-multi-llm-en.py` with `vote_k_sur_n` implemented and `atelier-vote.py` with a `--compare` mode (uploaded by Maya). `atelier-vote.py` loads the skeleton, and the skeleton imports `sandbox_sqlite.py`; `--compare` reads `questions-td1.json` (kit file). All four files must stay in this folder.
=======
The kit files provide the starting point. Pair A completed `vote_k_sur_n` in `skeleton-multi-llm-en.py`; it is no longer identical to the TD1 skeleton. `atelier-vote.py` loads `skeleton-multi-llm-en.py` (and the skeleton imports `sandbox_sqlite.py`) from this same folder.

Completed by Pair A: `Orchestrateur.vote_k_sur_n` in `skeleton-multi-llm-en.py` (contract in its docstring), then:
>>>>>>> ba2a02cb11374217facb5260388b33a9a541a7d2

```bash
cd TD2/pair-A
python3 atelier-vote.py                                                  # four synthetic examples, no network
python3 atelier-vote.py --traces ../../TD1/results/traces-td1.csv --case C02   # real traces of one question
python3 atelier-vote.py --traces ../../TD1/results/traces-td1.csv --compare --out vote-comparison.csv   # 2-of-3 vs 3-of-5, C01–C20
```

Without `--out`, `--compare` writes `vote-comparison.csv` next to the traces, i.e. inside `TD1/results/`: pass `--out` to keep TD 1 unchanged.

Expected deliverables (assignment, Step 1): the completed method, the outputs above, and the 2-of-3 vs 3-of-5 table for C01–C20 in [`../reports/td2.md`](../reports/td2.md) (section 2).
