# Reference solutions and scope

All four scenarios are synthetic. These derivations are newly written with AI assistance. Different numerical methods check the algebra/computation, not the completeness of the physical model. Independent human scientific review remains outstanding. Values in `reference/*.json` omit the prose field deliberately: they are answer keys, not complete model responses. Complete demonstration responses are in `fixtures/correct/`.

## W_transport: a mean is not a threshold distribution

For stationary-target elastic nonrelativistic scattering, maximum fractional recoil is beta=4mM/(m+M)^2=0.68359375. Isotropy in the center-of-mass frame makes the fractional loss uniform on [0,beta] in this pointlike approximation. Thus Q is uniform on [1-beta,1]. Recoil eligibility is E_exit >= E_cut=5/beta=7.314285714285714 keV. This is not recoil probability: for fixed eligible E the fraction of isotropic recoils exceeding threshold would itself depend on E. That extra response is deliberately excluded.

The Poisson product mean follows from its generating function:
E[E_exit]=E0 E[(1-beta/2)^N]=E0 exp(-tau beta/2)=5.047996051229458 keV.
The mean-energy threshold rule returns 0, since this is below E_cut. However the N=0 atom already contributes exp(-2)=0.1353352832366127, and all those particles are eligible.

For the full probability define Y=-log Q, a=-log(1-beta), and t=log(E0/E_cut). The density is exp(-y)/beta on 0<=y<=a. Here t<a, so the upper truncation cannot cut the integration simplex sum(Y_i)<=t. Conditional on N=k>=1:

P(E_exit>=E_cut | N=k) = [integral_0^t exp(-y)y^(k-1)/(k-1)! dy] / beta^k.

This is the integer-gamma CDF divided by beta^k. Add the k=0 atom and mix with Poisson(2). The result is **0.2671527383902417**. The reference sums through k=80; the uncomputed Poisson mass is below 5.8e-98, an upper bound on any probability truncation error. The public function refuses parameter regions outside its implemented t<a derivation rather than silently extending it. At tau=0 the exact eligibility is 1. The mean formula is exact for the mean within this surrogate, while applying a nonlinear threshold to that mean is invalid for the desired tail.

Independent methods: direct numerical quadrature of the log-loss simplex and 300,000 seeded Poisson/uniform product histories. The latter gives 80,058 eligible histories, or 0.26686, consistent with the reference sampling SE 0.00080784. This Monte Carlo agreement is evidence about this surrogate only.

A real Earth calculation needs the incident velocity/angular distribution, depth/chord geometry, composition and density profile, differential and energy-dependent scattering, changes in directions and path lengths, boundaries/backscattering, detector geometry and response, source-area convergence, and uncertainty/convergence checks. Gravity, nuclear form factors and other effects require domain-specific justification rather than automatic inclusion or exclusion. Neither this surrogate nor the original fixture rates establish experimental viability.

## W_geometry: score ratios, paired uncertainty and aperture

Totals are sum(B)=94, sum(A)=115, sum(F)=55. Ratios are 1.2234042553191489 and 0.5851063829787234. These are weighted response ratios for the stipulated source ensemble. They are not arrival fractions and need not be <=1.

Let r=mean(X)/mean(B). The paired delta-method variance estimate is

SE(r)^2 = [sum_i (X_i-r B_i)^2] / [n(n-1) mean(B)^2].

It follows by propagating the full two-variable sample covariance, or equivalently linearizing each paired history. The residual mean is zero at the fitted ratio. Expanding the row counts gives n=100, rather than three sampling units. The plane SE is 0.0509819759630599 and the finite SE is 0.04508320554175195. Plane interval approximately [1.12348,1.32333] supports enhancement in plane scores for this ensemble. Finite interval approximately [0.49674,0.67347] supports suppression for the aperture. These positive and negative conclusions are both part of the answer; rejecting everything is wrong.

Independent checks: NumPy covariance propagation and paired nonparametric bootstrap (20,000 resamples). The bootstrap is a sampling diagnostic, not an exact proof of nominal 95% coverage. The normal and delta approximations are specified by the task; they are not universally reliable at small counts or near-zero denominators.

All initial footprints are inside the aperture. Out-scattered trajectories can be lost but in-scattering from outside this source region is absent. This is a conditional diagnostic, not a full uniform-flux detector prediction. To extrapolate, increase the launch region, include outside histories with proper area and angular flux normalization, and demonstrate convergence of detector scores. No universal conclusion or actual sensitivity follows from these records.

## R_calibration: marginalizing a shared calibration error

The specified subtraction gives d=[4,4,8,4,0,2]. With B=100 and sigma_delta=0.02, C=4 I+4 11^T, not 8 I. Its eigenvalues are 28 along the common direction and 4 in the other five directions. C^-1=(1/4)[I-11^T/7]. This is a marginal Gaussian model under a known external calibration distribution; treating delta as a freely fitted intercept is a different model.

For a single unconstrained amplitude,
a_hat=(s^T C^-1 d)/(s^T C^-1 s), SE=(s^T C^-1 s)^(-1/2).
This gives a_hat=6.800401203610833, SE=2.369989567836737 and z=2.8693802267737647. The residual quadratic form is 3.4809428284854564. Under the stipulated model it has five degrees of freedom because one amplitude was fitted to six Gaussian observations with known covariance. No covariance parameters were estimated from these data.

Replacing C by diag(C)=8 I and refitting gives SE=2.4142865611338276. Here the incorrect diagonal replacement actually makes the amplitude SE slightly larger. Correlation does not always increase the uncertainty on a shaped contrast: this template carries information in directions with less shared noise. Saying shared error must always inflate this SE is wrong. Numerical check: Cholesky whitening and an independent least-squares solve reproduce amplitude, SE and residual statistic.

The fixed-template statistic is below the predefined z=5 threshold. A positive residual, acceptable residual fit, or even a highly significant excess does not uniquely identify a particle. The specified gain/noise distribution must be independently validated, and instrumental controls, injection/recovery, nuisance robustness and relevant alternative signal hypotheses are needed. No real RELIC performance or measurement is claimed.

## R_search: dependence and a positive replication control

Eight identical cells form one effective test, so there are 1000 independent block tests. Under the stated global null,
p_global=1-(1-9.96e-8)^1000=9.95950450442569e-5,
computed stably by -expm1(1000 log1p(-p)). A 60-digit Decimal power independently checks the value. This is above 2.87e-7 and fails the significance criterion. Treating all 8000 cells as independent or treating the selected cell as preregistered would both be wrong for this part.

With only identical marginal probabilities and no dependence knowledge, the sharp union bounds are p<=P(union)<=min(8000p,1). Numerically these are 9.96e-8 and 0.0007968. Identical events attain the lower bound; disjoint events can attain the upper bound here. They straddle the criterion, so the unknown-dependence case is undetermined. One may give a conservative upper bound, but cannot infer the exact decision from it alone.

The independent preregistered replication has one test and p_rep=1e-8. By itself it meets the specified criterion. There is no extra factor of 8000 for this new, independent, prespecified test. This does not identify a particle origin: it rejects its stipulated null, conditional on correct calibration and the stated absence of selection. Causation and physical attribution still require discriminatory controls. No combined discovery/replication p-value is requested or justified by multiplication without a defined combination test.
