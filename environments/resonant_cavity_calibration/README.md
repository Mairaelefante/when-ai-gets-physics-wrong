# Resonant cavity calibration

A single-turn physics evaluation adapted from `R_calibration` in
[When AI Gets Physics Wrong](https://github.com/Mairaelefante/when-ai-gets-physics-wrong/tree/cb0981b/when-ai-gets-physics-wrong).
The model fits a signal amplitude to six synthetic measurements under a known
covariance with shared calibration uncertainty. It compares the result with a
diagonal-covariance fit and distinguishes statistical significance from physical
identification.

## Run

From this directory:

```sh
uv venv
uv pip install -e .
uv run --no-project vf-eval -s resonant-cavity-calibration -m gpt-4.1 -n 1 -r 3
```

Set the API key for your configured evaluation endpoint before running a live
model. The environment has no configuration arguments. The prompt and numerical
reference ship inside the package, and grading works offline.

## Reward

`structured_accuracy` is 1 when the reply is a single JSON object with all five
numeric fields within the original tolerance and both decision strings correct.
The tolerance is the larger of 1e-10 and 0.2% of the reference magnitude. Each
reply must include a nonempty explanation. Scientific review of the explanation
is manual. The reference comes from the original Sherman–Morrison GLS solver.

This version provides one fixed example for evaluation. Its public reference
and small size limit its use as a training set or a general physics benchmark.
