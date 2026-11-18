#!/usr/bin/env python3
"""TD 2, Pair C: the routing simulator adapted to the DIA3-1 routing rule (policy pairC-v2.2).

v2 changes: stakes alone choose the check rung, TD 1 evidence can only raise it;
"none" becomes "format check by code"; each decision logs the policy, the check id
and every ruled-out resource with its reason.
v2.1 (review C-by-B): TD 1 cells in paid and abstention reasons, check status and
failure path per use, F2b+F3 combinations, deterministic fallback handed over outside
the simulator, no two-gpt-oss quorum.
v2.2 (review C-by-A): unknown use abstains, families parsed in any order, cash always
a float, age predicate written as in Pair B.

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


#9)Level of each base family; a combination takes its strictest part, in any order ("F1+F2" = "F2+F1")
PART_LEVEL = {"F1": 1, "F3": 1, "F2b": 2, "F2": 3}


def family_level(family):
    parts = [p.strip() for p in str(family).split("+")]
    if not parts or any(p not in PART_LEVEL for p in parts):
        return None
    return max(PART_LEVEL[p] for p in parts)

RESOURCES = [
    # OpenRouter free endpoints: no paid route for these exact models.
    {"id": "dots-3-note-free", "td1": {1: (10, 10), 2: (0, 2), 3: (5, 8)}, "level": 1, "access": "free", "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None,
     "evidence": "E: F1 6/6 (C01 C04-C07 C20), F3 4/4 (C03 C12-C14); F2 2/4 (C08 C09 wrong), F2b 0/1 (C10)"},
    {"id": "north-mini-code-free", "td1": {1: (10, 10), 2: (0, 2), 3: (2, 8)}, "level": 1, "access": "free", "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None,
     "evidence": "C: F1 6/6, F3 4/4; F2 0/4 (C11 invalid SQL), F2b 0/1, C19 correct by chance"},
    # Groq free tier (route used in TD 1).
    {"id": "gpt-oss-20b-groq-free", "td1": {1: (10, 10), 2: (2, 2), 3: (5, 8)}, "level": 2, "access": "free", "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None,
     "evidence": "B: F1 6/6, F3 4/4, F2b 1/1 (C10) and C18 correct; F2 1/4 (C02 C08 C11 wrong)"},
    {"id": "gpt-oss-120b-groq-free", "td1": {1: (10, 10), 2: (2, 2), 3: (8, 8)}, "level": 3, "access": "free", "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None,
     "evidence": "A: 20/20, F2 4/4 (C02 C08 C09 C11), combined 5/5 (C15-C19), F2b 1/1 (C10)"},
    {"id": "qwen3.8-27b-groq-free", "td1": {1: (10, 10), 2: (1, 2), 3: (4, 8)}, "level": 1, "access": "free", "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None,
     "evidence": "D: F1 6/6, F3 4/4; F2 3/4 (C09 wrong), F2b 0/1 (C10 wrong)"},
    # Groq Developer paid route, same models (prices 2026-10-05).
    {"id": "gpt-oss-20b-groq-dev", "td1": {1: (10, 10), 2: (2, 2), 3: (5, 8)}, "level": 2, "access": "tokens", "available": True,
     "cash": per_request(0.075, 0.30), "allocation": per_request(0.075, 0.30), "reset_minutes": None,
     "evidence": "B (paid route of the same model): F1 6/6, F3 4/4, F2b 1/1 (C10) and C18 correct; F2 1/4 (C02 C08 C11 wrong)"},
    {"id": "gpt-oss-120b-groq-dev", "td1": {1: (10, 10), 2: (2, 2), 3: (8, 8)}, "level": 3, "access": "tokens", "available": True,
     "cash": per_request(0.15, 0.60), "allocation": per_request(0.15, 0.60), "reset_minutes": None,
     "evidence": "A (paid route of the same model): 20/20, F2 4/4 (C02 C08 C09 C11), combined 5/5 (C15-C19), F2b 1/1 (C10)"},
    {"id": "qwen3.8-27b-groq-dev", "td1": {1: (10, 10), 2: (1, 2), 3: (4, 8)}, "level": 1, "access": "tokens", "available": True,
     "cash": per_request(0.80, 4.00), "allocation": per_request(0.80, 4.00), "reset_minutes": None,
     "evidence": "D (paid route of the same model): F1 6/6, F3 4/4; F2 3/4 (C09 wrong), F2b 0/1 (C10 wrong)"},
]

QUORUM_F1_F3 = ("2-of-3 quorum of the three cheapest available models among dots-3-note, north-mini-code, "
                "qwen3.8-27b (Groq free), gpt-oss-20b (all 10/10 on C01 C03-C07 C12-C14 C20)")
REF_PERIOD = "deterministic reference (closed-open period / product IN template)"
REF_AGE = ("deterministic reference (completed age: date(ref,'-26 years') < birth_date <= date(ref,'-25 years'), "
           "same predicate as Pair B, checked equal to the references of C02 C08 C09 C11; "
           "no quorum: shared wrong values on C08, C09, C10)")

POLICY = "pairC-v2.2"

#1)Stakes choose the check: one rung per use, the same whatever the family
STAKES_RUNG = {"dashboard": 0, "customer": 1, "payout": 3}
#2)TD 1 evidence can only forbid the lowest rung: format-only needs 100 % on at least MIN_CASES cells
MIN_CASES = 3
#3)On age families, models were wrong together (C08, C09, C10): the quorum rung is replaced by the reference
AGE_LEVELS = {2, 3}
LEVEL_CELLS = {1: "C01 C03 C04 C05 C06 C07 C12 C13 C14 C20",
               2: "C10 C18",
               3: "C02 C08 C09 C11 C15 C16 C17 C19"}
#8)C5: checks are simulated here; what happens when a check fails, by use
ON_FAILURE = {"dashboard": "no delivery; value flagged and recomputed at the next run",
              "customer": "no delivery; answer 'no verified figure yet' (abstain)",
              "payout": "no delivery; sent to human review"}
REF_AGE_ORDER = ("deterministic reference (age at each order: date(o.date,'-26 years') < birth_date "
                 "<= date(o.date,'-25 years'), checked equal to the reference of C10; "
                 "no quorum: shared wrong values on C08, C09, C10)")


def check_text(rung, level):
    #4)The text of each rung, adapted to the family
    ref = {1: REF_PERIOD, 2: REF_AGE_ORDER, 3: REF_AGE}[level]
    quorum = QUORUM_F1_F3  # only level 1 can reach the quorum rung (AGE_LEVELS skip it)
    return ["format check by code (one integer, euro cents, excluding VAT)",
            "format check + " + quorum,
            "format check + " + ref,
            "format check + " + ref + " + human review"][rung]


def check_for(request, level, chosen):
    #5)Stakes first, then the two TD 1 adjustments, each one logged
    rung = STAKES_RUNG[request["use"]]
    why = [f"stakes '{request['use']}' -> rung {rung}"]
    if rung == 0 and chosen is not None:
        ok, total = chosen["td1"][level]
        if ok < total or total < MIN_CASES:
            rung = 1
            why.append(f"{chosen['id']} {ok}/{total} on level-{level} cells: too thin for format only")
    if rung == 1 and level in AGE_LEVELS:
        rung = 2
        why.append("age family: no quorum, shared wrong values on C08, C09, C10")
    return {"id": f"{POLICY}-rung-{rung}", "check": check_text(rung, level), "why": why,
            "status": "simulated: named here, executed by code before delivery",
            "on_failure": ON_FAILURE[request["use"]] + " (a check in error counts as a failure)"}


def ruled_out(resources, level, request, chosen):
    #6)Every resource not chosen, with the reason, as in the lecture's decision log
    out = []
    for r in resources:
        if chosen is not None and r["id"] == chosen["id"]:
            continue
        if r["level"] < level:
            ok, total = r["td1"][level]
            why = f"level {r['level']} below level {level} (TD 1: {ok}/{total})"
        elif not r["available"]:
            why = "unavailable (quota exhausted)"
            if r["reset_minutes"] is not None:
                why += f", refill in {r['reset_minutes']} min"
        elif r["cash"] > request["budget"]:
            why = f"cash {r['cash']} USD above budget {request['budget']} USD"
        else:
            why = "eligible, but after the chosen resource in the priority order"
        out.append({"id": r["id"], "why": why})
    return out


def decision(action, chosen, cash, request, level, resources, reason, **extra):
    #7)One record per decision: policy, check id, chosen and ruled-out resources
    return {"action": action, "resource": chosen["id"] if chosen else None, "cash": cash,
            "policy": POLICY, "checks": check_for(request, level, chosen), "reason": reason,
            "ruled_out": ruled_out(resources, level, request, chosen), **extra}


def choose(request, resources):
    """Same priority order as the kit: included capacity, defer, paid, abstain."""
    level = family_level(request.get("family"))
    if level is None:
        return {"action": "abstain", "resource": None, "cash": 0.0, "policy": POLICY,
                "checks": {"id": f"{POLICY}-human", "check": "human review",
                           "why": ["unknown family"],
                           "status": "simulated: no automated check; unsupported request",
                           "on_failure": "no delivery; human review required"},
                "reason": f"family {request.get('family')!r} not covered by TD 1 C01-C20: no eligibility evidence",
                "ruled_out": [{"id": r["id"], "why": "no TD 1 evidence for this family"} for r in resources]}
    if request.get("use") not in STAKES_RUNG:
        return {"action": "abstain", "resource": None, "cash": 0.0, "policy": POLICY,
                "checks": {"id": f"{POLICY}-human", "check": "human review",
                           "why": ["unknown use"],
                           "status": "simulated: no automated check; unsupported request",
                           "on_failure": "no delivery; human review required"},
                "reason": f"use {request.get('use')!r} is not one of {sorted(STAKES_RUNG)}: the stakes, so the check, are unknown",
                "ruled_out": [{"id": r["id"], "why": "stakes unknown"} for r in resources]}
    eligible = [r for r in resources if r["level"] >= level]
    included = [r for r in eligible if r["available"] and r["cash"] == 0]
    if included:
        chosen = min(included, key=lambda r: (r["allocation"], r["level"], r["id"]))
        return decision("run", chosen, 0.0, request, level, resources,
                        f"cheapest eligible included capacity for level {level}; TD 1: {chosen['evidence']}")
    waiting = [r for r in eligible if not r["available"] and r["cash"] == 0
               and r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: r["reset_minutes"])
        return decision("defer", chosen, 0.0, request, level, resources,
                        ("free quota exhausted, refill before deadline; recheck availability at wake-up "
                         f"(TD 1: all six HTTP 429 recovered on attempt 2); TD 1: {chosen['evidence']}"),
                        wake_in_minutes=chosen["reset_minutes"])
    paid = [r for r in eligible if r["available"] and r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=lambda r: (r["cash"], r["allocation"], r["id"]))
        return decision("run", chosen, chosen["cash"], request, level, resources,
                        f"paid route within the authorised budget; TD 1: {chosen['evidence']}")
    return decision("abstain", None, 0.0, request, level, resources,
                    f"no level-{level} resource within deadline and budget; level-{level} cells "
                    f"{LEVEL_CELLS[level]}: eligible in TD 1 = "
                    + ", ".join(f"{r['id']} {r['td1'][level][0]}/{r['td1'][level][1]}" for r in eligible),
                    handover=("outside this simulator: the deterministic reference query if a template exists "
                              "for this exact question, otherwise a person"))


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
        ("age at order, dashboard", {**base, "family": "F2b"}, RESOURCES),
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
