# TD 1 — Member E: AI-assistance prompts and disclosure

**Assigned model:** `openrouter:dots-studio/dots-3-note-preview:free`  
**Session:** 21 October 2026  
**Scope:** Personal use of AI assistants to prepare, understand and document TD 1. This file is **not** the prompt sent to Model E during the experiment.

## 1. Prompt used for the five-model experiment

The system message and user template sent to all five tested models are already documented verbatim in the subgroup file [`prompts-en.md`](./prompts-en.md). Model E used those same prompts without modifications. They were constructed by `build_prompt()` in `skeleton-multi-llm-en.py` using `schema.sql` and `questions-td1.json`; the `prompt_sha256` values are recorded in the traces.

## 2. Personal ChatGPT prompts (verbatim examples)

The following are actual messages I sent to ChatGPT during TD 1. Original wording is preserved.

### Understanding the model run and trace files

> Before doing 20 questions what are the files where are they how do I interpret this

### Investigating incorrect answers and drafting explanations

> Okay is that enough for you ? are you capable of seeing the wrong answers and make an explanation on all the incorrect ones (for the correct ones the explanation is just "The SQL Query is Correct") ?

### Checking results before submission

> so I put traces, is the format of my traces correct ? And then I put the model E comparison I don't think the others are quite important they're not asked for right

### Combining individual results into subgroup deliverables

> ok but in terms of what I need to give my subgroup and stuff what do I give here, I give the model E comparison csv you gave me, combine it with others to do the final model-question-comparion-en.csv right, or like what do I do now

### Understanding pricing sources and the five-model summary

> in five-model-summary it talks about pricing and stuff do we have access to this information ? Does model-question-comparison-en have this information or not ?

### Checking remaining assignment requirements

> ok so now we combine our model question comparions and what's next anything missing from what the TD is asking here

## 3. How AI assistance was used

- **Trace interpretation:** understanding the result, timing, verdict and structure of `traces-E.csv` and `state-E.jsonl`.
- **Failure analysis:** helping identify and explain the five non-correct Model E results (C08, C09, C10, C16, C18) by reviewing the generated SQL and reference values.
- **Documentation:** drafting `model-question-comparison-E.csv` explanations and helping interpret the subgroup's `traces-td1.csv`, `model-question-comparison-en.csv` and `five-model-summary-en.csv` deliverables.
- **Reference preparation:** AI assistance was also used while preparing/checking the reference calculations. The subgroup is responsible for independent checking; an assistant's result is not a reference by itself.

**Other AI tools used for reference preparation:** Codex and Claude, alongside ChatGPT. Their exact prompt wording is not included here because it has not been retrieved from their original conversations; it should be appended from those logs if the subgroup wants a complete verbatim record. Do not replace it with invented quotations.

## 4. Evidence and limitations

- Model E was queried through the provided skeleton and the OpenRouter API, not through ChatGPT. Its experimental inputs and outputs are captured in `traces-E.csv` and `state-E.jsonl`.
- The personal ChatGPT prompts above were **assistance prompts**, not additional model evaluations; they must not be counted among the 100 initial model-question tests.
- Proposed explanations and derived summary files should be checked against the original SQL, reference values and real traces before final submission.
- No API secrets or private keys are included in this document.
