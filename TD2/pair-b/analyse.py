"""Reproduce Pair B evidence offline: python TD2/pair-b/analyse.py."""
import csv
import hashlib
import json
import sqlite3
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = HERE / 'data'

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))

def write_csv(name, rows, fields):
    with (HERE / name).open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def main():
    traces_path = ROOT / 'TD1/results/traces-td1.csv'
    refs_path = ROOT / 'TD1/reference-td1.csv'
    attempts = read_csv(traces_path)
    # Preserve the source; select the last attempt per provider/model/question.
    latest = {}
    for row in sorted(attempts, key=lambda r: (r['date_utc'], int(r['attempts']))):
        latest[(row['provider'], row['model_requested'], row['case_id'])] = row
    traces = list(latest.values())
    assert len(traces) == 100
    shared = defaultdict(list)
    for row in traces:
        if row['verdict'] == 'incorrect':
            shared[(row['case_id'], int(row['value']))].append(row['model_requested'])
    candidates = [dict(case_id=case, value=value, models=models)
                  for (case, value), models in sorted(shared.items()) if len(models) >= 2]
    case = [r for r in traces if r['case_id'] == 'C08']
    reference = next(r for r in read_csv(refs_path) if r['case_id'] == 'C08')
    faulty = [r for r in case if r['value'] == '25920']
    assert len(faulty) == 2 and all(r['verdict'] == 'incorrect' for r in faulty)
    sql = {
        'reference.sql': reference['sql'],
        'faulty-gpt-oss-20b.sql': next(r['sql'] for r in faulty if r['provider'] == 'groq'),
        'faulty-dots.sql': next(r['sql'] for r in faulty if r['provider'] == 'openrouter'),
        'delta.sql': """-- Customers aged 25 on 2026-09-24 omitted by BOTH faulty queries.
SELECT c.customer_id, c.birth_date,
       SUM(o.quantity_product * p.price) AS revenue_cents
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN product p ON p.product_id = o.product_id
WHERE c.birth_date > '2000-09-24'
  AND c.birth_date <= '2001-09-24'
  AND NOT (c.birth_date >= '2001-09-24' AND c.birth_date < '2001-09-25')
  AND NOT (c.birth_date = '2001-09-24')
GROUP BY c.customer_id, c.birth_date
ORDER BY c.customer_id;""",
    }
    for name, query in sql.items():
        (HERE / name).write_text(query.rstrip() + '\n', encoding='utf-8')
    manifest = json.loads((DATA / 'manifest.json').read_text())
    db = DATA / 'boutique.sqlite'
    assert hashlib.sha256(db.read_bytes()).hexdigest() == manifest['sqlite_file_sha256']
    for name, expected in manifest['csv_sha256'].items():
        assert hashlib.sha256((DATA / name).read_bytes()).hexdigest() == expected
    with sqlite3.connect(db.as_uri() + '?mode=ro', uri=True) as connection:
        connection.row_factory = sqlite3.Row
        values = {name: connection.execute(query).fetchone()[0]
                  for name, query in sql.items() if name != 'delta.sql'}
        delta = [dict(r) for r in connection.execute(sql['delta.sql'])]
    assert values['reference.sql'] == int(reference['revenue_cents']) == 605580
    assert values['faulty-gpt-oss-20b.sql'] == values['faulty-dots.sql'] == 25920
    assert sum(r['revenue_cents'] for r in delta) == 579660 == 605580 - 25920
    # Independent check: CSV joins and completed-age arithmetic, without SQL.
    customers = {r['customer_id']: r for r in read_csv(DATA / 'customers.csv')}
    prices = {r['product_id']: int(r['price']) for r in read_csv(DATA / 'product.csv')}
    totals = defaultdict(int)
    day = date(2026, 9, 24)
    for order in read_csv(DATA / 'orders.csv'):
        birth = date.fromisoformat(customers[order['customer_id']]['birth_date'])
        age = day.year - birth.year - ((day.month, day.day) < (birth.month, birth.day))
        if age == 25:
            totals[order['customer_id']] += int(order['quantity_product']) * prices[order['product_id']]
    omitted = {key: value for key, value in totals.items()
               if customers[key]['birth_date'] != '2001-09-24'}
    assert sum(totals.values()) == 605580
    assert omitted == {r['customer_id']: r['revenue_cents'] for r in delta}
    panel = {'openai/gpt-oss-120b', 'cohere/north-mini-code:free', 'qwen/qwen3.8-27b'}
    decisions = []
    for label, members, threshold in [('2-of-3', [r for r in case if r['model_requested'] in panel], 2),
                                      ('3-of-5', case, 3)]:
        assert len(members) in (3, 5)
        # Hand-count equivalent; only executed numerical answers vote.
        counts = Counter(int(r['value']) for r in members if r['verdict'] in ('correct', 'incorrect'))
        value, votes = counts.most_common(1)[0]
        consensus = votes >= threshold
        decisions.append(dict(panel=label, n=len(members), k=threshold,
                              counts=dict(counts), consensus=consensus,
                              value=value if consensus else None, votes=votes))
    write_csv('delta-customers.csv', delta, ['customer_id', 'birth_date', 'revenue_cents'])
    write_csv('C08-models.csv', [{key: r[key] for key in ['provider', 'model_requested', 'value', 'reference', 'verdict']} for r in case],
              ['provider', 'model_requested', 'value', 'reference', 'verdict'])
    evidence = dict(case_id='C08', nature='real, stored team TD1 traces; offline SQL replay',
                    source_attempt_rows=len(attempts), final_cells=len(traces),
                    shared_wrong_candidates=candidates, sql_values=values,
                    missing_customers=len(delta), delta_cents=579660,
                    independent_csv_reference=sum(totals.values()), independent_csv_delta=sum(omitted.values()),
                    quorum_counts=decisions, pair_a_integration='Pending: compare with Pair A vote_k_sur_n implementation',
                    source_sha256={str(path.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(path.read_bytes()).hexdigest()
                                   for path in [traces_path, refs_path, db]})
    (HERE / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(evidence, indent=2))

if __name__ == '__main__':
    main()
