"""Strict JSON validation for the structured reward."""

import json
import math


def _unique_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise ValueError(f"Invalid JSON constant: {token}")


def parse_response(response: object, expected: dict) -> dict | None:
    if not isinstance(response, str):
        return None
    try:
        result = json.loads(response, object_pairs_hook=_unique_keys, parse_constant=_reject_constant)
        if not isinstance(result, dict) or not expected.keys() <= result.keys():
            return None
        explanation = result.get("explanation")
        if not isinstance(explanation, str) or not explanation.strip():
            return None
        for field, reference in expected.items():
            value = result[field]
            if isinstance(reference, str):
                if not isinstance(value, str):
                    return None
            elif type(value) not in (int, float) or not math.isfinite(value):
                return None
    except (ValueError, OverflowError, RecursionError):
        return None
    return result
