# System Architecture (Frontend + Backend + Quokka)

This project’s runtime pipeline has four layers:

- **Frontend**: UI for levels, circuit building, preview, submit, results (no login)
- **Backend API**: validates input, calls game engine, calls Quokka, returns JSON
- **Game Engine (this repo)**: builds circuits/QASM and evaluates results
- **Quokka**: external simulator that executes OpenQASM and returns shot results

## Layered Diagram

```mermaid
flowchart LR
    subgraph FE["Frontend Layer (Web App)"]
        A1["Level Menu"]
        A2["Circuit Builder<br/>(add/undo/clear gates)"]
        A3["Preview Panel<br/>(diagram + QASM)"]
        A4["Submit + Result UI"]
        A5["Local Storage<br/>(unlock progress, host)"]
        A1 --> A2 --> A3 --> A4
        A1 -.read/write.-> A5
        A4 -.read/write.-> A5
    end

    subgraph BE["Backend API Layer (Python/FastAPI)"]
        B1["GET /api/levels"]
        B2["POST /api/circuit/preview"]
        B3["POST /api/submit"]
        B4["Validation + Error Handling"]
        B4 --- B1
        B4 --- B2
        B4 --- B3
    end

    subgraph GAME["Game Engine Layer (Current Repo)"]
        C1["game.py<br/>PennyLaneGame + GameProgress"]
        C2["circuit.py<br/>Build tape + Export QASM"]
        C3["evaluation.py<br/>Counts / MAE / Match %"]
        C4["gate_types.py<br/>CircuitOp types"]
        C1 --> C2
        C1 --> C3
        C1 --> C4
    end

    subgraph EXT["External Compute Layer"]
        D1["quokka.py<br/>HTTP client + parser"]
        D2["Quokka Cloud API<br/>/qsim/qasm"]
        D1 -->|"POST QASM + count"| D2
        D2 -->|"shots JSON"| D1
    end

    FE -->|"HTTPS JSON"| BE
    B1 --> C1
    B2 --> C1
    B3 --> C1
    C2 --> D1
    D1 --> C1
    C1 --> BE
    BE --> FE
```

## Submit Flow (Sequence)

```mermaid
sequenceDiagram
    participant U as Player
    participant F as Frontend
    participant B as Backend API
    participant G as Game Engine
    participant Q as Quokka

    U->>F: Select level + build gate sequence
    F->>B: POST /api/submit {levelId, appliedOps, quokkaHost}
    B->>G: Create PennyLaneGame + submit()
    G->>G: build_qasm(appliedOps)
    G->>Q: Send QASM + shot count
    Q-->>G: Return measurement shots
    G->>G: Evaluate (deterministic/MAE/match fraction)
    G-->>B: {success, message, metrics, script}
    B-->>F: JSON response
    F-->>U: Show result + unlock next level (local)
```

