"""Re-run Pair B's quorum counts (C08, C09) with Pair A's completed vote_k_sur_n.

Pair A's completed method is in TD2/pair-A/skeleton-multi-llm-en.py; the skeleton needs
sandbox_sqlite.py next to it (kept in TD2/pair-A/). This script copies the three
files into a temporary folder, loads the vote through TD2/pair-A/atelier-vote.py, and
votes on the last attempt of each model in TD1/results/traces-td1.csv.
No network call; the reference is printed only after each decision.

Usage, from the repository root:  python3 TD2/pair-b/check-votes-with-pair-A.py
It is a regression test: every decision is compared with the committed votes-pair-A-method.jsonl
(consensus, value, votes, models) and the script exits with status 1 if one differs. It writes nothing.
"""
import csv, importlib.util, json, shutil, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TD2 = ROOT / "TD2"
TRACES = ROOT / "TD1" / "results" / "traces-td1.csv"
REFERENCE = ROOT / "TD1" / "reference-td1.csv"

tmp = Path(tempfile.mkdtemp())
for src in (TD2 / "pair-A" / "skeleton-multi-llm-en.py", TD2 / "pair-A" / "atelier-vote.py", TD2 / "pair-A" / "sandbox_sqlite.py"):
    shutil.copy(src, tmp / src.name)

spec = importlib.util.spec_from_file_location("atelier_vote", tmp / "atelier-vote.py")
av = importlib.util.module_from_spec(spec)
sys.modules["atelier_vote"] = av
spec.loader.exec_module(av)
vote = av.load_vote()

rows = list(csv.DictReader(TRACES.open(encoding="utf-8")))
all_five = sorted({(r["provider"], r["model_requested"]) for r in rows})
refs = {r["case_id"]: int(r["revenue_cents"]) for r in csv.DictReader(REFERENCE.open(encoding="utf-8")) if r.get("revenue_cents")}

expected = {(e["case"], e["quorum"]): e for e in map(json.loads, (Path(__file__).with_name("votes-pair-A-method.jsonl")
                                                                    .read_text(encoding="utf-8").splitlines())) if e}
failures = 0
for case in ("C08", "C09"):
    for label, panel, k in (("2-of-3 fixed panel", av.PANEL, 2), ("3-of-5 all models", all_five, 3)):
        proposals = av.proposals_for(rows, case, "real", panel=panel)
        decision = vote(proposals, k)
        record = {"case": case, "quorum": label, "n": len(proposals), "k": k,
                  "decision": decision, "reference": refs.get(case),
                  "matches_reference": (decision["value"] == refs.get(case)) if decision["consensus"] else None}
        ok = expected.get((case, label)) == record
        failures += not ok
        print(("OK   " if ok else "DIFF ") + json.dumps(record))
shutil.rmtree(tmp)
print("regression test:", "passed (4/4 decisions unchanged)" if not failures else f"FAILED ({failures} decision(s) changed)")
sys.exit(1 if failures else 0)
