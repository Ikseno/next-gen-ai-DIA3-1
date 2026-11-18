#!/usr/bin/env python3
"""TD2 Task A: offline 2-of-3 vs 3-of-5 comparison on TD1 traces.

Place next to skeleton-multi-llm-en.py and sandbox_sqlite.py. Run from the
repository root: python TD2/pair-A/td2_compare_votes.py
No network, no API keys. Never passes references into the voting function.
"""
import argparse
import csv
import io
import importlib.util
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
TRACES = HERE.parent.parent / 'TD1' / 'results' / 'traces-td1.csv'
REFERENCE = HERE.parent.parent / 'TD1' / 'reference-td1.csv'
OUTPUT = HERE.parent / 'reports' / 'td2-task-A-comparison.csv'
MODELS = [
    ('groq', 'openai/gpt-oss-120b'),
    ('groq', 'openai/gpt-oss-20b'),
    ('openrouter', 'cohere/north-mini-code:free'),
    ('groq', 'qwen/qwen3.8-27b'),
    ('openrouter', 'dots-studio/dots-3-note-preview:free'),
]
PANEL3 = [MODELS[0], MODELS[2], MODELS[3]]  # fixed instructor panel


def load_vote():
    path = HERE / 'skeleton-multi-llm-en.py'
    spec = importlib.util.spec_from_file_location('td2_skeleton', path)
    import sys
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return lambda proposals, k: mod.Orchestrateur.vote_k_sur_n(None, proposals, k)


def read_csv(path):
    with path.open('r', newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def last_rows_for_case(all_rows, case):
    # Source export contains retry attempts; only the last chronological attempt
    # for each provider/model/case is allowed to supply a vote.
    rows = [r for r in all_rows if r.get('case_id') == case and r.get('nature') == 'real']
    rows.sort(key=lambda r: (r.get('date_utc') or '', int(r.get('attempts') or 0)))
    last = {}
    for row in rows:
        last[(row.get('provider'), row.get('model_requested'))] = row
    return last


def proposals_for(last, panel):
    out = []
    for provider, model in panel:
        row = last.get((provider, model), {})
        raw_value = (row.get('value') or '').strip()
        sql = (row.get('sql') or '').strip()
        accepted = row.get('verdict') in ('correct', 'incorrect') and bool(sql)
        value = None
        if accepted and raw_value:
            try:
                # Do not guess units or silently round non-integral values.
                value = int(raw_value)
            except ValueError:
                pass
        out.append(SimpleNamespace(provider=provider, model_requested=model,
                                   value=value, verdict='executed' if value is not None else 'error'))
    return out


def outcome(result, reference):
    if not result['consensus']:
        return 'abstain'
    return 'correct' if result['value'] == reference else 'wrong'


def describe_change(a, b):
    if a['outcome'] == b['outcome'] and a['value'] == b['value']:
        return 'No decision change'
    if a['outcome'] == 'abstain' and b['outcome'] != 'abstain':
        return f"3-of-5 reaches quorum with {b['votes']} votes for {b['value']}; 2-of-3 abstained"
    if b['outcome'] == 'abstain':
        return f"3-of-5 abstains (largest count {b['votes']} < 3); 2-of-3 accepted {a['value']}"
    return f"Different accepted values: 2-of-3={a['value']}, 3-of-5={b['value']}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the committed CSV without modifying it",
    )
    args = parser.parse_args()
    vote = load_vote()
    rows = read_csv(TRACES)
    refs = {r['case_id']: int(r['revenue_cents']) for r in read_csv(REFERENCE)}
    result_rows = []
    counts3 = {'correct': 0, 'wrong': 0, 'abstain': 0}
    counts5 = {'correct': 0, 'wrong': 0, 'abstain': 0}
    for case in sorted(refs):
        last = last_rows_for_case(rows, case)
        decisions = []
        for panel, k, counts in [(PANEL3, 2, counts3), (MODELS, 3, counts5)]:
            result = vote(proposals_for(last, panel), k)
            result['outcome'] = outcome(result, refs[case])
            counts[result['outcome']] += 1
            decisions.append(result)
        a, b = decisions
        reason = describe_change(a, b)
        result_rows.append({
            'case_id': case, 'reference_cents': refs[case],
            'panel_2of3_consensus': a['consensus'], 'panel_2of3_value': a['value'],
            'panel_2of3_votes': a['votes'], 'panel_2of3_outcome': a['outcome'],
            'panel_2of3_models': '; '.join(a['models']),
            'panel_3of5_consensus': b['consensus'], 'panel_3of5_value': b['value'],
            'panel_3of5_votes': b['votes'], 'panel_3of5_outcome': b['outcome'],
            'panel_3of5_models': '; '.join(b['models']),
            'decision_change': reason
        })
    if args.check:
        with OUTPUT.open('r', newline='', encoding='utf-8-sig') as f:
            expected = list(csv.DictReader(f))

        buffer = io.StringIO(newline='')
        writer = csv.DictWriter(buffer, fieldnames=list(result_rows[0]))
        writer.writeheader()
        writer.writerows(result_rows)
        buffer.seek(0)
        actual = list(csv.DictReader(buffer))

        if actual != expected:
            raise SystemExit("FAIL: Recomputed results differ from committed CSV.")
        print("PASS: All 20 cases match the committed CSV.")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(result_rows[0]))
            w.writeheader()
            w.writerows(result_rows)
    print('2-of-3:', counts3)
    print('3-of-5:', counts5)
    print('Changed decisions:')
    for row in result_rows:
        if row['decision_change'] != 'No decision change':
            print(' ', row['case_id'], row['decision_change'])
    print('Detailed 20-case CSV:', OUTPUT)


if __name__ == '__main__':
    main()

