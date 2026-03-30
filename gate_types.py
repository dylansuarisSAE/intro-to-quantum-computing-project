"""Shared type aliases, constants, and circuit-op formatting."""

from __future__ import annotations

from typing import Literal, Sequence, Tuple, Union

Mode1 = Literal["deterministic", "probabilistic"]

# Circuit op: ("1", gate, qidx) | ("cx", c, t) | ("swap",) | ("cz", a, b)
CircuitOp = Tuple[Union[str, int], ...]

SINGLE_1Q = frozenset({"X", "Z", "H", "Y", "I"})
TWO_Q_GATES = frozenset({"CNOT", "CX", "SWAP", "CZ"})


def format_op(op: CircuitOp) -> str:
    k = op[0]
    if k == "1":
        return f"{op[1]}[q{op[2]}]"
    if k == "cx":
        return f"CX q[{op[1]}]->q[{op[2]}]"
    if k == "swap":
        return "SWAP"
    if k == "cz":
        return f"CZ q[{op[1]}],q[{op[2]}]"
    return str(op)


def format_circuit(applied: Sequence[CircuitOp]) -> str:
    return "(none)" if not applied else " -> ".join(format_op(o) for o in applied)
