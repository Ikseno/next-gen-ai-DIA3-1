"""Independent check of C09 without SQL: reads the three CSV files of the kit and computes
completed age by year, month and day. Usage: python3 check_c09_csv.py <path to kit-td1/data>"""
import csv, sys, os
from datetime import date
d = sys.argv[1]
ref_day = date(2026, 9, 26)
def age(b, on):
    return on.year - b.year - ((on.month, on.day) < (b.month, b.day))
price = {r['product_id']: int(r['price']) for r in csv.DictReader(open(os.path.join(d, 'product.csv')))}
born = {r['customer_id']: date.fromisoformat(r['birth_date']) for r in csv.DictReader(open(os.path.join(d, 'customers.csv')))}
per = {}
for r in csv.DictReader(open(os.path.join(d, 'orders.csv'))):
    c = r['customer_id']
    if age(born[c], ref_day) == 25:
        per[c] = per.get(c, 0) + int(r['quantity_product']) * price[r['product_id']]
for c in sorted(per, key=lambda k: born[k]):
    print(c, born[c], per[c])
print('TOTAL', sum(per.values()))
