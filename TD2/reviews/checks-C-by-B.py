"""Offline Pair C checks, independent of Pair A's unfinished implementation."""
import csv
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def main():
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    with (ROOT / 'TD1/results/traces-td1.csv').open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    latest = {}
    for row in rows:
        latest[(row['provider'], row['model_requested'], row['case_id'])] = row
    assert len(latest) == 100
    models = sorted({(p, m) for p, m, _ in latest})
    families = {'F1': ['C01','C04','C05','C06','C07','C20'], 'F3': ['C03','C12','C13','C14'],
                'F2': ['C02','C08','C09','C11'], 'F2b': ['C10'],
                'F2+F1/F3': ['C15','C16','C17','C19'], 'F2b+F1': ['C18']}
    expected = {
        'cohere/north-mini-code:free': ['6/6','4/4','0/4','0/1','2/4','0/1'],
        'dots-studio/dots-3-note-preview:free': ['6/6','4/4','2/4','0/1','3/4','0/1'],
        'openai/gpt-oss-20b': ['6/6','4/4','1/4','1/1','4/4','1/1'],
        'openai/gpt-oss-120b': ['6/6','4/4','4/4','1/1','4/4','1/1'],
        'qwen/qwen3.8-27b': ['6/6','4/4','3/4','0/1','1/4','1/1'],
    }
    rates = {}
    for index, (family, cases) in enumerate(families.items()):
        rates[family] = {}
        for provider, model in models:
            rate = f"{sum(latest[(provider, model, c)]['verdict'] == 'correct' for c in cases)}/{len(cases)}"
            assert rate == expected[model][index], (family, model, rate)
            rates[family][model] = rate
    routing = []
    for script, saved in [('atelier-routage.py', 'output-before.jsonl'),
                           ('atelier-routage-adapted.py', 'output-after.jsonl')]:
        result = subprocess.run([sys.executable, str(ROOT / 'TD2/pair-C' / script)], cwd=ROOT,
                                capture_output=True, text=True, encoding='utf-8')
        assert result.returncode == 0, result.stderr
        actual = [json.loads(line) for line in result.stdout.splitlines()]
        stored = [json.loads(line) for line in (ROOT / 'TD2/pair-C' / saved).read_text().splitlines()]
        assert actual == stored
        routing.append(dict(script=script, scenarios=len(actual), saved_output_matches=True, results=actual))
    amount = (650 * 0.15 + 300 * 0.60) / 1e6
    assert round(amount, 6) == 0.000278
    evidence = dict(reviewed_commit=commit, source_attempt_rows=len(rows), final_cells=len(latest),
                    rates=rates, routing=routing, urgent_simulated_usd=amount,
                    paid_reason_has_explicit_case_ids=any('C0' in item['result']['reason'] for item in routing[1]['results'] if item['scenario'] == 'urgent'))
    (HERE / 'checks-C-by-B.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    print('PASS: all 30 rates, 7 before / 9 after scenarios and simulated urgent cost.')

if __name__ == '__main__':
    main()
