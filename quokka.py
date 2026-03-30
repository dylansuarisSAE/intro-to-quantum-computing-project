"""Quokka HTTP backend — send OpenQASM, receive measurement results."""

from __future__ import annotations

import json
from typing import List, Tuple

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def normalize_shots(
    raw: object, bits_per_shot: int, expected_shots: int
) -> List[Tuple[int, ...]]:
    """Each shot is a tuple of 0/1 classical outcomes (length *bits_per_shot*)."""
    if raw is None or not isinstance(raw, list):
        raise TypeError(f"Expected list for c, got {type(raw).__name__}")
    out: List[Tuple[int, ...]] = []
    for i, res in enumerate(raw):
        if isinstance(res, (list, tuple)):
            if len(res) != bits_per_shot:
                raise ValueError(
                    f"Shot {i}: expected {bits_per_shot} classical bits, "
                    f"got {len(res)}: {res!r}"
                )
            shot = tuple(int(res[j]) for j in range(bits_per_shot))
        else:
            if bits_per_shot != 1:
                raise ValueError(
                    f"Shot {i}: expected list of length {bits_per_shot}, got {res!r}"
                )
            shot = (int(res),)
        for b in shot:
            if b not in (0, 1):
                raise ValueError(f"Shot {i}: expected 0/1, got {shot!r}")
        out.append(shot)
    if len(out) != expected_shots:
        preview = raw[:3] if isinstance(raw, list) else raw
        raise RuntimeError(
            f"Expected {expected_shots} shots, got {len(out)}. Preview: {preview!r}"
        )
    return out


def parse_quokka_payload(
    payload: object, expected_shots: int, bits_per_shot: int
) -> List[Tuple[int, ...]]:
    if not isinstance(payload, dict):
        raise RuntimeError(
            f"Quokka JSON should be an object, got {type(payload).__name__}"
        )
    ec = payload.get("error_code", 0)
    if ec != 0:
        detail = (
            payload.get("message")
            or payload.get("error")
            or payload.get("msg")
            or payload
        )
        raise RuntimeError(f"Quokka error_code={ec!r}: {detail!r}")
    result = payload.get("result")
    if not isinstance(result, dict):
        raise RuntimeError(f"Quokka missing or invalid 'result': {payload!r}")
    raw_c = result.get("c")
    return normalize_shots(raw_c, bits_per_shot, expected_shots)


def send_to_quokka(
    script: str,
    count: int,
    quokka: str,
    bits_per_shot: int = 1,
    timeout: float = 120.0,
) -> List[Tuple[int, ...]]:
    """POST an OpenQASM script to the Quokka simulator and return shot tuples."""
    url = f"http://{quokka}.quokkacomputing.com/qsim/qasm"
    response = requests.post(
        url, json={"script": script, "count": count}, timeout=timeout
    )
    response.raise_for_status()
    try:
        payload = response.json()
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Quokka did not return JSON: {response.text[:300]!r}"
        ) from e
    return parse_quokka_payload(payload, expected_shots=count, bits_per_shot=bits_per_shot)
