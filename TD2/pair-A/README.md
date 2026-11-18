# TD2 / pair-A — k-of-n vote (Alexandre, Maya)

Kit files copied unchanged from `kit-td1` (pack of 14 October; `skeleton-multi-llm-en.py` is byte-identical to [`../../TD1/skeleton-multi-llm-en.py`](../../TD1/skeleton-multi-llm-en.py)). `atelier-vote.py` loads `skeleton-multi-llm-en.py` (and the skeleton imports `sandbox_sqlite.py`) from this same folder.

To complete by Pair A: `Orchestrateur.vote_k_sur_n` in `skeleton-multi-llm-en.py` (contract in its docstring), then:

```bash
cd TD2/pair-A
python3 atelier-vote.py                                                  # four synthetic examples, no network
python3 atelier-vote.py --traces ../../TD1/results/traces-td1.csv --case C02   # real traces of one question
```

Expected deliverables (assignment, Step 1): the completed method, the outputs above, and the 2-of-3 vs 3-of-5 table for C01–C20 in [`../reports/td2.md`](../reports/td2.md) (section 2).
