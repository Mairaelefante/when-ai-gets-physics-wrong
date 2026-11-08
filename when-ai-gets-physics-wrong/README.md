# When AI Gets Physics Wrong

**Reproducible physics-grounded evaluation of numerical reliability in language-model answers.**

[Open the interactive offline demonstration](OPEN_DEMO.html) by downloading and opening `OPEN_DEMO.html` in a modern browser. It contains illustrative 3D graphics, selected original scientific plots, and a side-by-side comparison between stored AI responses and deterministic reference values.

## Research question

Can an AI model give a scientifically plausible explanation yet make an internally inconsistent numerical calculation that changes its conclusion? This project examines that question using four structured tasks: stochastic transport, paired-history geometry, correlated calibration, and signal searches.

## What the evaluation actually tests

- `W_transport`: stochastic threshold probabilities versus mean-energy reasoning.
- `W_geometry`: paired-history ratios, geometry, uncertainty, and conclusions.
- `R_calibration`: common calibration covariance and generalized least squares.
- `R_search`: global significance and careful claims about identification, a positive control.

**Evidence:** 12 original GPT-5.2 trials, three per task; 3 structured passes, 8 structured numerical failures, and 1 format error. These are limited results from a single model with no model-side computational tools, **not** a general ranking of AI physics capability. `scientific_pass: null` means narrative scientific adjudication has not been completed; it does not mean a pending API response.

The included WIMP graphics motivate the domain. This evaluation **did not test an AI reproducing the full multi-layer WIMP simulation**. The standalone WIMP source code and its assumptions are maintained separately in the companion *WIMP Earth Transport* repository on this GitHub profile.

## Reproduce, offline

Requires Python 3. The runner and scorer use the Python standard library.

```bash
python3 -m unittest discover -s tests -v
python3 run_eval.py replay transcripts/all_tasks_final
```

For independent numerical checks, install the optional requirements in `requirements-verification.txt` and run:

```bash
python3 verify_reference.py
```

New live model calls require an `OPENAI_API_KEY` environment variable and may incur API charges. Consult `run_eval.py` for run command options. Stored transcript replay makes no network requests.

## Repository map

| Component | Purpose |
| --- | --- |
| `OPEN_DEMO.html` | Offline visual explainer, illustrative 3D and evidence board |
| `tasks/` | Four prompts with explicit success criteria |
| `reference.py` + `reference/` | Independently calculated numerical reference answers |
| `grader.py` | Deterministic checks and structured outcome scoring |
| `run_eval.py` | Model harness and offline replay |
| `transcripts/all_tasks_final/` | 12 preserved responses and their results |
| `fixtures/` + `tests/` | Positive, negative and edge-case grading tests |
| `REPORT.md` | Findings, caveats and interpretation |
| `docs/` | Derivations and adjudication guidance |

The rendered 3D particle tracks are **illustrations, not Monte Carlo output**. References are not supplied to the model during inference.

## Reproducibility and limitations

The numerical grader uses frozen references and structured comparisons. The evidence board is a replay of recorded API responses and is **not** a live model call. The sample includes four tasks and one tested model. A formal independent review of open-ended scientific explanations remains future work.

## Provenance and use of AI tools

The computational WIMP model predates this AI-evaluation exercise and is not included as a second full simulation here. The benchmark tasks, grading rules, model trials, documentation and visualization were subsequently assembled as a separate evaluation project. AI-assisted drafting and software development were used in preparing portions of the evaluation and presentation; all quantitative claims should be independently checked against the included references and transcript evidence. See `REPORT.md` for methodology.

## Licenses

The included Three.js library retains its accompanying `THREE_LICENSE.txt`. No license is granted for the remainder of this repository until a project license is explicitly selected by the owner.
