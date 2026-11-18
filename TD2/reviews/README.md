# TD2 / reviews — cross-review between pairs

Each pair's work is reviewed by the two other pairs, with **at least two reviewers per review**, who read the code, re-run it and check the figures against the TD 1 traces:

| Reviewed pair → | A (vote) | B (wrong consensus) | C (routing rule) |
|---|---|---|---|
| reviewed by A | — | [`review-B-by-A.md`](review-B-by-A.md) | [`review-C-by-A.md`](review-C-by-A.md) |
| reviewed by B | [`review-A-by-B.md`](review-A-by-B.md) | — | [`review-C-by-B.md`](review-C-by-B.md) |
| reviewed by C | [`review-A-by-C.md`](review-A-by-C.md) | [`review-B-by-C.md`](review-B-by-C.md) | — |

Pairs: **A** Alexandre, Maya (`vote_k_sur_n`, 2-of-3 vs 3-of-5) · **B** Yasmine, Marc, Mohamed (wrong consensus C08 and C09) · **C** Dorian, Raphaël (routing rule, simulator).

Each review states: reviewers, files reviewed, what was re-run and its result, what is correct, issues found (with file and line or cell), questions to the authors, and the authors' answer.
