"""Consolidate experiment logs; no network calls or changes to raw traces."""
import csv
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent
kit = root.parent / 'kit-td1'
def read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))
def write(name, fields, rows):
    target=root/name
    try:
        f=target.open('w',encoding='utf-8',newline='')
    except PermissionError:
        target=target.with_stem(target.stem+'-reviewed')
        f=target.open('w',encoding='utf-8',newline='')
        print(f'Original file locked; saved {target.name}')
    with f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    return target.name

causes = {
 'A': dict.fromkeys(['C15','C17','C19'],'Exact birthday equality selects only customers born on 2001-09-25 instead of the full completed-age-25 birth interval.'),
 'B': {'C02':'Birth interval is 2025-09-25 to 2026-09-25, not the interval for completed age 25.', 'C08':'Birth filter spans only 2001-09-23 to 2001-09-24 rather than the full year-long age interval.', 'C11':'Birth interval is after 2001-12-01 through 2006-12-01; correct interval is after 2000-12-01 through 2001-12-01.'},
 'C': {'C02':'Incorrect upper birth bound admits younger customers; also adds an unrequested one-day order filter.', 'C08':'Incorrect age interval and an unrequested restriction around the reference day.', 'C09':'Uses birth year itself minus birthday adjustment as age, omitting subtraction from reference year.', 'C11':'Boolean date predicate admits all supplied customers; does not calculate age 25.', 'C15':'Contradictory month-day tests compare a birthday with the same month-day one year later, eliminating matches.', 'C16':'Opposing inclusive bounds collapse the birth interval to exactly 2001-09-25.', 'C17':'Upper birth bound is the reference date rather than reference date minus 25 years, admitting younger customers.', 'C19':'Month/day CASE expression filters birthdays without enforcing age 25.'},
 'D': {'C09':'Uses order date rather than reference date and requires the same month-day to be both >= and < the birthday.', 'C15':'Month-day must be both <= and > 09-25; contradictory filters omit birth-year calculation.', 'C17':'Birthday boundaries are reversed at equality: includes 2000-09-25 and excludes 2001-09-25.', 'C19':'Compares four-digit year strings with full date strings and does not enforce exact completed age.', 'C18':'Output-token-per-minute HTTP 429 on both permitted attempts; no model SQL received.'},
 'E': {'C02':'Exact birthday equality instead of a full completed-age interval.', 'C08':'Malformed CAST expression; SQLite rejects the SQL syntax.', 'C09':'Exact birthday equality instead of a full completed-age interval.', 'C10':'Year difference 25 plus birthday passed omits customers with year difference 26 whose birthday is still upcoming.', 'C11':'Selects only one birthday and adds an unrequested one-day order filter.', 'C15':'Year difference 25 plus birthday passed omits still-25 customers born in the preceding year.', 'C16':'Malformed numeric date arithmetic multiplies encoded birth dates by 10000; predicate does not calculate completed age.', 'C17':'Year difference 25 plus birthday passed omits still-25 customers born in the preceding year.', 'C18':'Year difference 25 plus birthday passed omits still-25 customers born in the preceding year.', 'C19':'Exact birthday equality instead of a full completed-age interval.'}
}
questions=json.loads((kit/'questions-td1.json').read_text())['questions']
qmap={q['id']:q for q in questions}
raw=[]; comparison=[]; batches={}; latest_by_batch={}
for batch in 'ABCDE':
    records=[json.loads(line) for line in (root/f'state-{batch}.jsonl').read_text().splitlines() if line.strip()]
    batches[batch]=records
    latest={}
    for row in records:
        raw.append(row)
        old=latest.get(row['case_id'])
        assert old is None or row['attempts']>old['attempts'], 'Duplicate/reset attempt counter'
        latest[row['case_id']]=row
    assert set(latest)==set(qmap)
    latest_by_batch[batch]=latest
    for case,row in sorted(latest.items()):
        explanation=causes[batch].get(case,'Executed read-only SQL matches the computed reference; numerical agreement does not prove the query correct on other datasets.')
        if row['attempts']>1:
            explanation += ' Final attempt follows an earlier recorded access/rate-limit failure.'
        comparison.append(dict(case_id=case,model_id=row['model_requested'],trace_file=f'traces-{batch}.csv',cell_id=row['cell_id'],nature=row['nature'],status=row['verdict'],value_cents=row['value'],reference_cents=row['reference'],explanation=explanation))
fields=list(raw[0])
write('traces-td1.csv',fields,raw)
write('model-question-comparison-en.csv',list(comparison[0]),comparison)
assert len(comparison)==100 and len({(r['case_id'],r['model_id']) for r in comparison})==100
for case in qmap:
    assert len({r['prompt_sha256'] for r in raw if r['case_id']==case})==1, 'Prompt mismatch'

portfolio=read(kit/'portefeuille-modeles-2026-09-28.csv')
summary=[]
source='../kit-td1/portefeuille-modeles-2026-09-28.csv (course snapshot; not live-verified)'
def family(q):
    t=q['type']
    return 'combined' if '+' in t else 'period' if t=='period' else 'product' if t=='product list' else 'age'
for batch,latest in latest_by_batch.items():
    sample=next(iter(latest.values())); model=sample['model_requested']
    entries=[p for p in portfolio if p['identifiant_gate']==model]
    paid=next((p for p in entries if p['acces']=='payant'),None)
    score=next((p['score_public'] for p in entries if p['score_public']),None)
    r=dict(provider=sample['provider'],model_id=model,public_index=score or 'N/A',index_date='2026-09-28' if score else 'N/A',index_source=source if score else 'N/A: exact model absent from supplied snapshot',paid_route_same_model=(paid['gate']+':'+model) if paid else 'N/A: no paid route documented in supplied snapshot',input_usd_per_million=paid['prix_entree_usd_m'] if paid else 'N/A',output_usd_per_million=paid['prix_sortie_usd_m'] if paid else 'N/A',price_date='2026-09-29' if paid else 'N/A',price_source=source+'; portfolio guide Sources: prices re-read 2026-09-29' if paid else 'N/A: no documented exact-model paid route',access_used=sample['provider']+' Free',trace_files=f'traces-{batch}.csv; state-{batch}.jsonl',limits='One small batch; reference peer/instructor validation pending; historical portfolio metadata only. '+('C and E used the same personal account, contrary to prescribed allocation.' if batch in 'CE' else ''))
    for f in ['period','age','product','combined']:
        selected=[latest[q['id']] for q in questions if family(q)==f]
        r[f+'_results']=f"{sum(x['verdict']=='correct' for x in selected)}/{len(selected)} correct; {sum(x['verdict']=='not_executed' for x in selected)} not executed"
    summary.append(r)
summary_fields=list(read(kit/'five-model-summary-en.csv')[0])
summary_name=write('five-model-summary-en.csv',summary_fields,summary)

lines=['# TD 1 comparison view','','Derived from the long comparison CSV; one final result per cell.','', '| Model | '+' | '.join(qmap)+' |','|---|'+'---|'*20]
for batch,latest in latest_by_batch.items():
    labels={'correct':'OK','incorrect':'WRONG','sql_invalid':'SQL','not_executed':'429'}
    lines.append('| '+next(iter(latest.values()))['model_requested']+' | '+' | '.join(labels.get(latest[c]['verdict'],latest[c]['verdict']) for c in qmap)+' |')
(root/'comparison-view.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

sys.path.insert(0,str(kit))
spec=importlib.util.spec_from_file_location('td1_runner',kit/'skeleton-multi-llm-en.py')
module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module)
system,user,_=module.build_prompt((kit/'schema.sql').read_text(),'{QUESTION}')
(root/'prompt-used.md').write_text('# Prompt used\n\n## System\n\n```text\n'+system+'\n```\n\n## User template\n\n```text\n'+user+'\n```\n\nThe question placeholder is replaced with the exact question text. Each question has one shared fingerprint across all five models. No prompt edits were made during these runs.\n',encoding='utf-8')

reports=root.parent/'reports'; reports.mkdir(exist_ok=True)
counts=Counter(r['status'] for r in comparison)
statuses=Counter(str(r['http_status']) for r in raw)
attempt2=sum(r['attempts']==2 for r in raw)
report=f'''# TD 1 — Model comparison

Date: 21 October 2026. Review draft: member names/contributions, independent peer validation and instructor validation remain to be completed.

## Method and evidence

Twenty reference queries were executed read-only on the supplied database and cross-checked by a separate CSV iteration. Both implementations share case definitions; an independent group member must still review their interpretation. See [references](../td1/reference-td1.csv), [cross-check](../td1/reference-crosscheck.json), and [notes](../td1/reference-notes.md).

Five models received the same prompt per question. All observed attempts have nature `real`; no simulation or replay is included. See the [prompt](../td1/prompt-used.md), [all raw attempts](../td1/traces-td1.csv), [100 final comparisons](../td1/model-question-comparison-en.csv), [five-model summary](../td1/{summary_name}) and [comparison view](../td1/comparison-view.md). Original CSV and JSONL logs for A–E are retained in td1.

## Results

| Batch | Model | Correct / planned |
|---|---|---|
| A | GPT-OSS 120B | 17/20 |
| B | GPT-OSS 20B | 17/20 |
| C | Cohere North Mini Code | 12/20 |
| D | Qwen 3.8 27B | 15/20 |
| E | Dots 3 Note Preview | 10/20 |

Final cells: {dict(counts)}. Of 100 planned cells, 99 received model output, 98 executed SQL successfully, and 71 matched the reference. Dots C08 had invalid SQL. Qwen C18 remained blocked by HTTP 429 on both allowed attempts. Access failures are separate from wrong numerical answers.

All five models answered the six pure-period and four product-family cases correctly (the product family includes cases combining products with periods, as classified in the supplied question JSON). Failures concentrate in age and combined questions: exact-birthday equality, wrong birth intervals, omitted completed-age cases, contradictory predicates, or unrequested order-date filters. The comparison CSV gives an evidence-based explanation for each final failure. This is a hypothesis about this batch, not a general ranking.

For example, A/C15 uses `c.birth_date = date('2026-09-25', '-25 years')`, selecting one birthday instead of all age-25 customers. E/C08 contains malformed CAST syntax. The original SQL remains unchanged in the raw traces.

## Access, attempts and missing measurements

There are {len(raw)} recorded batch attempts: 100 initial calls and {attempt2} second attempts. HTTP status counts: {dict(statuses)}. A initially had 17 HTTP 403 failures and two HTTP 401 failures; C18 succeeded before the other cells were recovered. D recorded five HTTP 429 responses across four cells. All originals and retries remain in the same state files, with a maximum of two attempts per cell. Setup checks are additional calls and are not included in these batch totals; the full setup-call count and before/after account allowances were not recorded and must not be invented.

Missing token/cost measurements remain blank in raw logs. Free-route access does not establish a paid-route price. Model metadata in the summary comes only from the dated course portfolio: it is not a live price check. N/A entries mean the supplied snapshot does not document the exact model/paid route; they do not assert that no paid route exists.

## Assistance, contributions and protocol deviations

The user ran all five batches locally. Batches C and E used the same personal OpenRouter account, rather than two different members' accounts required by the protocol. No exception or instructor approval is claimed. Group membership, named contributions and instructor disposition of this deviation remain pending.

Codex drafted reference queries, the CSV cross-check, launcher, consolidation, explanations and this report. The user must review and explain them. Reference values were obtained through SQL execution, not adopted from model numerical answers.

The supplied runner was modified to add explicit `--retry-access` for repaired access failures, preserving original traces and the two-attempt cap, and `--stop-on-access-error` to stop a batch after a new access failure. The launcher trims key input and reuses process environment variables. Prompts, output caps, temperature, sandbox and reference values were unchanged. The explicit recovery of previously terminal access failures is documented here; it is not an automatic retry of every HTTP 403.

## Remaining work and TD 2 hypothesis

- Obtain independent peer and instructor reference validation.
- Add actual group members/contributions and any instructor decision on allocation/recovery deviations.
- Record any available account allowance evidence; acknowledge unavailable records.
- Review historical index/price metadata and any required current exact-model sources before submission.
- Present the comparison view and explain selected traces. No further retries of exhausted cells are planned.
- For TD 2, test a routing hypothesis that simple date/product queries need less model capacity, while age questions need explicit completed-age checks. Correctness on this dataset alone does not establish reliable generalisation.
- Publish code, prompts, evidence and this report in the subgroup public repository, then submit the repository URL, full commit hash and report permalink through Moodle. Due 25 October 2026 at 23:59 Paris time. No publication or submission has been performed.
'''
(reports/'td1.md').write_text(report,encoding='utf-8')
print(json.dumps({'raw_attempts':len(raw),'final_cells':len(comparison),'final_statuses':dict(counts),'second_attempts':attempt2,'http_statuses':dict(statuses),'shared_fingerprints':'20/20'},indent=2))
