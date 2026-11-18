"""Single read-only verification of all Pair B evidence (C08 and C09), answering question 5 of review B-by-A.

From the repository root:  python3 TD2/pair-b/check_all.py
Runs, without writing anything: analyse.py (C08, check mode), C09/check_c09.py (C09 evidence + delivery gate),
C09/check_c09_csv.py (C09 without SQL, compared with the reference) and check-votes-with-pair-A.py (vote
regression test with Pair A's vote_k_sur_n). Prints the input hashes and one line per step; exit 0 only if all pass.
"""
import hashlib, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = [ROOT / "TD1/results/traces-td1.csv", ROOT / "TD1/reference-td1.csv", HERE / "data/boutique.sqlite",
          ROOT / "TD2/pair-A/skeleton-multi-llm-en.py"]
STEPS = [("C08 evidence (analyse.py, check mode)", [HERE / "analyse.py"]),
         ("C09 evidence and delivery gate (check_c09.py)", [HERE / "C09/check_c09.py"]),
         ("C09 without SQL vs reference (check_c09_csv.py)", [HERE / "C09/check_c09_csv.py"]),
         ("Votes with Pair A's vote_k_sur_n (regression test)", [HERE / "check-votes-with-pair-A.py"])]

print("Inputs (SHA-256, line endings normalised for text files):")
for p in INPUTS:
    data = p.read_bytes()
    if p.suffix != ".sqlite":
        data = data.replace(b"\r\n", b"\n")
    print(f"  {hashlib.sha256(data).hexdigest()[:16]}  {p.relative_to(ROOT)}")
print()
failed = 0
for name, cmd in STEPS:
    r = subprocess.run([sys.executable, "-I", *map(str, cmd)], cwd=ROOT, capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or [r.stderr.strip()])[-1]
    print(f"{'PASS' if r.returncode == 0 else 'FAIL'}  {name}: {last}")
    failed += r.returncode != 0
print(f"\n{len(STEPS) - failed}/{len(STEPS)} steps passed")
sys.exit(1 if failed else 0)
