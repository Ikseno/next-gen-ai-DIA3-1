# TD 2 — The quorum, then the routing rule

Session of 18 November 2026, pack `2026-11-18-students-5`. Inputs: the TD 1 outputs in [`../TD1/`](../TD1/) (no new network batch). Report: [`reports/td2.md`](reports/td2.md).

| Pair | Step | Expected files in this folder |
|---|---|---|
| A | k-of-n vote | `skeleton-multi-llm-en.py` with `vote_k_sur_n` completed, `atelier-vote.py` outputs, 2-of-3 vs 3-of-5 table for C01–C20 |
| B | Wrong consensus | the case (ID, models, shared wrong value, reference, quorum results), both faulty SQL queries, the delta query and its output |
| C | Routing rule | one-page rule per family, `atelier-routage.py` outputs before and after adaptation, priority analysis of `choose` |

## Folders

| Folder | Content |
|---|---|
| [`pair-A/`](pair-A/) | Pair A — k-of-n vote: `atelier-vote.py`, `skeleton-multi-llm-en.py` (`vote_k_sur_n` completed) |
| [`pair-b/`](pair-b/) | Pair B — wrong consensus: C08 at the root of the folder (Yasmine), C09 in [`pair-b/C09/`](pair-b/C09/) (Marc, Mohamed) |
| [`pair-C/`](pair-C/) | Pair C — routing rule and simulator |
| [`reviews/`](reviews/) | Cross-review: each pair reviewed by the two others (6 reviews) |
| [`reports/`](reports/) | TD 2 report [`td2.md`](reports/td2.md) |

Pair A is complete: the implementation and comparison scripts are in `pair-A/`, with results in `reports/td2.md` (Section 2) and supporting evidence in `reports/`.
