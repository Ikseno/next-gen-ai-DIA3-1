"""One-command, read-only check of the C09 evidence (Pair B), answering review B-by-A, issues 1 and 3.

It never writes a file. From the repository root:
    python3 TD2/pair-b/C09/check_c09.py

1. Data:      boutique.sqlite and the three CSV files match the SHA-256 of data/manifest.json.
2. Evidence:  re-runs faulty-north-mini-code.sql, faulty-qwen.sql (both must return 0), the delta query
              (compared with delta-output.csv) and the empty-filter check (compared with empty-filter-check.csv),
              then recomputes C09 without SQL (check_c09_csv.py) and compares with the reference 487980.
3. Gate:      runs the deterministic delivery gate `age-window-nonempty` on positive and negative cases.
Exit code 0 only if every line is OK.
"""
import csv, hashlib, io, json, os, sqlite3, sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
sys.path.insert(0, HERE)
from check_c09_csv import revenue_by_customer  # noqa: E402

REFERENCE = 487980
results = []


def check(name, ok, detail=''):
    results.append(ok)
    print(f"{'OK  ' if ok else 'FAIL'} {name}{' — ' + detail if detail else ''}")


def sha256_text(path):
    # line endings normalised to LF, so the check passes on a Windows checkout too
    return hashlib.sha256(open(path, 'rb').read().replace(b'\r\n', b'\n')).hexdigest()


def statements(path):
    sql = open(path, encoding='utf-8').read()
    lines = [l for l in sql.splitlines() if not l.strip().startswith('--')]
    return [s.strip() for s in '\n'.join(lines).split(';') if s.strip()]


def as_rows(cursor_rows):
    return [[str(v) for v in r] for r in cursor_rows]


def committed_csv(path):
    rows = list(csv.reader(open(path, newline='', encoding='utf-8')))
    return rows[0], rows[1:]


# --- deterministic delivery gate -------------------------------------------------------------
def age_window(ref_day, target_age):
    """Birth-date window of a completed age on ref_day: ] ref - (age+1) years ; ref - age years ]."""
    return f"date('{ref_day}', '-{target_age + 1} years')", f"date('{ref_day}', '-{target_age} years')"


def age_window_nonempty(db, model_value, ref_day, target_age):
    """Sanity gate run AFTER the vote on an F2 (age-at-a-date) question.

    It only judges a value of 0: a 0 is delivered only if code finds no customer with orders in the age
    window. It does NOT verify a non-zero total; that is the separate full numerical check below.
    """
    if model_value != 0:
        return 'not applicable (non-zero value: use the full numerical check)'
    lo, hi = age_window(ref_day, target_age)
    n = db.execute(f"""SELECT COUNT(DISTINCT c.customer_id) FROM customers c
                       JOIN orders o ON o.customer_id = c.customer_id
                       WHERE c.birth_date > {lo} AND c.birth_date <= {hi}""").fetchone()[0]
    return 'accept' if n == 0 else f'reject ({n} customers with orders in the window)'


def full_numerical_check(db, model_value, ref_day, target_age):
    """Full check: recompute the revenue of the age window by code and compare with the model's value."""
    lo, hi = age_window(ref_day, target_age)
    expected = db.execute(f"""SELECT COALESCE(SUM(o.quantity_product * p.price), 0) FROM customers c
                              JOIN orders o ON o.customer_id = c.customer_id
                              JOIN product p ON p.product_id = o.product_id
                              WHERE c.birth_date > {lo} AND c.birth_date <= {hi}""").fetchone()[0]
    return ('accept' if model_value == expected else f'reject (expected {expected})'), expected


def main():
    manifest = json.load(open(os.path.join(DATA, 'manifest.json')))
    db_path = os.path.join(DATA, 'boutique.sqlite')
    check('data: boutique.sqlite matches manifest',
          hashlib.sha256(open(db_path, 'rb').read()).hexdigest() == manifest['sqlite_file_sha256'])
    for name, h in manifest['csv_sha256'].items():
        check(f'data: {name} matches manifest', sha256_text(os.path.join(DATA, name)) == h)

    db = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)

    for f in ('faulty-north-mini-code.sql', 'faulty-qwen.sql'):
        value = db.execute(statements(os.path.join(HERE, f))[0]).fetchone()[0]
        check(f'evidence: {f} returns 0', value == 0, f'got {value}')

    header, committed = committed_csv(os.path.join(HERE, 'delta-output.csv'))
    rows = as_rows(db.execute(statements(os.path.join(HERE, 'delta-query.sql'))[0]).fetchall())
    check('evidence: delta query = delta-output.csv', rows == committed, f'{len(rows)} customers')
    total = sum(int(r[3]) for r in rows)
    check('evidence: delta total = reference - 0', total == REFERENCE, f'{total}')

    header, committed = committed_csv(os.path.join(HERE, 'empty-filter-check.csv'))
    rows = as_rows(db.execute(statements(os.path.join(HERE, 'empty-filter-check.sql'))[0]).fetchall())
    check('evidence: empty-filter check = empty-filter-check.csv', rows == committed,
          '; '.join(f'{r[0]}: {r[2]} customers' for r in rows))

    by_csv = revenue_by_customer(DATA)
    check('independent: CSV recomputation (no SQL) = reference', sum(v for _, v in by_csv.values()) == REFERENCE)
    check('independent: same customers as the delta query',
          sorted(by_csv) == sorted(r[0] for r in as_rows(db.execute(statements(os.path.join(HERE, 'delta-query.sql'))[0]).fetchall())))

    print('\nDelivery gate age-window-nonempty (sanity, zeros only) and full numerical check:')
    cases = [  # (case, value proposed, ref day, age, expected gate, expected full check)
        ('C09 Cohere = 0 (wrong)', 0, '2026-09-26', 25, 'reject', 'reject'),
        ('C09 Qwen = 0 (wrong)', 0, '2026-09-26', 25, 'reject', 'reject'),
        ('negative case: true 0, age 80 on 2026-09-26 (nobody in the window)', 0, '2026-09-26', 80, 'accept', 'accept'),
        ('C09 gpt-oss-120b = 487980 (right)', 487980, '2026-09-26', 25, 'not applicable', 'accept'),
        ('C09 Dots = 369240 (wrong, non-zero)', 369240, '2026-09-26', 25, 'not applicable', 'reject'),
        ('C08 gpt-oss-20b / Dots = 25920 (wrong, non-zero)', 25920, '2026-09-24', 25, 'not applicable', 'reject'),
        ('C08 Cohere = 1188090 (wrong, non-zero)', 1188090, '2026-09-24', 25, 'not applicable', 'reject'),
        ('C08 gpt-oss-120b / Qwen = 605580 (right)', 605580, '2026-09-24', 25, 'not applicable', 'accept'),
    ]
    for name, value, ref_day, a, exp_gate, exp_full in cases:
        gate = age_window_nonempty(db, value, ref_day, a)
        full, expected = full_numerical_check(db, value, ref_day, a)
        check(f'gate: {name}', gate.startswith(exp_gate) and full.startswith(exp_full),
              f'gate {gate}; full check {full}')

    print(f"\n{sum(results)}/{len(results)} checks OK")
    sys.exit(0 if all(results) else 1)


if __name__ == '__main__':
    main()
