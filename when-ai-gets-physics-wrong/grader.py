"""Structured grading only. Scientific explanation always needs manual adjudication."""
import json, math, sys
from pathlib import Path
from reference import ROOT, solve
INFERENCE={'mean_rule','earth_claim','plane_decision','finite_decision','universal_claim',
           'significance','origin','block_decision','unknown_decision','replication_decision','particle_origin'}

def tolerance(v):return max(1e-10,abs(v)*.002)

def no_duplicates(pairs):
    obj={}
    for k,v in pairs:
        if k in obj:raise ValueError('duplicate key: '+k)
        obj[k]=v
    return obj

def reject_constant(s):raise ValueError('nonfinite JSON: '+s)

def grade(task_id,response):
    expected=solve(task_id)
    try:
        obj=json.loads(response,object_pairs_hook=no_duplicates,parse_constant=reject_constant) if isinstance(response,str) else response
        if not isinstance(obj,dict):raise ValueError('response must be an object')
        if not set(expected)<=set(obj):raise ValueError('missing required answer fields')
        for k,v in expected.items():
            x=obj[k]
            if type(v) in (int,float):
                if type(x) not in (int,float) or not math.isfinite(x):raise ValueError('finite JSON number required: '+k)
            elif not isinstance(x,str):raise ValueError('decision string required: '+k)
        if not isinstance(obj.get('explanation'),str) or not obj['explanation'].strip():
            raise ValueError('nonempty explanation required')
    except (ValueError,TypeError,RecursionError,OverflowError) as e:
        return dict(status='format_error',structured_pass=False,scientific_pass=None,
                    review_status='pending',reason=str(e))
    checks={}
    for k,v in expected.items():
        x=obj[k]
        if type(v) in (int,float):
            checks[k]=type(x) in (int,float) and math.isfinite(x) and abs(x-v)<=tolerance(v)
        else: checks[k]=isinstance(x,str) and x.strip().casefold()==v.casefold()
    groups={g:[checks[k] for k in checks if (k in INFERENCE)==(g=='inference')] for g in ('local','inference')}
    return dict(status='graded',structured_pass=all(checks.values()),checks=checks,
                scores={g:sum(v)/len(v) for g,v in groups.items()},scientific_pass=None,
                review_status='pending',extra_fields=sorted(set(obj)-set(expected)-{'explanation'}))

if __name__=='__main__':
    result=grade(sys.argv[1],Path(sys.argv[2]).read_text())
    print(json.dumps(result,indent=2,allow_nan=False))
    sys.exit(0 if result['structured_pass'] else 1)
