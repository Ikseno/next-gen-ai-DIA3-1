# TD 1 — Model comparison 

member : Yasmine Boukrouh

## Method and evidence

Twenty reference queries were executed read-only on the supplied database and cross-checked by a separate CSV iteration. Both implementations share case definitions; an independent group member must still review their interpretation. See [references](../td1/reference-td1.csv), [cross-check](../td1/reference-crosscheck.json), and [notes].

Five models received the same prompt per question. All observed attempts have nature `real`; no simulation or replay is included. See the [prompt](../td1/prompt-used.md), [all raw attempts](../td1/traces-td1.csv), [100 final comparisons](../td1/model-question-comparison-en.csv), [five-model summary](../td1/five-model-summary-en-reviewed.csv) and [comparison view](../td1/comparison-view.md). Original CSV and JSONL logs for A–E are retained in td1.

## Results

| Batch | Model | Correct / planned |
|---|---|---|
| A | GPT-OSS 120B | 17/20 |
| B | GPT-OSS 20B | 17/20 |
| C | Cohere North Mini Code | 12/20 |
| D | Qwen 3.8 27B | 15/20 |
| E | Dots 3 Note Preview | 10/20 |

Final cells: {'correct': 71, 'incorrect': 27, 'not_executed': 1, 'sql_invalid': 1}. Of 100 planned cells, 99 received model output, 98 executed SQL successfully, and 71 matched the reference. Dots C08 had invalid SQL. Qwen C18 remained blocked by HTTP 429 on both allowed attempts. Access failures are separate from wrong numerical answers.

All five models answered the six pure-period and four product-family cases correctly (the product family includes cases combining products with periods, as classified in the supplied question JSON). Failures concentrate in age and combined questions: exact-birthday equality, wrong birth intervals, omitted completed-age cases, contradictory predicates, or unrequested order-date filters. The comparison CSV gives an evidence-based explanation for each final failure. This is a hypothesis about this batch, not a general ranking.

For example, A/C15 uses `c.birth_date = date('2026-09-25', '-25 years')`, selecting one birthday instead of all age-25 customers. E/C08 contains malformed CAST syntax. The original SQL remains unchanged in the raw traces.

## Access, attempts and missing measurements

There are 123 recorded batch attempts: 100 initial calls and 23 second attempts. HTTP status counts: {'403': 17, '200': 99, '401': 2, '429': 5}. A initially had 17 HTTP 403 failures and two HTTP 401 failures; C18 succeeded before the other cells were recovered. D recorded five HTTP 429 responses across four cells. All originals and retries remain in the same state files, with a maximum of two attempts per cell. Setup checks are additional calls and are not included in these batch totals; the full setup-call count and before/after account allowances were not recorded and must not be invented.

Missing token/cost measurements remain blank in raw logs. Free-route access does not establish a paid-route price. Model metadata in the summary comes only from the dated course portfolio: it is not a live price check. N/A entries mean the supplied snapshot does not document the exact model/paid route; they do not assert that no paid route exists.

## Assistance, contributions and protocol deviations


The supplied runner was modified to add explicit `--retry-access` for repaired access failures, preserving original traces and the two-attempt cap, and `--stop-on-access-error` to stop a batch after a new access failure. The launcher trims key input and reuses process environment variables. Prompts, output caps, temperature, sandbox and reference values were unchanged. The explicit recovery of previously terminal access failures is documented here; it is not an automatic retry of every HTTP 403.


