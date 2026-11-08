"""Deterministic references derived in docs/REFERENCE_SOLUTIONS.md; stdlib only."""
import json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
TASK_IDS=('W_transport','W_geometry','R_calibration','R_search')

def gamma_cdf_integer(k,t):
    if t<=0:return 0.0
    term=t**k/math.factorial(k); total=term
    for j in range(k+1,500):
        term*=t/j; total+=term
        if abs(term)<1e-16*max(total,1e-300):break
    return math.exp(-t)*total

def transport(tau,e0,threshold,beta):
    """Energy-only Poisson slab. Restricted to log(E0/Ecut)<-log(1-beta)."""
    if not (0<=tau<=10 and e0>0 and threshold>0 and 0<beta<1):
        raise ValueError('outside implemented parameter domain')
    cut=threshold/beta
    if cut>e0:return 0.0
    if cut==e0:return math.exp(-tau)
    t=math.log(e0/cut)
    if t>=-math.log1p(-beta):raise ValueError('reference formula requires t < -log(1-beta)')
    p=math.exp(-tau); total=p
    for k in range(1,81):
        p*=tau/k
        total+=p*gamma_cdf_integer(k,t)/beta**k
    return total

def paired_ratio(a,b):
    n=len(a); mean_b=sum(b)/n; r=sum(a)/sum(b)
    se=math.sqrt(sum((x-r*y)**2 for x,y in zip(a,b))/(n*(n-1)*mean_b**2))
    return r,se

def dot(a,b):return sum(x*y for x,y in zip(a,b))

def calibration(shared=True):
    d=[4.,4.,8.,4.,0.,2.];s=[.1,.25,1.,.5,.2,.1];n=len(d)
    # C = 4 I + 4 11^T; Sherman-Morrison inverse.
    def cinv(v):
        return [x/4-sum(v)/(4*(1+n)) for x in v] if shared else [x/8 for x in v]
    cs=cinv(s);den=dot(s,cs);amp=dot(cs,d)/den;se=1/math.sqrt(den)
    residual=[x-amp*y for x,y in zip(d,s)]
    return amp,se,dot(residual,cinv(residual))

def solve(tid):
    if tid=='W_transport':
        beta=4*100*28/128**2;mean=10*math.exp(-2*beta/2)
        return dict(beta=beta,cutoff_keV=5/beta,mean_energy_keV=mean,
                    ballistic=math.exp(-2),stochastic_acceptance=transport(2,10,5,beta),
                    mean_rule_acceptance=0.,mean_rule='invalid_for_tail',
                    transparent_acceptance=transport(0,10,5,beta),earth_claim='not_established')
    if tid=='W_geometry':
        b=[1.]*50+[.8]*40+[1.2]*10
        a=[1.]*50+[1.5]*40+[.5]*10
        f=[1.]*50+[0.]*40+[.5]*10
        p,ps=paired_ratio(a,b);r,rs=paired_ratio(f,b)
        return dict(plane_ratio=p,plane_se=ps,finite_ratio=r,finite_se=rs,
                    finite_upper95=r+1.96*rs,plane_decision='enhancement',
                    finite_decision='suppression',universal_claim='not_established')
    if tid=='R_calibration':
        a,se,q=calibration();_,diag,_=calibration(False)
        return dict(amplitude=a,shared_se=se,diagonal_se=diag,z=a/se,chi2=q,
                    significance='below_threshold',origin='not_identified')
    if tid=='R_search':
        p=9.96e-8
        return dict(global_p=-math.expm1(1000*math.log1p(-p)),
                    unknown_lower=p,unknown_upper=8000*p,
                    block_decision='below_threshold',unknown_decision='undetermined',
                    replication_p=1e-8,replication_decision='meets_threshold',
                    particle_origin='not_identified')
    raise ValueError('unknown task: '+str(tid))

if __name__=='__main__':
    for tid in TASK_IDS:
        (ROOT/'reference'/f'{tid}.json').write_text(json.dumps(solve(tid),indent=2)+'\n')
    print(json.dumps({t:solve(t) for t in TASK_IDS},indent=2))
