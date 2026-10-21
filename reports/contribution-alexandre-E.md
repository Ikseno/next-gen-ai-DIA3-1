# TD 1 — Individual contribution: Alexandre Flavigny (role E)

**Sub-group:** DIA3-1  
**Session:** 21 October 2026  
**Assigned model:** `openrouter:dots-studio/dots-3-note-preview:free` (OpenRouter Free)  
**Reference questions assigned:** C07, C11 and C20, as recorded in the [group README](../README.md).

## 1. Preparation and reference work

I prepared my local TD 1 environment in VS Code on Windows, using the supplied `kit-td1`, a Python virtual environment and a personal OpenRouter account. I configured the API key through a PowerShell environment variable rather than adding it to the source code or repository. When opening a new terminal cleared that variable, I restored it and verified that it was available without printing the key.

During the reference stage, I was assigned **C07, C11 and C20**. I participated in preparing and checking the reference SQL and revenue values, paying particular attention to the assignment's conventions: revenue in euro cents excluding VAT, half-open date intervals, and completed age where applicable. I also reviewed the group's reference file before the model evaluation. The reference values were established independently of the outputs of the models being evaluated.

**Evidence:** [`reference-td1.csv`](../reference-td1.csv).

## 2. Running model E — Dots 3 Note Preview

I ran the supplied orchestrator against the real OpenRouter API. I first tested question C01 to verify the complete workflow: prompt construction, API call, SQL execution, reference comparison and trace export.

```powershell
python skeleton-multi-llm-en.py --run --models openrouter:dots-studio/dots-3-note-preview:free --cases C01 --state state-E.jsonl --out traces-E.csv
```

This first call returned **792,800 cents**, matching the reference for C01, with a reported latency of approximately **2,350 ms**. I then ran the remaining questions with the same state file:

```powershell
python skeleton-multi-llm-en.py --run --models openrouter:dots-studio/dots-3-note-preview:free --state state-E.jsonl --out traces-E.csv
```

Reusing the state file preserved C01 without making a duplicate request. The resulting batch contains **20 real API attempts covering C01–C20**, with **20 HTTP 200 responses**, **no retries**, and **no SQL-invalid or rejected responses**. I retained both the raw CSV trace and JSONL state file without replacing them with simulated results.

**Evidence:** [`trace/traces-E.csv`](../trace/traces-E.csv) and [`state/state-E.jsonl`](../state/state-E.jsonl).

## 3. Trace interpretation and failure analysis

My model obtained **15 correct answers out of 20 (75%)**. All six period-only and all four product-only questions were numerically correct; the age family scored 2/5 and the combined family 3/5.

I examined the SQL generated for each incorrect question, compared its filters and calculated revenue with the reference, and prepared an explanation for every model-question result. The five incorrect cases share a difficulty with the **completed-age convention**:

| Case | Cause identified from the generated SQL |
|---|---|
| **C08** | The query restricts customers to one birth date instead of the full interval corresponding to age 25 on the reference date. |
| **C09** | The age condition omits customers born late in 2000 who are still 25 on the reference date. |
| **C10** | Age at the time of each order is computed incompletely: customers whose year difference is 26 but whose birthday has not yet occurred are excluded. |
| **C16** | The birth-date bounds are wrong, including younger customers while excluding eligible 25-year-olds. |
| **C18** | The same age-at-order mistake as C10 excludes valid order lines. |

I also noted a **limitation on C19**: its numerical value agrees with the reference, but its age predicate is incomplete. This illustrates why a `correct` numerical verdict does not necessarily establish that the SQL is generally correct.

The resulting 20 question-level explanations are available in [`explanation/explanations-E.csv`](../explanation/explanations-E.csv). The group incorporated the Model E results into [`results/model-question-comparison-en.csv`](../results/model-question-comparison-en.csv).

## 4. Verification and contribution to group documentation

I performed **both manual and AI-assisted verification**. I personally reviewed the generated SQL, date and age conditions, reference values, recorded trace fields and failure explanations. AI assistance helped me cross-check the analyses, identify possible logical errors and draft clear explanations; I reviewed the resulting material myself before sharing it. The actual Model E evaluations were real API calls made by the course script, not responses simulated by a separate assistant.

I provided my trace, state and explanation files for the subgroup's consolidation. I also reviewed how my Model E outcomes appeared in the final comparison and five-model summary, and inspected the common system and user prompts in `skeleton-multi-llm-en.py`. The group's experimental prompts are documented in [`prompt/prompts-en.md`](../prompt/prompts-en.md); my AI-assistance disclosure is in [`prompt/ai-assistance/ai-prompts-alexandre-E.md`](../prompt/ai-assistance/ai-prompts-alexandre-E.md).

The merging of all five models' files and preparation of the subgroup-wide summary were collaborative tasks handled by other assigned members; I do not claim to have run their models or authored their analyses.

## 5. Lessons learned and next steps

This experiment showed that generating executable SQL and generating **semantically correct** SQL are different tasks. Dots handled the simpler period and product filters successfully but was less reliable for completed-age predicates, especially when the age must be evaluated on each order date. The C19 case also shows why checking SQL logic matters even when the final amount matches the reference.

For TD 2, **C08 and C10** are useful cases to study: another model produced the same incorrect amount as Dots on each, making them relevant examples of potential **wrong consensus** in a k-of-n vote. The result of one run on 20 questions should not be treated as a general measure of model quality.
