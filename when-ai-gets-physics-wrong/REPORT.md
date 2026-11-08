# Evaluation report: where the reasoning breaks

## Hypothesis

A model may know the correct scientific framework while losing numerical consistency in multi-step calculations, even when numerical outputs influence an inference decision.

## Experimental setup

Four frozen synthetic scientific tasks, one OpenAI Responses API model (`gpt-5.2`, returned `gpt-5.2-2025-12-11`), three independent-context trials per task, no Python calculator or file-execution tools supplied to the model. Strict grader, fixed numeric tolerance `max(1e-10, 0.2% * reference magnitude)`; original transcripts retained unchanged. The WIMP simulation is separate, pre-existing scientific work and is not itself a tested full coding task here.

## Observed results

| Task | Pass | Structured fail | Format fail |
|---|---:|---:|---:|
| W_transport | 0 | 2 | 1 |
| W_geometry | 0 | 3 | 0 |
| R_calibration | 0 | 3 | 0 |
| R_search | 3 | 0 | 0 |
| **Total** | **3** | **8** | **1** |

A strict structured pass is not the same as manual scientific approval. Scientific adjudication remains pending in all preserved trial records.

## Reproducible example 1: geometry

In `W_geometry` trial 1, the model gives totals `sum(A)=115` and `sum(B)=94`, then writes `115/94=1.12`. Direct division gives **1.2234042553191489**. In the specified paired delta-method uncertainty framework, this can reverse the interpretation of the nominal 95% interval at unity. See `reference/W_geometry.json` for graded values and the exact model explanation in the named transcript. This is an **internal arithmetic contradiction**, independently verifiable without trusting a model judge.

## Reproducible example 2: stochastic energy-loss distribution

`W_transport` requires the probability that the product of random retained energy fractions remains above threshold, explicitly including the zero-collision Poisson atom. The reference yields **0.2671527383902417**. The mean-energy rule yields zero eligibility, illustrating why a mean cannot replace a threshold distribution. Two evaluated trials fail the structured check; one trial contains Markdown-fenced JSON and is classified only as a **format error** by the strict grader (its physical content may be examined separately without changing the recorded outcome).

## Reproducible example 3: shared calibration

In `R_calibration` the model recognizes the generalized least-squares covariance framework but its numerical estimates of amplitude, variance, significance and residual statistic are inconsistent with the frozen reference in all three trials. See `reference/R_calibration.json`, the raw answers, and `reference/R_calibration.json` (reference numerical values). Correct methodology stated in prose does not guarantee the correct numerical substitution.

## Positive control and limits

`R_search` passes all three strict structured trials, showing that the grader does not automatically fail every scientific response. The result is not a general AI benchmark ranking. Error rates here describe only these prompts and exact settings. Use of a computation tool or independent human scientific review could change outcomes. No claim is made that AI cannot solve WIMP physics, nor that a realistic dark-matter signal or underground enhancement has been established.

## Insight

An evaluation of scientific AI should check *outcomes and numerical invariants*, not only plausible-looking explanations. The examples here show how apparently competent mathematical prose can conceal a wrong value and potentially a wrong statistical claim.

## Relationship to the original physics computation

The standalone numerical simulation in `wimp_scientific_case/` models a simplified Galactic-halo input, atmospheric and crustal material, scattering kinematics and an idealized xenon recoil-scoring observable. It supplied real computational-physics motivation and original illustrative plots. **The submitted AI benchmark does not evaluate end-to-end implementation of that simulation.** Its four smaller, deliberately specified diagnostic problems test quantitative dependencies, covariance-aware uncertainty and inference. The two components are related scientifically but should not be conflated.

## Rubric-matched self-assessment and limits

- **Task design (20 points available):** Four deterministic-answer tasks with frozen prompts, numeric tolerances, known-good reference fixtures. The guide recommends approximately five to ten tasks; this submission has fewer.
- **Grader reliability (20):** Unit tests, independent-reference checks, authored incorrect and boundary fixtures. The strict JSON rule can yield a formatting failure for a fenced yet otherwise interpretable reply; this is reported separately, not as a proven scientific failure.
- **Evidence of limitations (15):** GPT-5.2 repeated across three trials per task; original transcripts included. Only one model/version is tested, so cross-model variability and tool-assisted performance are unknown.
- **Reproducibility (15):** README, frozen transcripts, seed-independent arithmetic checks, offline replay. Future fresh API trials require model access and may differ; cost is not claimed without billing data.
- **Domain relevance (15):** Multi-step stochastic transport, finite-aperture effects and shared calibration can alter scientific conclusions. These are synthetic diagnostic tasks, not a peer-reviewed measurement.
- **Human expertise (10):** Physics foundations and numerical case are separate from the AI evaluation. AI-assisted writing and code support are disclosed; manual scientific adjudication of every explanation remains pending.
- **Insight (5):** Plausible mathematical explanations may violate elementary numerical invariants; a deterministic checker can surface these discrepancies.

This is a qualitative self-audit against the published rubric, **not** a claim of any awarded score.
