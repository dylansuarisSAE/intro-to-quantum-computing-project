"""PennyLane circuit building, OpenQASM export, and diagram drawing.

This is the core module that makes PennyLane the genuine circuit builder:
  1. User gate commands are stored as lightweight tuples (CircuitOp).
  2. build_tape()  converts those tuples into a PennyLane QuantumScript.
  3. build_qasm()  calls tape.to_openqasm() so PennyLane generates the QASM.
  4. draw_circuit() uses qml.draw() to render ASCII diagrams.

The generated OpenQASM 2.0 string is what gets sent to Quokka for execution.
"""

from __future__ import annotations

from typing import List, Sequence

import pennylane as qml
from pennylane.tape import QuantumScript
from pennylane.operation import Operation
from pennylane.measurements import MeasurementProcess

from gate_types import CircuitOp

PL_1Q_MAP = {
    "X": qml.PauliX,
    "Y": qml.PauliY,
    "Z": qml.PauliZ,
    "H": qml.Hadamard,
}


def _ops_from_circuit(applied: Sequence[CircuitOp]) -> List[Operation]:
    """Convert internal gate tuples into PennyLane Operation objects."""
    ops: List[Operation] = []
    for op in applied:
        k = op[0]
        if k == "1":
            g, qi = str(op[1]), int(op[2])
            if g == "I":
                continue
            ops.append(PL_1Q_MAP[g](wires=qi))
        elif k == "cx":
            ops.append(qml.CNOT(wires=[int(op[1]), int(op[2])]))
        elif k == "swap":
            ops.append(qml.SWAP(wires=[0, 1]))
        elif k == "cz":
            ops.append(qml.CZ(wires=[int(op[1]), int(op[2])]))
    return ops


def build_tape(
    applied: Sequence[CircuitOp], num_qubits: int
) -> QuantumScript:
    """Build a PennyLane QuantumScript (tape) from the user's gate sequence."""
    ops = _ops_from_circuit(applied)
    measurements: List[MeasurementProcess] = [
        qml.counts(wires=i) for i in range(num_qubits)
    ]
    return QuantumScript(ops, measurements, shots=1)


def build_qasm(applied: Sequence[CircuitOp], num_qubits: int) -> str:
    """Use PennyLane to build the circuit and export it as OpenQASM 2.0."""
    tape = build_tape(applied, num_qubits)
    wires = qml.wires.Wires(range(num_qubits))
    return tape.to_openqasm(wires=wires, measure_all=True)


def _apply_ops_in_qnode(applied: Sequence[CircuitOp]) -> None:
    """Create and queue PennyLane gates inside an active recording context (qnode)."""
    for op in applied:
        k = op[0]
        if k == "1":
            g, qi = str(op[1]), int(op[2])
            if g == "I":
                continue
            PL_1Q_MAP[g](wires=qi)
        elif k == "cx":
            qml.CNOT(wires=[int(op[1]), int(op[2])])
        elif k == "swap":
            qml.SWAP(wires=[0, 1])
        elif k == "cz":
            qml.CZ(wires=[int(op[1]), int(op[2])])


def draw_circuit(applied: Sequence[CircuitOp], num_qubits: int) -> str:
    """Return an ASCII diagram of the circuit via PennyLane's drawer."""
    dev = qml.device("default.qubit", wires=num_qubits, shots=1)

    @qml.qnode(dev)
    def circuit():
        _apply_ops_in_qnode(applied)
        if num_qubits == 1:
            return qml.sample(wires=0)
        return [qml.sample(wires=i) for i in range(num_qubits)]

    txt = qml.draw(circuit)()
    for old, new in [
        ("\u2500", "-"), ("\u2502", "|"),
        ("\u256d", "+"), ("\u256e", "+"),
        ("\u2570", "+"), ("\u256f", "+"),
        ("\u2524", "+"), ("\u251c", "+"),
        ("\u2534", "+"), ("\u252c", "+"),
        ("\u253c", "+"), ("\u25cf", "*"),
    ]:
        txt = txt.replace(old, new)
    return txt
