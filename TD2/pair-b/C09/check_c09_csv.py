"""Independent check of C09 without SQL: reads the three CSV files and computes completed age
by year, month and day (age = year difference - (birthday not reached yet)).

Usage (from the repository root):
    python3 TD2/pair-b/C09/check_c09_csv.py                    # uses TD2/pair-b/data by default
    python3 TD2/pair-b/C09/check_c09_csv.py --data <folder with product.csv, customers.csv, orders.csv>
"""
import argparse, csv, os, sys
from datetime import date

DEFAULT_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
REFERENCE_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'TD1', 'reference-td1.csv')


def age(born, on):
    return on.year - born.year - ((on.month, on.day) < (born.month, born.day))


def revenue_by_customer(data_dir, ref_day=date(2026, 9, 26), target_age=25):
    """Revenue (cents) of every customer whose completed age on ref_day is target_age."""
    price = {r['product_id']: int(r['price']) for r in csv.DictReader(open(os.path.join(data_dir, 'product.csv'), newline=''))}
    born = {r['customer_id']: date.fromisoformat(r['birth_date'])
            for r in csv.DictReader(open(os.path.join(data_dir, 'customers.csv'), newline=''))}
    per = {}
    for r in csv.DictReader(open(os.path.join(data_dir, 'orders.csv'), newline='')):
        c = r['customer_id']
        if age(born[c], ref_day) == target_age:
            per[c] = per.get(c, 0) + int(r['quantity_product']) * price[r['product_id']]
    return {c: (born[c], per[c]) for c in sorted(per, key=lambda k: born[k])}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--data', default=DEFAULT_DATA, help='folder holding product.csv, customers.csv and orders.csv')
    parser.add_argument('--expected', type=int, default=None,
                        help='expected total in cents (default: C09 in TD1/reference-td1.csv)')
    parser.add_argument('legacy_data', nargs='?', help=argparse.SUPPRESS)  # old positional form, still accepted
    args = parser.parse_args()
    data_dir = args.legacy_data or args.data
    missing = [f for f in ('product.csv', 'customers.csv', 'orders.csv') if not os.path.isfile(os.path.join(data_dir, f))]
    if missing:
        parser.error(f'{data_dir}: missing {", ".join(missing)}')
    rows = revenue_by_customer(data_dir)
    for c, (b, rev) in rows.items():
        print(c, b, rev)
    total = sum(rev for _, rev in rows.values())
    print('TOTAL', total)
    expected = args.expected
    if expected is None:
        expected = next(int(r['revenue_cents']) for r in csv.DictReader(open(REFERENCE_CSV, newline='', encoding='utf-8'))
                        if r['case_id'] == 'C09')
    if total != expected:
        sys.exit(f'FAIL: total {total} differs from the expected {expected}')
    print(f'OK: total equals the expected {expected}')


if __name__ == '__main__':
    main()
