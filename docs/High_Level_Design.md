# High-Level System Architecture

The Quantum Pipelines system follows a Service-Oriented Architecture (SOA), separating the frontend presentation layer from the quantum logic backend. The architecture consists of four major subsystems, designed to support dynamic generation of circuits during gameplay.

## 1. Subsystems Overview

- **Frontend UI (Web Client)**: A lightweight web application (Vanilla JS / HTML / CSS) providing the visual interface. It manages drag-and-drop interactions, performs client-side Bloch sphere visualization, and communicates with the backend via RESTful APIs.
- **Game Engine (FastAPI Backend)**: The core service managing game state validation, routing player moves, and defining puzzle configurations. It acts as the orchestrator between the user interface and the quantum layers.
- **Quantum Execution Layer**: Encapsulates all quantum logic, reusing the existing proof-of-concept backend. It takes abstract circuit representations from the Game Engine, uses PennyLane to construct the circuit, generates OpenQASM, and submits it to the Quokka execution backend via a stateless HTTP POST.
- **Data & Puzzle Layer**: Manages the static puzzle definitions (target distributions, available gates) and provides evaluation mechanisms to compare the player's results against the target goals.

Data flows from the Frontend (player interactions) to the Game Engine (validation), which then passes the circuit to the Quantum Layer for execution. The results are evaluated in the Data layer and returned via the Game Engine to the Frontend for visualization. Game state is maintained primarily in-memory/client-side, without requiring persistent database storage at this stage. The legacy CLI is preserved alongside the new backend as a debugging tool.

---

## 2. Component Architecture Diagram

```ascii
Player Input (Drag & Drop)
│
▼
┌─────────────────────────────────────────┐
│              Frontend UI                │
│ ├── Circuit Builder Component           │
│ ├── Client-Side Bloch Sphere            │
│ └── Results Dashboard                   │
└──────────────────┬──────────────────────┘
                   │ HTTP/REST API
                   ▼
┌─────────────────────────────────────────┐
│        Game Engine (FastAPI)            │
│ ├── API Router & Game Logic             │
│ ├── Circuit Validator                   │
│ ├── Puzzle Manager                      │
│ └── CLI Debugging Tool (Preserved)      │
└──────────────────┬──────────────────────┘
                   │ Abstract Circuit Definition
                   ▼
┌─────────────────────────────────────────┐
│        Quantum Execution Layer          │
│ ├── PennyLane Circuit Generator         │
│ ├── QASM Translator                     │
│ └── Quokka Executor (Stateless POST)    │
└──────────────────┬──────────────────────┘
                   │ Measurement Results
                   ▼
┌─────────────────────────────────────────┐
│        Data & Puzzle Layer              │
│ ├── Measurement Analyzer                │
│ ├── Distribution Evaluator              │
│ └── Puzzle Definitions Store            │
└──────────────────┬──────────────────────┘
                   │ Evaluation Results (Pass/Fail, Distribution)
                   ▼
            (Back to Frontend UI)
```
