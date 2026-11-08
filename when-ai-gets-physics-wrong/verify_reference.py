"""Independent numerical methods; requires NumPy and SciPy. NOT model inference."""
import json, math, platform
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.stats import poisson
from reference import ROOT, solve

def verify():
    checks={}; details={}
    beta=4*100*28/128**2;t=math.log(10/(5/beta))
    quadrature=math.exp(-2)
    for k in range(1,40):
        # Integrate a simplex volume in log-loss space instead of the reference's gamma series.
        integral,err=quad(lambda y:math.exp(-y)*y**(k-1)/math.factorial(k-1)/beta**k,0,t,epsabs=1e-13)
        quadrature+=math.exp(-2)*2**k/math.factorial(k)*integral
    expected=solve('W_transport')['stochastic_acceptance']
    checks['transport_quadrature']=abs(quadrature-expected)<1e-12
    rng=np.random.default_rng(20261107);n=300000
    collisions=rng.poisson(2,n);energies=np.full(n,10.)
    for j in range(int(collisions.max())):
        active=collisions>j;energies[active]*=rng.uniform(1-beta,1,int(active.sum()))
    accepted=int(np.sum(beta*energies>=5));mc=accepted/n;se=math.sqrt(expected*(1-expected)/n)
    checks['transport_seeded_mc']=abs(mc-expected)<5*se
    details['transport']={'quadrature':quadrature,'reference':expected,'mc_n':n,'mc_seed':20261107,
                          'mc_eligible':accepted,'mc_fraction':mc,'mc_sampling_se':se,
                          'poisson_tail_after_80':float(poisson.sf(80,2))}
    B=np.repeat([1,.8,1.2],[50,40,10]);A=np.repeat([1,1.5,.5],[50,40,10]);F=np.repeat([1,0,.5],[50,40,10])
    for name,vec in [('plane',A),('finite',F)]:
        cov=np.cov(np.array([vec,B]),ddof=1);r=vec.mean()/B.mean()
        gradient=np.array([1/B.mean(),-vec.mean()/B.mean()**2])
        se_np=float(np.sqrt(gradient@cov@gradient/len(B)))
        checks[f'{name}_paired_covariance']=abs(se_np-solve('W_geometry')[name+'_se'])<1e-12
        idx=rng.integers(0,100,(20000,100));ratios=vec[idx].mean(axis=1)/B[idx].mean(axis=1)
        boot=float(ratios.std(ddof=1));checks[f'{name}_bootstrap']=abs(boot/se_np-1)<.04
        details[name]={'numpy_delta_se':se_np,'paired_bootstrap_se':boot,'bootstrap_resamples':20000}
    d=np.array([4,4,8,4,0,2]);s=np.array([.1,.25,1,.5,.2,.1]);C=4*np.eye(6)+4*np.ones((6,6))
    L=np.linalg.cholesky(C);sw=np.linalg.solve(L,s);dw=np.linalg.solve(L,d)
    fit=np.linalg.lstsq(sw[:,None],dw,rcond=None)[0][0];se_np=1/np.linalg.norm(sw)
    chi=float(np.sum((dw-fit*sw)**2));ref=solve('R_calibration')
    checks['calibration_whitened_lstsq']=abs(fit-ref['amplitude'])<1e-12 and abs(se_np-ref['shared_se'])<1e-12 and abs(chi-ref['chi2'])<1e-12
    diag=1/np.sqrt(np.sum(s*s/np.diag(C)));checks['calibration_diagonal']=abs(diag-ref['diagonal_se'])<1e-12
    details['calibration']={'whitened_amplitude':float(fit),'whitened_se':float(se_np),'chi2':chi,'diagonal_se':float(diag),'covariance_eigenvalues':np.linalg.eigvalsh(C).tolist()}
    # Independent high-precision decimal power rather than logarithmic reference.
    from decimal import Decimal,localcontext
    with localcontext() as ctx:
        ctx.prec=60;global_p=float(1-(1-Decimal('9.96e-8'))**1000)
    checks['search_decimal']=abs(global_p-solve('R_search')['global_p'])<1e-16
    details['search']={'decimal_global_p':global_p}
    for tid in ('W_transport','W_geometry','R_calibration','R_search'):
        stored=json.loads((ROOT/'reference'/f'{tid}.json').read_text())
        checks[tid+'_frozen_reference']=stored==solve(tid)
    checks={k:bool(v) for k,v in checks.items()}
    result={'kind':'reference_verification_not_model_results','python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'checks':checks,'details':details,'all_passed':all(checks.values())}
    (ROOT/'results'/'reference_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if not result['all_passed']:raise SystemExit(1)

if __name__=='__main__':verify()
