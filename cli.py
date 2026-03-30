"""Interactive command-line game loop."""

from __future__ import annotations

import sys
from typing import List, Tuple

import pennylane as qml
import requests

from gate_types import SINGLE_1Q
from game import GameProgress, PennyLaneGame


def _print_help_1q() -> None:
    print(
        "Gates: X, Z, H, Y, I (one qubit q[0] only on this level).\n"
        "Other: undo, clear, show, draw, qasm, submit, menu, help, ?, quit\n"
        "  draw = PennyLane circuit diagram;  qasm = show OpenQASM script."
    )


def _print_help_2q() -> None:
    print(
        "Two-qubit level (q[0] and q[1]).\n"
        "Single-qubit (must give qubit index 0 or 1):\n"
        "  H 0    X 1    Z 0    Y 1    I 0\n"
        "Two-qubit:\n"
        "  CNOT 0 1   or   CX 0 1\n"
        "  SWAP\n"
        "  CZ 0 1   or   CZ\n"
        "Other: undo, clear, show, draw, qasm, submit, menu, help, ?, quit\n"
        "  draw = PennyLane circuit diagram;  qasm = show OpenQASM script."
    )


LEVEL_MENU: List[Tuple[int, str]] = [
    (1, "Level 1 (1-qubit): |1> on q[0]"),
    (2, "Level 2 (1-qubit): 50/50 on q[0] (MAE)"),
    (3, "Level 3 (2-qubit): CNOT, SWAP, CZ — reach |11>"),
    (4, "Level 4 (2-qubit): CNOT, SWAP, CZ — reach |01>"),
]


def _make_level_game(level_id: int, host: str) -> PennyLaneGame:
    if level_id == 1:
        return PennyLaneGame(
            num_qubits=1, level_id=1,
            level_label="Level 1 (1-qubit)",
            quokka=host, mode_1q="deterministic",
            target_bit=1, det_shots=100,
        )
    if level_id == 2:
        return PennyLaneGame(
            num_qubits=1, level_id=2,
            level_label="Level 2 (1-qubit)",
            quokka=host, mode_1q="probabilistic",
            target_distribution=(0.5, 0.5), prob_shots=1000,
        )
    if level_id == 3:
        return PennyLaneGame(
            num_qubits=2, level_id=3,
            level_label="Level 3 (2-qubit): CNOT, SWAP, CZ",
            quokka=host, target_bits_2q=(1, 1), det_shots_2q=150,
        )
    if level_id == 4:
        return PennyLaneGame(
            num_qubits=2, level_id=4,
            level_label="Level 4 (2-qubit): CNOT, SWAP, CZ",
            quokka=host, target_bits_2q=(0, 1), det_shots_2q=200,
        )
    raise ValueError(f"Unknown level_id: {level_id}")


def _submit_error_hint(exc: BaseException) -> str:
    msg = str(exc).lower()
    if "resolve" in msg or "getaddrinfo" in msg:
        return "\n  (Check DNS / Quokka host name.)"
    return ""


def _print_level_banner(game: PennyLaneGame) -> None:
    print(f"\n--- {game.level_label} ---")
    print(f"Circuits: PennyLane  |  Execution: Quokka ({game.quokka})")
    if game.num_qubits == 1:
        assert game.mode_1q is not None
        if game.mode_1q == "deterministic":
            print("Goal: measurements match target |1> (q[0]).")
            print(
                f"Submit: shots={game.det_shots}, need >= "
                f"{100 * game.det_match_fraction:.0f}% outcome 1."
            )
        else:
            print("Goal: ~50/50 on q[0] (e.g. H).")
            print(f"Submit: shots={game.prob_shots}, MAE tol={game.mae_tolerance}")
        print("Initial state: |0> on q[0].")
        _print_help_1q()
    else:
        assert game.target_bits_2q is not None
        t0, t1 = game.target_bits_2q
        print(f"Goal: both qubits measured as (q0,q1)=({t0},{t1}) (e.g. |{t0}{t1}>).")
        print(
            f"Submit: shots={game.det_shots_2q}, need >= "
            f"{100 * game.det_match_fraction:.0f}% shots matching."
        )
        print("Initial state: |00>.")
        _print_help_2q()


def _parse_gate_line(line: str, game: PennyLaneGame) -> bool:
    parts = line.split()
    if not parts:
        return False
    cmd = parts[0].upper()

    if game.num_qubits == 1:
        if cmd in SINGLE_1Q and len(parts) == 1:
            game.push_1q(cmd, 0)
            return True
        if cmd in SINGLE_1Q and len(parts) == 2:
            print("Level 1-2 use one qubit only: type e.g. H (no index).")
            return True
        return False

    if cmd in ("CNOT", "CX"):
        if len(parts) != 3:
            print("Usage: CNOT <control> <target>  e.g.  CNOT 0 1")
            return True
        try:
            game.push_cx(int(parts[1]), int(parts[2]))
        except ValueError as e:
            print(e)
        return True

    if cmd == "SWAP":
        if len(parts) > 1:
            print("SWAP takes no arguments.")
            return True
        game.push_swap()
        return True

    if cmd == "CZ":
        if len(parts) == 3:
            try:
                game.push_cz(int(parts[1]), int(parts[2]))
            except ValueError as e:
                print(e)
        elif len(parts) == 1:
            game.push_cz(0, 1)
        else:
            print("Usage: CZ 0 1   or plain CZ")
        return True

    if cmd in SINGLE_1Q:
        if len(parts) != 2:
            print(f"Usage: {cmd} <0|1>  e.g.  {cmd} 0")
            return True
        try:
            game.push_1q(cmd, int(parts[1]))
        except ValueError as e:
            print(e)
        return True

    return False


def play_level(game: PennyLaneGame, progress: GameProgress) -> None:
    _print_level_banner(game)
    while True:
        line = input(f"\n{game.level_label} > ").strip()
        if not line:
            continue
        low = line.lower()
        if low in ("q", "quit", "exit"):
            print("Bye.")
            sys.exit(0)
        if low in ("menu", "m", "back"):
            print("Returning to level menu.\n")
            return
        if low in ("help", "?"):
            _print_help_1q() if game.num_qubits == 1 else _print_help_2q()
            continue
        if low == "undo":
            game.pop_gate()
            print(f"Circuit: {game.gate_order_display()}")
            continue
        if low == "clear":
            game.reset_circuit()
            print("Circuit cleared.")
            continue
        if low == "show":
            print(f"Circuit: {game.gate_order_display()}")
            continue
        if low == "draw":
            try:
                print(game.draw())
            except Exception as e:
                print(f"Could not draw: {e}")
            continue
        if low == "qasm":
            print(game.preview_qasm())
            continue
        if low == "submit":
            try:
                r = game.submit()
            except (requests.RequestException, RuntimeError, ValueError) as e:
                print(f"Submit failed: {e}{_submit_error_hint(e)}")
                continue
            print(r["message"])
            if r.get("success"):
                progress.record_pass(r["level_id"])
                print(f"*** {game.level_label} passed! ***")
                nxt = r["level_id"] + 1
                if nxt <= 4 and progress.can_play(nxt):
                    print(f"Level {nxt} is now unlocked.")
            if r.get("script"):
                print("--- QASM sent ---\n" + r["script"])
            again = input("Play again on this level? [y/N]: ").strip().lower()
            if again in ("y", "yes"):
                game.reset_circuit()
                print("Circuit reset.")
            else:
                print("Returning to level menu.\n")
                return
            continue

        if _parse_gate_line(line, game):
            print(f"Circuit: {game.gate_order_display()}")
            continue

        print("Unknown command. Type help or ?.")


def run_interactive() -> None:
    print("Quantum Gate Game (PennyLane + Quokka)\n")
    print(f"PennyLane version: {qml.version()}  (circuit building & drawing)")
    print("Execution backend: Quokka (QASM over HTTP)\n")
    host = input("Quokka prefix [quokka1] (Enter = default): ").strip() or "quokka1"
    progress = GameProgress()

    while True:
        print("\n========== LEVELS (pass each to unlock the next) ==========")
        for lid, desc in LEVEL_MENU:
            if progress.can_play(lid):
                print(f"  {lid}) {desc}")
            else:
                print(f"  {lid}) (locked) Pass Level {lid - 1} first.")
        print("  q) Quit")
        choice = input("Select level: ").strip().lower()

        if choice in ("q", "quit", "exit"):
            print("Bye.")
            return
        if not choice.isdigit():
            print("Enter a level number or q.")
            continue
        level_id = int(choice)
        known = {lid for lid, _ in LEVEL_MENU}
        if level_id not in known:
            print(f"Unknown level. Available: {sorted(known)}")
            continue
        if not progress.can_play(level_id):
            print(f"Level {level_id} is locked. Pass Level {level_id - 1} first.")
            continue

        play_level(_make_level_game(level_id, host), progress)


def main() -> None:
    try:
        run_interactive()
    except KeyboardInterrupt:
        print("\nBye.")
        sys.exit(0)
