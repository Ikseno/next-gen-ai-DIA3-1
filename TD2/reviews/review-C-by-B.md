# Review of Pair C by Pair B

**Reviewers (at least two):** _Pair B members who validate this review — to sign: Yasmine Boukrouh, Marc Chen, Mehdy (Mohamed Diawara)_
**Reviewed:** Pair C (Dorian Courcelle, Raphaël Delavictoire) — routing rule: [`../pair-C/`](../pair-C/), section 4 of [`../reports/td2.md`](../reports/td2.md)
**Date:** 18 November 2026
_Draft prepared with AI assistance (Claude); every check below was re-run on the repository and must be confirmed by the reviewers before signing._

## Files reviewed

[`routing-rule-C.md`](../pair-C/routing-rule-C.md), [`atelier-routage.py`](../pair-C/atelier-routage.py), [`atelier-routage-adapted.py`](../pair-C/atelier-routage-adapted.py), [`output-before.jsonl`](../pair-C/output-before.jsonl), [`output-after.jsonl`](../pair-C/output-after.jsonl), [`pair-C/README.md`](../pair-C/README.md), section 4 of `td2.md`.

## What we re-ran and the result

| Check | Command / source | Result |
|---|---|---|
| Simulator before adaptation | `python3 TD2/pair-C/atelier-routage.py` | Same 7 decisions as `output-before.jsonl` ✅ |
| Simulator after adaptation | `python3 TD2/pair-C/atelier-routage-adapted.py` | Same 9 decisions as `output-after.jsonl` ✅ |
| Rates by family (table 4.1) | final attempt per cell in `TD1/results/model-question-comparison-en.csv` | All 30 rates match (e.g. F2: north 0/4, dots 2/4, gpt-oss-20b 1/4, gpt-oss-120b 4/4, qwen 3/4; F2b C10: only gpt-oss-20b and gpt-oss-120b correct) ✅ |
| Paid cost of the "urgent" scenario | 650 × 0.15 / 10⁶ + 300 × 0.60 / 10⁶ | 0.0002775 USD, shown as 0.000278 ✅ |
| Shared wrong values cited (C08, C09, C10) | `TD1/results/model-question-comparison-en.csv` | 25,920 / 0 / 119,410, agreeing models correct ✅ |

## What is correct

- The **consistency constraint** of the assignment is respected: a single free model with no check is used only for an internal dashboard and only when that model was 100 % on the family (F1/F3 any model 10/10; F2 gpt-oss-120b 4/4 + 4/4 combined). For F2b (one case), "none" is refused and a quorum is required.
- Every model choice cites TD 1 cells, and every `reason` in the adapted simulator names them (traceable decisions).
- The priority analysis of `choose` reads the branches correctly (included capacity `cash == 0` is listed before resources to wait for) and gives a concrete reversal condition (scarce subscription allocation still needed by level-3 requests, or overage charges).
- The rule draws the right conclusion from the C09 wrong consensus: no quorum alone for customer or payout figures on age questions.
- It follows Lecture 2's principle **"difficulty chooses the model, stakes choose the check"**: the family sets the first model, the use (dashboard / customer / payout) sets the check, and the two are not mixed.
- It applies **"filter, then the cheapest good enough"** (rule C of the lecture) and never silently falls back to a weaker model for F2: when nothing eligible is available it waits for the refill or abstains.

## Issues found

| # | File / cell | Issue | Severity | Suggested fix |
|---|---|---|---|---|
| 1 | `routing-rule-C.md`, first line | Links to `../TD1/results/...` are broken since the move to one folder per TD (they resolve to `TD2/TD1/`). | low | Replace `../TD1/` by `../../TD1/`. |
| 2 | Rule, F2b row | First model gpt-oss-20b rests on **one** cell (C10), and gpt-oss-20b is only 1/4 on F2 (C02, C08, C11 wrong). A question misclassified as F2b instead of F2 would go to a weak model. | medium | Say how a question is classified (age "on a date" vs "at the order") and route to gpt-oss-120b (1/1 on F2b, 4/4 on F2) when the classification is uncertain. |
| 3 | Rule, F2 "customer" and "payout" columns | "Deterministic reference" computes the answer without any model. The role of the model is then unclear: is its value compared with the reference (and what happens on disagreement), or is the model skipped? | medium | State: model value compared with the deterministic value; disagreement → abstain (customer) or human review (payout). |
| 4 | Table 4.1, north-mini-code combined 2/4 | One of the two correct cells (C19) is correct **by chance** (wrong age rule: keeps C003 aged 24, drops C005 aged 25). Counting it as evidence overstates north on age. | low | Already flagged "(C19 by chance)"; also exclude it when choosing a first model (north is never chosen for F2, so the rule itself is unaffected). |
| 6 | Rule, F1/F3 "figure shown to a customer" | Lecture 2's case *low difficulty / high stakes* uses **5 models, quorum 3 of 5 and a deterministic check**; the rule uses a 2-of-3 quorum without a deterministic check. Our C09 case shows a 2-of-3 panel can adopt a shared wrong value. | medium | Either align on the lecture (3-of-5 + deterministic period/product template), or justify 2-of-3 by the 10/10 rate of every model on F1/F3. |
| 7 | Rule, F2b "dashboard" quorum | The quorum is gpt-oss-20b + gpt-oss-120b + qwen: **two models of the same family** (OpenAI gpt-oss). Lecture 2: a panel should mix families, since models of one family share mistakes. | medium | Replace one gpt-oss model by a model of another family, or state the risk. |
| 8 | Simulator, `checks` field | Lecture 2's incident: "a check in error means no delivery" and "the check belongs to the request, not to the route". The adapted `choose` returns a `checks` text but nothing shows what happens if that check fails. | low | Add one line in the rule: a failed or erroring check → abstain (customer) or human review (payout), whatever the route used. |
| 5 | Rates | Qwen's C16–C20 are final values obtained **after an HTTP 429 retry**; the rate counts them like first attempts. | low | Add one line: the rate is on the final attempt; 5 of Qwen's cells needed a retry, which matters for the F2 fallback that relies on waiting for the Groq refill. |

## Questions to the authors

1. In the "product, customer, OpenRouter down" scenario, why is qwen (most expensive paid price) preferred over gpt-oss-20b for the run? Is it because the Groq free tier is used, so price does not apply?
2. For F1/F3 payout, the deterministic period/product template replaces the model entirely: should the rule still call a model at all for these families when the use is a payout?
3. How would the rule handle a question that combines age **at the order** with a product list (F2b + F3), not seen in TD 1?
4. Lecture 2 recommends a **shadow test** before using a new model: how would a sixth model enter the rule?

## Authors' answer

_To complete by Pair C._
