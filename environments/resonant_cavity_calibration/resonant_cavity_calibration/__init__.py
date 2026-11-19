"""Single-turn resonant-cavity calibration evaluation."""

import json
import math
from importlib.resources import files

import verifiers as vf
from datasets import Dataset

from ._grading import parse_response


async def structured_accuracy(completion: list[dict], info: dict) -> float:
    """Score a complete, correctly formatted answer against the numerical reference."""
    response = completion[-1].get("content") if completion and completion[-1]["role"] == "assistant" else None
    expected = info["reference"]
    result = parse_response(response, expected)
    if result is None:
        return 0.0

    for field, reference in expected.items():
        value = result[field]
        if isinstance(reference, str):
            correct = value.strip().casefold() == reference.casefold()
        else:
            correct = math.isclose(value, reference, rel_tol=0, abs_tol=max(1e-10, abs(reference) * 0.002))
        if not correct:
            return 0.0
    return 1.0


def load_environment() -> vf.Environment:
    task = json.loads(files(__package__).joinpath("task.json").read_text(encoding="utf-8"))
    dataset = Dataset.from_list(
        [{"prompt": [{"role": "user", "content": task["prompt"]}], "info": {"reference": task["answer"]}}]
    )
    return vf.SingleTurnEnv(
        eval_dataset=dataset,
        rubric=vf.Rubric(funcs=[structured_accuracy]),
    )
