"""Build a local, self-contained HTML evidence board from authentic transcript records.
No fabricated responses; fixture demonstrations are explicitly marked as such.
"""
import argparse, hashlib, html, json
from pathlib import Path
from grader import grade
from reference import ROOT, TASK_IDS, solve
from run_eval import digest, extract_text, fingerprints, SYSTEM

STYLE='''
:root {color-scheme:dark;font-family:system-ui,-apple-system,sans-serif;background:#0c1320;color:#e9edf3}
body{max-width:1250px;margin:34px auto;padding:0 22px}h1{font-size:32px}h2{margin-top:40px}
small,.muted{color:#a6b4ca} .warn{color:#ffcf88}.good{color:#8ae6ba}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}@media(max-width:760px){.grid{grid-template-columns:1fr}}
.panel{border:1px solid #31415a;border-radius:12px;padding:18px;background:#131f31;overflow-wrap:anywhere}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px;max-height:530px;overflow:auto;line-height:1.5}
table{width:100%;border-collapse:collapse}td,th{padding:10px;border-bottom:1px solid #31415a;text-align:left;font-size:14px}
.pass{color:#8ae6ba}.fail{color:#ff9c91}.unknown{color:#ffcf88}
code{background:#27354a;padding:2px 5px;border-radius:4px}
blockquote{border-left:4px solid #ffcf88;margin:12px 0;padding:8px 12px;background:#233047}
'''
def esc(x): return html.escape(str(x),quote=True)
def read_review(folder, transcript):
    path=Path(folder)/(transcript.stem+'.review.json')
    if not path.is_file(): return None,'No human scientific review filed'
    try:
        data=json.loads(path.read_text())
        if data.get('transcript_sha256') != hashlib.sha256(transcript.read_bytes()).hexdigest():
            return None,'REVIEW HASH MISMATCH: review cannot be trusted for this transcript'
        return data,None
    except (OSError,ValueError) as ex:return None,'Invalid review: '+str(ex)
def summarize(records):
    lines=[];events=[]
    for path,rec in records:
        tid=rec.get('task'); response=rec.get('raw_response',{})
        if tid not in TASK_IDS:continue
        expected=solve(tid)
        actual_text=extract_text(response) if rec.get('status')=='completed' else ''
        g=grade(tid,actual_text) if actual_text else None
        review, review_error=read_review(path.parent,path)
        rows=[]
        try:actual=json.loads(actual_text)
        except (ValueError,TypeError):actual={}
        if not isinstance(actual,dict):actual={}
        for k,v in expected.items():
            passed=(g or {}).get('checks',{}).get(k)
            marker='pass' if passed else ('fail' if passed is False else 'unknown')
            rows.append(f'<tr><td>{esc(k)}</td><td>{esc(v)}</td><td>{esc(actual.get(k,"[missing]"))}</td><td class="{marker}">{"PASS" if passed else "FAIL" if passed is False else "NOT GRADED"}</td></tr>')
        review_text='<p class="warn">Explanation-level judgment: NOT REVIEWED.</p>'
        if review_error: review_text+=f'<p class="muted">{esc(review_error)}</p>'
        if review:
            label=review.get('primary_label','undecided')
            quote=review.get('exact_quote','')
            review_text=f'<p><b>Human review:</b> {esc(label)}</p><blockquote>{esc(quote)}</blockquote><p>{esc(review.get("scientific_reason",""))}</p>'
            if label=='unsupported_inference_with_local_correct' and review.get('local_all_correct') is True and review.get('scientific_pass') is False and not review.get('task_ambiguous') and not review.get('grader_error') and quote and quote in actual_text:
                events.append((rec.get('requested_model'),tid,path.name,quote))
        lines.append(f'''<section><h2>{esc(tid)} · {esc(rec.get('requested_model'))} · trial {esc(rec.get('trial'))}</h2>
<p class="muted">Completed: {esc(rec.get('finished_at','?'))} | API status: {esc(rec.get('status'))} | structured pass: {esc((g or {}).get('structured_pass','not scored'))}</p>
<div class="grid"><article class="panel"><h3>Ground truth vs model</h3><table><tr><th>Field</th><th>Reference</th><th>Model</th><th>Check</th></tr>{''.join(rows)}</table></article>
<article class="panel"><h3>Model explanation (verbatim)</h3><pre>{esc(actual.get('explanation',actual_text) or '[no output]')}</pre></article></div>
<div class="panel" style="margin-top:12px"><h3>Scientific adjudication</h3>{review_text}</div></section>''')
    return lines,events

def build(folder,out,allow_fixture=False):
    records=[];skipped=[]
    for path in sorted(Path(folder).glob('*.json')):
        try:rec=json.loads(path.read_text())
        except (ValueError,OSError):continue
        if 'request' not in rec:continue
        sealed={k:v for k,v in rec.items() if k!='record_sha256'}
        tid=rec.get('task');valid=(rec.get('record_sha256')==digest(sealed)
            and rec.get('request_sha256')==digest(rec['request'])
            and rec.get('fingerprints')==fingerprints() and tid in TASK_IDS
            and rec.get('requested_model')==rec['request'].get('model'))
        if valid:
            prompt=json.loads((ROOT/'tasks'/f'{tid}.json').read_text())['prompt']
            valid=rec['request'].get('input')==[{'role':'system','content':SYSTEM},{'role':'user','content':prompt}]
        if valid and rec.get('status')=='completed':
            valid=rec.get('http_status')==200 and rec.get('response_sha256')==digest(rec.get('raw_response',{})) and rec['raw_response'].get('status')=='completed'
        if not valid or rec.get('status')!='completed':
            skipped.append(path.name+': invalid/incomplete record');continue
        if rec.get('test_only') and not allow_fixture:
            skipped.append(path.name+': test fixture excluded');continue
        records.append((path,rec))
    lines,events=summarize(records)
    flag='DEMONSTRATION ONLY: SYNTHETIC TEST FIXTURES MAY BE INCLUDED. NOT MODEL EVIDENCE.' if allow_fixture else 'Only transcript records, not authored fixtures; reviewed scientific failures are shown separately.'
    intro='<p class="warn">No eligible completed model transcripts. No evidence of any AI failure is available here.</p>' if not records else ''
    body=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>PHYSICS-GAP evidence board</title><style>{STYLE}</style>
<body><h1>PHYSICS-GAP · evidence board</h1><p>{esc(flag)}</p>{intro}
<div class="panel"><b>Completed included transcripts:</b> {len(records)}<p><b>Human-adjudicated local-correct / global-inference failures:</b> {len(events)}</p>
<p class="muted">Structured answer correctness is not the same as scientific correctness. Screenshot only authentic transcript results for competition claims.</p></div>
{''.join(lines)}<h2>Excluded records</h2><pre>{esc(chr(10).join(skipped) or 'None')}</pre></body></html>'''
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(body)
    return {'included':len(records),'adjudicated_local_correct_global_wrong':len(events),'excluded':skipped,'output':str(out)}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--include-test-fixtures',action='store_true')
    a=p.parse_args();print(json.dumps(build(a.folder,a.out,a.include_test_fixtures),indent=2))
