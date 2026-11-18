# TD2 — Task A: k-of-n voting and comparison of two panels

**Subgroup:** DIA3-1  
**Method:** offline replay of TD1 traces; no new model calls  
**Scope:** cases C01–C20

## 1. Objective and fixed policy

The objective is to compare a strict-majority **2-of-3** quorum with a **3-of-5** quorum, using the same recorded answers and references from TD1. Both panels and their thresholds were fixed for the comparison; neither is adjusted after inspecting a case's answers.

- **2-of-3:** GPT-OSS 120B (Groq), Cohere North Mini Code (OpenRouter), Qwen 27B (Groq); threshold `k=2`.
- **3-of-5:** the preceding three models plus GPT-OSS 20B (Groq) and Dots 3 Note (OpenRouter); threshold `k=3`.

**Abstention / fallback policy:** if no value reaches the preset threshold, return an abstention with no value. Do not lower `k`, replace the panel retrospectively, or fabricate a value. Log the abstention and refer the case for independent verification or human review; no result is delivered automatically on abstention. Replaying the alternative panel in this TD is an *experimental comparison*, not a silent production fallback.

## 2. Voting procedure

The `Orchestrateur.vote_k_sur_n` function implements the contract in the course skeleton:

1. Let `n` be the number of panel members, including those whose calls failed. Reject `k` unless `n // 2 < k <= n` (`ValueError`).
2. Reject duplicate `(provider, model_requested)` model identities (`ValueError`): one model cannot cast two votes.
3. Count only available, executed, non-missing integer values. A real value of `0` can vote; a missing value cannot.
4. Return a consensus if one integer value receives at least `k` votes. Otherwise abstain, report the largest count, and return `value=None`.
5. The function never receives the reference value. The reference is used only **after** the vote to label the outcome correct or wrong.

For the 20-case offline comparison, a proposal is also excluded *before voting* if its trace has no recorded SQL, in line with the lecture's traceability requirement. The replay selects the last recorded attempt per `(provider, model, case)` and ignores unsuccessful attempts and non-integer outputs. Values are compared as integers in euro cents, excluding tax, as specified by the TD1 kit.

**Scope of validation:** SQL presence is checked automatically, but this does not on its own prove that the SQL computes the quantity actually requested. Format, meaning/SQL semantics, and correctness must still be considered in that order; a consensus is not independent proof of correctness.

## 3. Experimental results (20 questions)

| Panel | Correct consensus | Incorrect consensus | Abstention | Total |
|---|---:|---:|---:|---:|
| 2-of-3 | 16 | 1 | 3 | 20 |
| 3-of-5 | 17 | 0 | 3 | 20 |

The full per-case table with reference values, vote counts, agreeing model names, and a decision-change explanation is in **`TD2/reports/td2-task-A-comparison.csv`**.

### Four decisions that change

| Case | 2-of-3 outcome | 3-of-5 outcome | Explanation |
|---|---|---|---|
| **C08** | Correct consensus, **605580** cents | Abstention | Two votes were enough in the three-member panel; no value received the three votes required in the five-member panel. |
| **C09** | **Incorrect consensus, 0** cents | Abstention | Cohere and Qwen both returned **0**, whereas the independent reference is **487980** cents. This wrong two-vote agreement reaches `k=2` but not `k=3`. |
| **C15** | Abstention | Correct consensus, **168680** cents | The three-member panel had no two-vote agreement, whereas three of the five models agreed on **168680**. |
| **C17** | Abstention | Correct consensus, **258180** cents | The larger panel had three votes for **258180**, overcoming the abstention of the three-member panel. |

These are **four changes out of 20 cases**. In the remaining 16 cases, the accepted decision (including abstention) did not change.

## 4. Interpretation and limits

- **C09 is a demonstrated incorrect consensus:** a voting majority can agree on the same false number. The two model responses need not share identical SQL bugs to agree on the same wrong result. The associated SQL should be examined in the subgroup's Task B analysis.
- **A higher quorum is not monotonically more permissive.** In C08, raising the panel from three to five *and* the threshold from two to three turns a correct consensus into an abstention. In C15 and C17, the additional members allow a consensus that the smaller panel could not reach.
- **In this dataset only,** the 3-of-5 panel produced 17 correct consensuses, zero incorrect consensuses, and three abstentions, versus 16/1/3 for 2-of-3. This does **not** establish a general error rate or prove 3-of-5 will always outperform 2-of-3; the comparison covers only 20 questions, and model errors may be correlated.
- **A vote is not a delivery check.** An accepted answer still needs the required independent verification. In this lab, comparison with `reference-td1.csv` is an *evaluation step performed after voting*, not an input to voting and not an available production reference.
- The two panels share models. This comparison changes both panel composition and threshold as required by the assignment; it does not isolate the causal effect of changing only `k`.

## 5. Reproducibility and evidence

Run from the repository root:

```powershell
python TD2/pair-A/atelier-vote.py
python TD2/pair-A/td2_compare_votes.py
```

Inputs: `TD1/results/traces-td1.csv` and `TD1/reference-td1.csv`.  
Outputs: `reports/td2-vote-synthetic.jsonl`, `reports/td2-vote-real.jsonl`, and `reports/td2-task-A-comparison.csv`.

The synthetic cases and the recorded TD1 traces are clearly labelled as **simulation** and **real replay**, respectively. No live model calls were made during TD2. The results were checked against the offline test outputs and the course's voting contract.

## 6. Cross-review and hand-in checks

- [x] Confirmed model identifiers and trace paths against the final TD1 files.
- [x] Verified the comparison covers C01-C20 and changes only on C08, C09, C15 and C17.
- [x] Cross-checked C09's different faulty SQL clauses with Pair B's analysis.
- [x] Checked the official TD2 assignment's required technical artefacts.
- [x] Obtained documented cross-reviews from [Pair B](../reviews/review-A-by-B.md) and [Pair C](../reviews/review-A-by-C.md).
- [ ] Confirm the final Moodle submission and any remaining individual approvals required by the instructor.

These checks reflect the completed technical evidence and cross-review
documents; they do not assert approval by an absent individual.
