# TD 2 report — The quorum, then the routing rule

**Class DIA 3, sub-group 1 (DIA3-1)** · Session of 18 November 2026 · Course pack `2026-11-18-students-5`
Inputs: TD 1 outputs in [`TD1/`](../../TD1/) — no new network batch. Work files: [`TD2/`](../).

## 1. What we attempted and what we completed

_To complete._

## 2. Step 1 — k-of-n vote (Pair A)

_Method, 2-of-3 vs 3-of-5 table for C01–C20, explanation of each changed decision._

## 3. Step 2 — Wrong consensus (Pair B)

Pair B analyses **C08**, a real shared wrong answer in the team's stored TD1 traces. GPT-OSS 20B and Dots both return **25,920 cents**, whereas the independently checked reference is **605,580 cents**. Both faulty queries select only customers born on `2001-09-24`, rather than all customers aged 25 on `2026-09-24` (birth dates strictly after `2000-09-24` and on or before `2001-09-24`).

The executed delta query identifies five omitted customers whose revenue totals **579,660 cents**, exactly `605,580 - 25,920`. The fixed **2-of-3** panel returns the correct value with two votes; the **3-of-5** quorum abstains (two correct votes, two votes for 25,920, one for 1,188,090). The shared wrong value wins neither quorum.

Full diagnosis, complete SQL queries, customer-level evidence, source hashes and independent CSV checking: **[Pair B analysis](../pair-b/README.md)**. Reproduce offline with `python TD2/pair-b/analyse.py` from the repository root. SQLite execution and the independent Python/CSV calculation agree. **Pending:** verify the vote counts with Pair A's completed method and complete the internal team cross-review.

## 4. Step 3 — Routing rule (Pair C)

_One-page rule per family with TD 1 rates and cells, simulator outputs before/after adaptation, priority analysis of `choose`._

## 5. Limits, decisions and next steps

_To complete._

## 6. Who did what

| Pair | Members | Step |
|---|---|---|
| A | Alexandre, Maya | k-of-n vote |
| B | Yasmine Boukrouh, Marc, Mehdy | wrong consensus; C08 analysis and evidence prepared with AI assistance; team review pending |
| C | Dorian et Raphael | routing rule |
