"""Compute TD1 references with SQLite and cross-check the supplied CSV data.
Usage: python build_references.py PATH_TO_KIT
AI-assisted; requires peer and instructor validation before model experiments.
"""
import csv
import json
import sqlite3
import sys
from datetime import date
from pathlib import Path

kit = Path(sys.argv[1]).resolve()
out = Path(__file__).resolve().parent
# case, inclusive start, exclusive end, reference date (or 'order'), products
cases = [
 ('C01','2026-03-01','2026-06-01',None,None),
 ('C02',None,None,'2026-09-25',None),
 ('C03','2026-01-01','2026-07-01',None,'abc'),
 ('C04','2026-01-01','2026-10-01',None,None),
 ('C05','2026-06-01','2026-06-02',None,None),
 ('C06','2025-01-01','2026-01-01',None,None),
 ('C07','2026-05-31','2026-06-01',None,None),
 ('C08',None,None,'2026-09-24',None),
 ('C09',None,None,'2026-09-26',None),
 ('C10',None,None,'order',None),
 ('C11',None,None,'2026-12-01',None),
 ('C12',None,None,None,'abc'),
 ('C13','2026-04-01','2026-05-01',None,'ac'),
 ('C14','2026-10-01','2026-12-01',None,'abc'),
 ('C15','2026-03-01','2026-06-01','2026-09-25',None),
 ('C16',None,None,'2026-09-25','abc'),
 ('C17','2026-01-01','2026-07-01','2026-09-25','abc'),
 ('C18','2026-05-01','2026-06-01','order',None),
 ('C19','2026-09-01','2026-10-01','2026-09-25','d'),
 ('C20','2026-06-01','2026-09-01',None,None),
]

def read_csv(name):
    with (kit/'data'/name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

prices = {r['product_id']:int(r['price']) for r in read_csv('product.csv')}
births = {r['customer_id']:date.fromisoformat(r['birth_date']) for r in read_csv('customers.csv')}
orders = read_csv('orders.csv')
rows, checks = [], []
with sqlite3.connect((kit/'data'/'boutique.sqlite').as_uri()+'?mode=ro', uri=True) as con:
    for case, start, end, ref, products in cases:
        conditions = []
        if start:
            conditions += [f"o.date >= '{start} 00:00:00'", f"o.date < '{end} 00:00:00'"]
        if ref:
            sql_date = 'o.date' if ref == 'order' else f"'{ref}'"
            conditions.append(f"(CAST(strftime('%Y', {sql_date}) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) - (strftime('%m-%d', {sql_date}) < strftime('%m-%d', c.birth_date))) = 25")
        if products:
            conditions.append('o.product_id IN ('+', '.join(repr(p) for p in products)+')')
        sql = 'SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p ON p.product_id = o.product_id JOIN customers AS c ON c.customer_id = o.customer_id'
        if conditions:
            sql += ' WHERE '+' AND '.join(conditions)
        sql += ';'
        value = con.execute(sql).fetchone()[0]
        csv_total = 0
        for order in orders:
            when = date.fromisoformat(order['date'][:10])
            if start and not (date.fromisoformat(start) <= when < date.fromisoformat(end)):
                continue
            if products and order['product_id'] not in products:
                continue
            if ref:
                at = when if ref == 'order' else date.fromisoformat(ref)
                birth = births[order['customer_id']]
                age = at.year-birth.year-((at.month,at.day)<(birth.month,birth.day))
                if age != 25:
                    continue
            csv_total += int(order['quantity_product'])*prices[order['product_id']]
        if value != csv_total:
            raise ValueError(f'{case}: SQL {value} != CSV {csv_total}')
        rows.append({'case_id':case,'sql':sql,'revenue_cents':value})
        checks.append({'case_id':case,'sql_cents':value,'csv_cents':csv_total,'match':True})
with (out/'reference-td1.csv').open('w',encoding='utf-8',newline='') as f:
    writer = csv.DictWriter(f,fieldnames=['case_id','sql','revenue_cents'])
    writer.writeheader()
    writer.writerows(rows)
(out/'reference-crosscheck.json').write_text(json.dumps({'method':'SQLite read-only execution versus CSV iteration; shared case definitions','peer_review':'pending','instructor_validation':'pending','checks':checks},indent=2),encoding='utf-8')
print('\n'.join(f"{r['case_id']}: {r['revenue_cents']} cents" for r in rows))
print('20/20 SQL and CSV computations agree. Peer/instructor validation remains pending.')
