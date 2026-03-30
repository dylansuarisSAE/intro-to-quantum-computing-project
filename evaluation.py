"""Scoring and measurement-statistics helpers."""

from __future__ import annotations

from typing import Sequence, Tuple


def count_bits_single(bits: Sequence[int]) -> Tuple[int, int]:
    z = sum(1 for b in bits if b == 0)
    o = sum(1 for b in bits if b == 1)
    if z + o != len(bits):
        raise ValueError("Non 0/1 in single-qubit results")
    return z, o


def probs_from_counts(c0: int, c1: int) -> Tuple[float, float]:
    n = c0 + c1
    if n == 0:
        raise ValueError("No shots")
    return c0 / n, c1 / n


def mae_dist(obs: Tuple[float, float], tgt: Tuple[float, float]) -> float:
    return 0.5 * (abs(obs[0] - tgt[0]) + abs(obs[1] - tgt[1]))


def frac_2q_matches(
    shots: Sequence[Tuple[int, ...]], want: Tuple[int, int]
) -> float:
    """Fraction of shots where (b0, b1) == want."""
    if not shots:
        return 0.0
    ok = sum(1 for s in shots if s == want)
    return ok / len(shots)
