#!/usr/bin/env python3
"""TD 2, Pair C: the routing simulator adapted to the DIA3-1 routing rule.

Same priority order as the kit's atelier-routage.py (included capacity, then
defer, then paid route, then abstain). What changes:

- RESOURCES are our five TD 1 portfolio models, on the route actually used in
  TD 1 (free tiers) plus the documented Groq Developer paid route.
- Eligibility levels come from the TD 1 table (TD1/results/pivot-td1.md):
    level 1 = F1 period and F3 product (C01 C03 C04 C05 C06 C07 C12 C13 C14 C20)
    level 2 = F2b age at the order (C10, and C18 when combined with a period)
    level 3 = F2 completed age at a date (C02 C08 C09 C11, and C15 C16 C17 C19)
  A model gets the highest level whose cells it got all right in TD 1.
- The check level comes from the rule (family x use), not from a single
  high_impact flag. See routing-rule-C.md.

Synthetic simulation: no API call, no key. Cash is USD per request for a fixed
envelope of 650 input + 300 output tokens at the Groq Developer prices of
2026-10-05 (five-model-summary-en.csv). Availability is a scenario input, not
a measurement. Twenty questions give a batch hypothesis, not a guarantee.
"""
import argparse
import json

ENVELOPE_IN, ENVELOPE_OUT = 650, 300


def per_request(usd_in_per_m, usd_out_per_m):
    return round((ENVELOPE_IN * usd_in_per_m + ENVELOPE_OUT * usd_out_per_m) / 1e6, 6)


FAMILY_LEVEL = {"F1": 1, "F3": 1, "F1+F3": 1, "F2b": 2, "F2b+F1": 2,
                "F2": 3, "F2+F1": 3, "F2+F3": 3, "F2+F1+F3": 3}

RESOURCES = [
    # OpenRouter free endpoints: no paid route for these exact models.
    {"id": "dots-3-note-free", "level": 1, "access": "free", "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None,
     "evidence": "E: F1 6/6 (C01 C04-C07 C20), F3 4/4 (C03 C12-C14); F2 2/4 (C08 C09 wrong), F2b 0/1 (C10)"},
    {"id": "north-mini-code-free", "level": 1, "access": "free", "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None,
     "evidence": "C: F1 6/6, F3 4/4; F2 0/4 (C11 invalid SQL), F2b 0/1, C19 correct by chance"},
    # Groq free tier (route used in TD 1).
    {"id": "gpt-oss-20b-groq-free", "level": 2, "access": "free", "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None,
     "evidence": "B: F1 6/6, F3 4/4, F2b 1/1 (C10) and C18 correct; F2 1/4 (C02 C08 C11 wrong)"},
    {"id": "gpt-oss-120b-groq-free", "level": 3, "access": "free", "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None,
     "evidence": "A: 20/20, F2 4/4 (C02 C08 C09 C11), combined 5/5 (C15-C19), F2b 1/1 (C10)"},
    {"id": "qwen3.8-27b-groq-free", "level": 1, "access": "free", "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None,
     "evidence": "D: F1 6/6, F3 4/4; F2 3/4 (C09 wrong), F2b 0/1 (C10 wrong)"},
    # Groq Developer paid route, same models (prices 2026-10-05).
    {"id": "gpt-oss-20b-groq-dev", "level": 2, "access": "tokens", "available": True,
     "cash": per_request(0.075, 0.30), "allocation": per_request(0.075, 0.30), "reset_minutes": None,
     "evidence": "B, same model as gpt-oss-20b-groq-free"},
    {"id": "gpt-oss-120b-groq-dev", "level": 3, "access": "tokens", "available": True,
     "cash": per_request(0.15, 0.60), "allocation": per_request(0.15, 0.60), "reset_minutes": None,
     "evidence": "A, same model as gpt-oss-120b-groq-free"},
    {"id": "qwen3.8-27b-groq-dev", "level": 1, "access": "tokens", "available": True,
     "cash": per_request(0.80, 4.00), "allocation": per_request(0.80, 4.00), "reset_minutes": None,
     "evidence": "D, same model as qwen3.8-27b-groq-free"},
]

QUORUM_F1_F3 = ("2-of-3 quorum of the three cheapest available models among dots-3-note, north-mini-code, "
                "qwen3.8-27b (Groq free), gpt-oss-20b (all 10/10 on C01 C03-C07 C12-C14 C20)")
QUORUM_F2B = "2-of-3 quorum gpt-oss-20b + gpt-oss-120b + qwen3.8-27b (C10: 2 of 3 right; C18: 3 of 3 right)"
REF_PERIOD = "deterministic reference (closed-open period / product IN template)"
REF_AGE = ("deterministic reference (age window date(birth,'+25 years') <= ref < date(birth,'+26 years'); "
           "no quorum: shared wrong values on C08, C09, C10)")

CHECKS = {
    1: {"dashboard": "none (every model 100% on F1/F3 in TD 1)",
        "customer": QUORUM_F1_F3,
        "payout": REF_PERIOD},
    2: {"dashboard": QUORUM_F2B + "; 'none' refused, one F2b case only",
        "customer": REF_AGE.replace("ref <", "order_date <").replace("<= ref", "<= order_date"),
        "payout": REF_AGE.replace("ref <", "order_date <").replace("<= ref", "<= order_date")
                  + " + human review"},
    3: {"dashboard": "none (gpt-oss-120b 4/4 on F2 in TD 1), value logged as unchecked",
        "customer": REF_AGE,
        "payout": REF_AGE + " + human review"},
}


def choose(request, resources):
    """Same priority order as the kit: included capacity, defer, paid, abstain."""
    level = FAMILY_LEVEL.get(request["family"])
    if level is None:
        return {"action": "abstain", "resource": None, "cash": 0, "checks": "human review",
                "reason": f"family {request['family']!r} not covered by TD 1 C01-C20: no eligibility evidence"}
    checks = CHECKS[level][request["use"]]
    eligible = [r for r in resources if r["level"] >= level]
    included = [r for r in eligible if r["available"] and r["cash"] == 0]
    if included:
        chosen = min(included, key=lambda r: (r["allocation"], r["level"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": f"cheapest eligible included capacity for level {level}; TD 1: {chosen['evidence']}"}
    waiting = [r for r in eligible if not r["available"] and r["cash"] == 0
               and r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: r["reset_minutes"])
        return {"action": "defer", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": ("free quota exhausted, refill before deadline; recheck availability at wake-up "
                           f"(TD 1: all six HTTP 429 recovered on attempt 2); TD 1: {chosen['evidence']}"),
                "wake_in_minutes": chosen["reset_minutes"]}
    paid = [r for r in eligible if r["available"] and r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=lambda r: (r["cash"], r["allocation"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": chosen["cash"], "checks": checks,
                "reason": f"paid route within the authorised budget; TD 1: {chosen['evidence']}"}
    return {"action": "abstain", "resource": None, "cash": 0, "checks": checks,
            "reason": f"no level-{level} resource within deadline and budget"}


def scenarios():
    base = {"family": "F1", "use": "dashboard", "can_wait": True,
            "deadline_minutes": 120, "budget": 0.30}
    groq_free_exhausted = [dict(r, available=False, reset_minutes=60)
                           if r["id"].endswith("groq-free") else dict(r) for r in RESOURCES]
    openrouter_down = [dict(r, available=False) if r["id"].endswith("-free") and "groq" not in r["id"]
                       else dict(r) for r in RESOURCES]
    return [
        # The kit's seven scenarios, mapped onto our families.
        ("simple", base, RESOURCES),
        ("complex", {**base, "family": "F2"}, RESOURCES),
        ("deferrable", {**base, "family": "F2"}, groq_free_exhausted),
        ("urgent", {**base, "family": "F2", "can_wait": False, "deadline_minutes": 5}, groq_free_exhausted),
        ("budget exhausted", {**base, "family": "F2", "can_wait": False, "budget": 0}, groq_free_exhausted),
        ("high impact", {**base, "family": "F2", "use": "payout"}, RESOURCES),
        ("unknown capability", {**base, "family": "F4"}, RESOURCES),
        # Extra scenarios for our rule.
        ("age at order, customer", {**base, "family": "F2b+F1", "use": "customer"}, RESOURCES),
        ("product, customer, OpenRouter down", {**base, "family": "F3", "use": "customer"}, openrouter_down),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", help="show only the named scenario")
    args = parser.parse_args()
    found = False
    for name, request, resources in scenarios():
        if args.scenario and name != args.scenario:
            continue
        found = True
        print(json.dumps({"scenario": name, "nature": "simulation", "request": request,
                          "result": choose(request, resources)}))
    if not found:
        parser.error("unknown scenario")


if __name__ == "__main__":
    main()
