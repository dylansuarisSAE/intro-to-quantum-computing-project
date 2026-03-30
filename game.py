"""Core game dataclasses — PennyLaneGame level and GameProgress tracker."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from gate_types import CircuitOp, Mode1, SINGLE_1Q, format_circuit
from circuit import build_qasm, draw_circuit
from quokka import send_to_quokka
from evaluation import count_bits_single, probs_from_counts, mae_dist, frac_2q_matches


@dataclass
class GameProgress:
    max_cleared: int = 0

    def record_pass(self, level_id: int) -> None:
        if level_id > self.max_cleared:
            self.max_cleared = level_id

    def can_play(self, level_id: int) -> bool:
        if level_id <= 1:
            return True
        return self.max_cleared >= level_id - 1


@dataclass
class PennyLaneGame:
    """PennyLane for circuit building/drawing, Quokka for execution."""

    num_qubits: int
    level_id: int
    level_label: str
    quokka: str = "quokka1"
    applied: List[CircuitOp] = field(default_factory=list)

    mode_1q: Optional[Mode1] = None
    target_bit: int = 1
    target_distribution: Tuple[float, float] = (0.5, 0.5)
    prob_shots: int = 1000
    det_shots: int = 100

    target_bits_2q: Optional[Tuple[int, int]] = None
    det_shots_2q: int = 150

    mae_tolerance: float = 0.05
    det_match_fraction: float = 0.99

    def __post_init__(self) -> None:
        if self.num_qubits not in (1, 2):
            raise ValueError("num_qubits must be 1 or 2")
        if self.num_qubits == 1:
            if self.mode_1q is None:
                raise ValueError("1-qubit level needs mode_1q")
        else:
            if self.target_bits_2q is None:
                raise ValueError("2-qubit level needs target_bits_2q")

    def reset_circuit(self) -> None:
        self.applied.clear()

    def pop_gate(self) -> None:
        if self.applied:
            self.applied.pop()

    def gate_order_display(self) -> str:
        return format_circuit(self.applied)

    def draw(self) -> str:
        return draw_circuit(self.applied, self.num_qubits)

    def preview_qasm(self) -> str:
        return build_qasm(self.applied, self.num_qubits)

    def push_1q(self, gate: str, qidx: int) -> None:
        g = gate.upper()
        if g not in SINGLE_1Q:
            raise ValueError(f"Unknown single-qubit gate: {gate}")
        if qidx < 0 or qidx >= self.num_qubits:
            raise ValueError(f"Qubit index must be 0..{self.num_qubits - 1}, got {qidx}")
        self.applied.append(("1", g, qidx))

    def push_cx(self, control: int, target: int) -> None:
        if self.num_qubits != 2:
            raise ValueError("CNOT/CX only on 2-qubit levels")
        for x in (control, target):
            if x not in (0, 1):
                raise ValueError("Control/target must be 0 or 1")
        if control == target:
            raise ValueError("Control and target must differ")
        self.applied.append(("cx", control, target))

    def push_swap(self) -> None:
        if self.num_qubits != 2:
            raise ValueError("SWAP only on 2-qubit levels")
        self.applied.append(("swap",))

    def push_cz(self, a: int, b: int) -> None:
        if self.num_qubits != 2:
            raise ValueError("CZ only on 2-qubit levels")
        for x in (a, b):
            if x not in (0, 1):
                raise ValueError("CZ qubits must be 0 or 1")
        if a == b:
            raise ValueError("CZ needs two different qubits")
        self.applied.append(("cz", a, b))

    def submit(self) -> dict:
        script = build_qasm(self.applied, self.num_qubits)

        if self.num_qubits == 1:
            assert self.mode_1q is not None
            if self.mode_1q == "deterministic":
                shots = send_to_quokka(
                    script, self.det_shots, self.quokka, bits_per_shot=1
                )
                bits = [s[0] for s in shots]
                n = len(bits)
                c0, c1 = count_bits_single(bits)
                p0, p1 = probs_from_counts(c0, c1)
                want = self.target_bit
                matches = c1 if want == 1 else c0
                frac = matches / n
                ok = frac >= self.det_match_fraction
                msg = (
                    f"Success: {matches}/{n} shots are {want} (target |{want}>); "
                    f"P(|0>)={p0:.3f}, P(|1>)={p1:.3f}."
                    if ok
                    else (
                        f"Fail: target |{want}>. Counts: |0>={c0}, |1>={c1} "
                        f"-> P(|0>)={p0:.3f}, P(|1>)={p1:.3f}. "
                        f"Circuit: {self.gate_order_display()}"
                    )
                )
                return {
                    "success": ok,
                    "level_id": self.level_id,
                    "message": msg,
                    "counts": (c0, c1),
                    "observed": (p0, p1),
                    "match_fraction": frac,
                    "script": script,
                }

            shots = send_to_quokka(
                script, self.prob_shots, self.quokka, bits_per_shot=1
            )
            bits = [s[0] for s in shots]
            c0, c1 = count_bits_single(bits)
            obs = probs_from_counts(c0, c1)
            tgt = self.target_distribution
            mae = mae_dist(obs, tgt)
            ok = mae <= self.mae_tolerance
            t0, t1 = tgt
            msg = (
                f"Success: MAE={mae:.4f} (tol {self.mae_tolerance:.2f}). "
                f"Counts |0>={c0}, |1>={c1}: P(|0>)={obs[0]:.3f}, P(|1>)={obs[1]:.3f}. "
                f"Target P(|0>)={t0:.3f}, P(|1>)={t1:.3f}."
                if ok
                else (
                    f"Fail: MAE={mae:.4f}. Observed P(|0>)={obs[0]:.3f}, P(|1>)={obs[1]:.3f}; "
                    f"target P(|0>)={t0:.3f}, P(|1>)={t1:.3f}. "
                    f"Circuit: {self.gate_order_display()}"
                )
            )
            return {
                "success": ok,
                "level_id": self.level_id,
                "message": msg,
                "mae": mae,
                "observed": obs,
                "counts": (c0, c1),
                "target_distribution": tgt,
                "script": script,
            }

        assert self.target_bits_2q is not None
        shots = send_to_quokka(
            script, self.det_shots_2q, self.quokka, bits_per_shot=2
        )
        want = self.target_bits_2q
        frac = frac_2q_matches(shots, want)
        matches = int(round(frac * len(shots)))
        ok = frac >= self.det_match_fraction
        msg = (
            f"Success: {matches}/{len(shots)} shots match target "
            f"(q0,q1)=({want[0]},{want[1]}) "
            f"({100 * frac:.1f}% >= {100 * self.det_match_fraction:.0f}% required)."
            if ok
            else (
                f"Fail: want measurement (q0,q1)=({want[0]},{want[1]}) every time. "
                f"Got match rate {100 * frac:.1f}%. "
                f"Circuit: {self.gate_order_display()}"
            )
        )
        return {
            "success": ok,
            "level_id": self.level_id,
            "message": msg,
            "match_fraction": frac,
            "script": script,
        }
