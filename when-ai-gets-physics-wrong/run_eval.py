"""Independent-context OpenAI Responses calls and transcript replay; no oracle in requests."""
import argparse, datetime, hashlib, json, os, re, time, urllib.request, urllib.error
from pathlib import Path
from grader import grade
from reference import ROOT,TASK_IDS
SYSTEM='You are a scientific analyst. Solve the supplied problem from its stated assumptions. Return the requested JSON object including your derivation and limitations in the explanation field.'

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,allow_nan=False).encode()).hexdigest()
def fingerprints():
    paths=[ROOT/'grader.py',ROOT/'reference.py',ROOT/'run_eval.py',*sorted((ROOT/'tasks').glob('*.json')),*sorted((ROOT/'reference').glob('*.json'))]
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def extract_text(response):
    return ''.join(c.get('text','') for o in response.get('output',[]) if o.get('type')=='message'
                   for c in o.get('content',[]) if c.get('type')=='output_text')

def api_transport(payload):
    key=os.environ.get('OPENAI_API_KEY')
    if not key:raise RuntimeError('OPENAI_API_KEY not configured; no inference attempted')
    request=urllib.request.Request('https://api.openai.com/v1/responses',data=json.dumps(payload).encode(),
            headers={'Content-Type':'application/json','Authorization':'Bearer '+key},method='POST')
    try:
        with urllib.request.urlopen(request,timeout=300) as h:
            return h.status,json.loads(h.read())
    except urllib.error.HTTPError as e:
        body=e.read().decode(errors='replace')
        try:body=json.loads(body)
        except ValueError:body={'unparsed_http_error':body}
        return e.code,body

def run_trial(task_id,trial,model,outdir,transport=api_transport,test_only=False,reasoning_effort=None,max_output_tokens=8192):
    prompt=json.loads((ROOT/'tasks'/f'{task_id}.json').read_text())['prompt']
    payload={'model':model,'input':[{'role':'system','content':SYSTEM},{'role':'user','content':prompt}],
             'max_output_tokens':max_output_tokens,'store':False}
    if reasoning_effort:payload['reasoning']={'effort':reasoning_effort}
    outdir.mkdir(parents=True,exist_ok=True)
    safe_model=re.sub(r'[^A-Za-z0-9_.-]','_',model)
    path=outdir/f'{safe_model}__{task_id}__{trial:03d}.json'
    rec={'task':task_id,'trial':trial,'requested_model':model,'test_only':test_only,'started_at':now(),
         'request':payload,'request_sha256':digest(payload),'fingerprints':fingerprints(),'status':'started',
         'settings_note':'Unspecified generation parameters use provider defaults; no seed or previous-response context. Hidden internal reasoning is not exposed by the API.'}
    with path.open('x') as h:json.dump(rec,h,indent=2)
    start=time.monotonic()
    try:
        code,response=transport(payload)
        rec.update(http_status=code,raw_response=response,response_sha256=digest(response))
        rec['status']='completed' if code==200 and response.get('status')=='completed' else 'api_error_or_incomplete'
        rec['returned_model']=response.get('model');rec['usage']=response.get('usage')
        if rec['status']=='completed':
            rec['output_text']=extract_text(response)
            try:rec['grade']=grade(task_id,rec['output_text'])
            except Exception as e:
                rec['status']='grader_error'
                rec['grading_error']=type(e).__name__+': '+str(e)
    except Exception as e:
        # Preserve transport failure separately from scientific performance. Never save headers/credentials.
        rec.update(status='transport_error',error_type=type(e).__name__,error_message=str(e))
    rec.update(finished_at=now(),latency_seconds=time.monotonic()-start)
    rec['record_sha256']=digest(rec)
    path.write_text(json.dumps(rec,indent=2,allow_nan=False)+'\n')
    return path

def replay(folder):
    result={'eligible_model_trials':0,'test_fixture_trials':0,'api_errors':0,'integrity_errors':0,
            'grader_errors':0,'format_errors':0,'structured_passes':0,'structured_failures':0,'scientific_passes':None,'rows':[]}
    for path in sorted(Path(folder).glob('*.json')):
        rec=json.loads(path.read_text())
        if 'request' not in rec:continue
        row={'file':path.name,'task':rec['task'],'trial':rec['trial'],'test_only':rec.get('test_only',False),'status':rec['status']}
        sealed={k:v for k,v in rec.items() if k!='record_sha256'}
        valid=(rec.get('record_sha256')==digest(sealed) and rec.get('request_sha256')==digest(rec['request']) and rec.get('fingerprints')==fingerprints())
        tid=rec.get('task')
        valid=valid and tid in TASK_IDS and rec.get('requested_model')==rec['request'].get('model')
        if valid:
            expected_prompt=json.loads((ROOT/'tasks'/f'{tid}.json').read_text())['prompt']
            valid=rec['request'].get('input')==[{'role':'system','content':SYSTEM},{'role':'user','content':expected_prompt}]
        if rec.get('status')=='completed':
            valid=valid and rec.get('http_status')==200 and rec.get('raw_response',{}).get('status')=='completed'
        if 'raw_response' in rec:valid=valid and rec.get('response_sha256')==digest(rec['raw_response'])
        if not valid:result['integrity_errors']+=1;row['status']='integrity_error'
        elif rec['status']=='grader_error':result['grader_errors']+=1
        elif rec['status']!='completed':result['api_errors']+=1
        elif rec.get('test_only'):result['test_fixture_trials']+=1
        else:
            result['eligible_model_trials']+=1
            g=grade(rec['task'],extract_text(rec['raw_response']));row['grade']=g
            if g['status']=='format_error':result['format_errors']+=1
            elif g['structured_pass']:result['structured_passes']+=1
            else:result['structured_failures']+=1
        result['rows'].append(row)
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='command',required=True)
    run=sub.add_parser('run');run.add_argument('--model',required=True);run.add_argument('--trials',type=int,default=3)
    run.add_argument('--task',choices=TASK_IDS,action='append');run.add_argument('--out',type=Path,required=True)
    run.add_argument('--reasoning-effort');run.add_argument('--max-output-tokens',type=int,default=8192)
    rp=sub.add_parser('replay');rp.add_argument('folder',type=Path);rp.add_argument('--out',type=Path)
    args=ap.parse_args()
    if args.command=='run':
        if args.trials<1:ap.error('--trials must be >=1')
        if not os.environ.get('OPENAI_API_KEY'):
            raise SystemExit('BLOCKED: OPENAI_API_KEY is absent. Zero model calls made. Configure a credential in environment settings, not in chat.')
        for trial in range(1,args.trials+1):
            for tid in args.task or TASK_IDS:
                p=run_trial(tid,trial,args.model,args.out,reasoning_effort=args.reasoning_effort,max_output_tokens=args.max_output_tokens)
                print(p,flush=True)
    else:
        result=replay(args.folder);text=json.dumps(result,indent=2)
        if args.out:args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(text+'\n')
        print(text)
