# Quantum Gate Game (PennyLane + Quokka)

An interactive command-line puzzle game for learning quantum gates.
Build quantum circuits with **PennyLane**, which exports them to **OpenQASM 2.0**, then execute them on the **Quokka** cloud simulator and try to hit target measurement outcomes across four progressive levels.

## Architecture

```
User input (gate commands)
        │
        ▼
┌───────────────────────────────────────────┐
│              PennyLane                    │
│                                           │
│  1. Builds a QuantumScript (tape) from    │
│     user gate commands                    │
│  2. Exports to OpenQASM 2.0 via          │
│     tape.to_openqasm()                    │
│  3. Draws ASCII circuit diagrams via      │
│     qml.draw()                            │
└──────────────────┬────────────────────────┘
                   │  QASM string
                   ▼
            ┌──────────────┐
            │   Quokka     │  HTTP POST to
            │   backend    │  quokkacomputing.com/qsim/qasm
            │  (execution) │
            └──────┬───────┘
                   │  measurement results (JSON)
                   ▼
            ┌──────────────┐
            │  Evaluation  │
            │  (pass/fail) │
            └──────────────┘
```

| Component | Role |
|-----------|------|
| **PennyLane** | Builds quantum circuits as `QuantumScript` tapes, exports them to OpenQASM 2.0 via `tape.to_openqasm()`, and renders ASCII circuit diagrams via `qml.draw()`. |
| **Quokka** | Remote quantum simulator backend. Receives the PennyLane-generated OpenQASM 2.0 script over HTTP and returns shot-based measurement statistics. |

## How the Pipeline Works

1. **User types gate commands** (e.g. `H`, `X`, `CNOT 0 1`) -- stored as lightweight tuples.
2. **`circuit.py` builds a PennyLane `QuantumScript`** -- each tuple becomes a real PennyLane operation (`qml.Hadamard`, `qml.PauliX`, `qml.CNOT`, etc.).
3. **PennyLane exports QASM** -- `tape.to_openqasm()` serialises the tape to an OpenQASM 2.0 string.
4. **QASM is POSTed to Quokka** -- `quokka.py` sends `{"script": "<QASM>", "count": N}` to the Quokka API.
5. **Results are evaluated** -- shot outcomes are compared against the level's target state.

## Levels

| Level | Qubits | Mode | Goal |
|-------|--------|------|------|
| 1 | 1 | Deterministic | Reach \|1⟩ on q\[0\] |
| 2 | 1 | Probabilistic | Reach ~50/50 superposition (MAE) |
| 3 | 2 | Deterministic | Reach \|11⟩ (CNOT, SWAP, CZ introduced) |
| 4 | 2 | Deterministic | Reach \|01⟩ |

Pass each level to unlock the next.

## Prerequisites

- Python 3.9 or higher

## Setup

### 1. Clone and enter the repository

```bash
git clone <repo-url>
```

### 2. Create a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` at the start of your terminal prompt when the environment is active.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Game


```bash
python main.py
```

That's it. On startup the game will:

1. Display the PennyLane version.
2. Ask for the Quokka host prefix -- press **Enter** to accept the default (`quokka1`).
3. Show the level menu (1--4). Type a number and press **Enter** to play.

### Quick example session

```
Quantum Gate Game (PennyLane + Quokka)

PennyLane version: 0.38.0  (circuit building & drawing)
Execution backend: Quokka (QASM over HTTP)

Quokka prefix [quokka1] (Enter = default):

========== LEVELS (pass each to unlock the next) ==========
  1) Level 1 (1-qubit): |1> on q[0]
  2) (locked) Pass Level 1 first.
  ...
Select level: 1

--- Level 1 (1-qubit) ---
Goal: measurements match target |1> (q[0]).

Level 1 (1-qubit) > X
Circuit: X[q0]

Level 1 (1-qubit) > draw
0: --X-+  Sample

Level 1 (1-qubit) > qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[1];
creg c[1];
x q[0];
measure q[0] -> c[0];

Level 1 (1-qubit) > submit
Success: 100/100 shots are 1 (target |1>); P(|0>)=0.000, P(|1>)=1.000.
*** Level 1 (1-qubit) passed! ***
```

## In-Game Commands

| Command | Description |
|---------|-------------|
| `X`, `H`, `Z`, `Y`, `I` | Apply single-qubit gate (1-qubit levels: no index needed) |
| `H 0`, `X 1`, etc. | Apply single-qubit gate to qubit 0 or 1 (2-qubit levels) |
| `CNOT 0 1` / `CX 0 1` | Controlled-NOT (control, target) |
| `SWAP` | Swap q\[0\] and q\[1\] |
| `CZ 0 1` / `CZ` | Controlled-Z |
| `show` | Print current gate sequence |
| `draw` | PennyLane ASCII circuit diagram |
| `qasm` | Preview the PennyLane-generated OpenQASM 2.0 script |
| `undo` | Remove last gate |
| `clear` | Reset circuit |
| `submit` | Build QASM via PennyLane, send to Quokka, evaluate result |
| `menu` | Return to level select |
| `quit` | Exit |

## Project Structure

```
pennylane_game/            <-- repo root
├── main.py                # Entry point: python main.py
├── gate_types.py          # Shared type aliases, constants, op formatting
├── circuit.py             # PennyLane circuit building, QASM export, drawing
├── quokka.py              # Quokka HTTP client (send QASM, parse results)
├── evaluation.py          # Measurement scoring helpers (counts, MAE, match %)
├── game.py                # PennyLaneGame & GameProgress dataclasses
├── cli.py                 # Interactive game loop, input parsing, help text
├── requirements.txt       # Python dependencies
└── README.md
```
