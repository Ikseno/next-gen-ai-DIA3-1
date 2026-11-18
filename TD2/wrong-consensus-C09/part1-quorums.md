# TD 2 — Pair B, part 1: identification and quorum verdict on C09

**Question C09:** revenue excluding VAT, in euro cents, of the customers who are exactly 25 years old on the reference date **2026-09-26** (all their orders).
**Reference:** **487 980** cents ([`TD1/reference-td1.csv`](../../TD1/reference-td1.csv), identical to the official TD 1 value).
**Source:** final attempt of each model in [`TD1/results/traces-td1.csv`](../../TD1/results/traces-td1.csv) — one attempt per model on C09, all HTTP 200, `nature = real`.

## The five answers

| Model | Provider | In the fixed panel? | Value (cents) | TD 1 verdict |
|---|---|---|---:|---|
| `openai/gpt-oss-120b` | Groq | yes | 487 980 | correct |
| `cohere/north-mini-code:free` | OpenRouter | yes | **0** | incorrect |
| `qwen/qwen3.8-27b` | Groq | yes | **0** | incorrect |
| `openai/gpt-oss-20b` | Groq | no | 487 980 | correct |
| `dots-studio/dots-3-note-preview:free` | OpenRouter | no | 369 240 | incorrect |

**Shared wrong value:** Cohere and Qwen both return **0**, two of the three members of the fixed panel. (Dots is wrong too, by 118 740 = the revenue of C007, born 2000-11-30, which its age test misses; it agrees with nobody.)

## Quorum verdicts (decided without looking at the reference)

Rules of the assignment: only executed proposals with a value vote; k is a strict majority; a value is kept only if it reaches k votes, otherwise the vote abstains.

| Quorum | Members (n) | k | Votes by value | Decision | Against the reference |
|---|---|---|---|---|---|
| **Fixed panel 2-of-3** | gpt-oss-120b, Cohere, Qwen | 2 | 0: **2** (Cohere, Qwen) · 487 980: 1 | **consensus on 0** | **wrong** — the two wrong answers outvote the correct one |
| **3-of-5** | the five models | 3 | 487 980: 2 · 0: 2 · 369 240: 1 | **abstention** (value `None`, highest count 2) | no wrong value retained |

**Families.** Cohere and Qwen come from two different makers and wrote two different queries (see part 2): as in Lecture 2's pilot case C11, distinct families lower the risk of a shared error but do not remove it.

**Reading.** C09 is a true wrong consensus: the fixed 2-of-3 panel *returns* the wrong value. Widening the panel to five models with k = 3 turns it into an abstention — safer, but no answer. Compare with C08 ([`../pair-b/`](../pair-b/)), where the shared wrong value (25 920, gpt-oss-20b and Dots) wins **neither** quorum because both wrong models are outside the fixed panel: whether a shared error wins depends on **who is in the panel**, not only on how many models agree.

Part 2 (SQL root cause): [`part2-sql-cause-marc.md`](part2-sql-cause-marc.md) · Part 3 (delta query and independent check): [`part3-delta-mehdy.md`](part3-delta-mehdy.md).

*Counts computed from the stored answers with the assignment's rules; to be re-checked with Pair A's `vote_k_sur_n` once it is in the repository.*
