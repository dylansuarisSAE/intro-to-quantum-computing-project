# Technical Design Document

## 1. Core Data Structures

The application relies on several core data structures mapped between the Frontend and the Game Engine.

**QubitLine**
Represents a single wire in the circuit.
```json
{
  "id": "q0",
  "index": 0,
  "state_vector_preview": [1.0, 0.0] 
}
```

**QuantumGate**
Represents a gate placed on the circuit.
```json
{
  "id": "gate_123",
  "type": "CNOT",
  "target_qubits": [1],
  "control_qubits": [0],
  "position": 2,
  "parameters": {}
}
```

**PlayerCircuit**
The current state of the player's circuit payload sent to the backend.
```json
{
  "circuit_id": "circ_001",
  "num_qubits": 4,
  "gates": [
    {"type": "H", "target_qubits": [0], "position": 0},
    {"type": "CNOT", "target_qubits": [1], "control_qubits": [0], "position": 1}
  ]
}
```

**PuzzleDefinition**
The static definition of a puzzle level loaded by the Game Engine.
```json
{
  "level_id": 3,
  "title": "Bell State Generator",
  "num_qubits": 2,
  "available_gates": ["H", "X", "CNOT"],
  "max_gates": 5,
  "target_distribution": {
    "00": 0.5,
    "11": 0.5
  },
  "tolerance": 0.05
}
```

**MeasurementDistribution**
The results obtained from the Quokka backend and evaluated against the PuzzleDefinition.
```json
{
  "shots": 1000,
  "counts": {
    "00": 495,
    "11": 505
  },
  "probabilities": {
    "00": 0.495,
    "11": 0.505
  }
}
```

---

## 2. Gameplay Execution Pipeline

1. **Player action**: Player drags an 'H' gate onto Qubit 0 at position 0 in the UI. Client-side visualizers (e.g. Bloch sphere) optionally update their local previews.
2. **Circuit update**: Upon submission, the Frontend sends the new `PlayerCircuit` payload to the FastAPI Game Engine via a REST API endpoint.
3. **QASM generation**: The Game Engine forwards the `PlayerCircuit` to the Quantum Execution Layer. The PennyLane Generator builds a `QuantumScript` and translates it into OpenQASM.
4. **Quantum execution**: The Quokka Executor submits the OpenQASM string to the Quokka backend via HTTP POST (no auth required) and awaits the result.
5. **Measurement sampling**: The Quokka backend returns shot counts (e.g., 500 shots of '0', 500 shots of '1').
6. **Distribution comparison**: The Data Layer evaluates the measured distribution against the `PuzzleDefinition`'s target distribution, checking if the Mean Absolute Error (MAE) is within statistical tolerance.
7. **UI update**: The Game Engine returns the measurement results and pass/fail status to the Frontend, which updates the visual dashboards and allows the player to progress.

---

## 3. Team Roles

The 5-member team handles different architectural domains:

1. **Quantum Systems Lead**: Owns the Quantum Execution Layer. Since the existing CLI backend is largely sufficient, focuses on maintaining the PennyLane-to-QASM logic, ensuring the Quokka client remains reliable, and handling any quantum-specific scaling constraints.
2. **Backend / API Engineer**: Owns the Game Engine (FastAPI) and REST API contracts. Responsible for building the bridge that wires the new UI into the existing quantum backend, defining Pydantic payloads, and applying SOLID principles to the web service.
3. **Frontend UI Engineer**: Owns the Vanilla JS/HTML Web UI. Responsible for the drag-and-drop circuit builder, implementing the client-side Bloch sphere rendering, and integrating the API client.
4. **Game Design & Puzzle Engineer**: Owns the Data & Puzzle Layer. Responsible for creating JSON puzzle definitions, determining target distributions, tuning the evaluation tolerance, and defining the learning curve for players.
5. **Integration & DevOps Engineer**: Owns the deployment. Responsible for containerizing the FastAPI backend, hosting the frontend static files, establishing the CI/CD pipeline, and maintaining the project structure.

---

## 4. Epics and Stories

Most of the underlying quantum backend (circuit building, QASM generation, Quokka client) is already functional. The development focuses on uplifting the experience to a web architecture.

**Epic 1: Build UI**
- *Owner*: Frontend UI Engineer
- *Stories*: 
  - Scaffold lightweight Vanilla JS / HTML application.
  - Implement circuit builder (Vanilla JS drag-and-drop for gates on up to 4 qubit lines).
  - Implement client-side Bloch Sphere visualization logic.
  - Create results dashboard and puzzle level progression layout.

**Epic 2: Wire UI into API layer**
- *Owner*: Backend / API Engineer & Quantum Systems Lead
- *Stories*: 
  - Wrap the existing Python quantum backend (PennyLane/Quokka) in FastAPI endpoints.
  - Define data contracts (`PlayerCircuit`, `MeasurementDistribution`) via OpenAPI/Pydantic.
  - Integrate the Vanilla JS frontend to call FastAPI backend endpoints, returning pass/fail and shot data.
  - Preserve the existing `cli.py` functionality within a debugging module.

**Epic 3: Deploy backend**
- *Owner*: Integration & DevOps Engineer
- *Stories*: 
  - Containerize the FastAPI backend (Docker).
  - Setup hosting/CDN for the frontend static files.
  - Establish a deployment pipeline (GitHub Actions).

---

## 5. Suggested Milestone Plan

A streamlined 4-week development plan for a student team:

**Week 1: Scaffolding and API Contracts**
- Wrap existing backend in a FastAPI skeleton and define the API data contracts.
- Start UI scaffolding (HTML/CSS grid for the circuit builder).
- Retain CLI as a fallback testing harness.

**Week 2: Frontend Construction**
- Build the core UI components: drag-and-drop circuit building.
- Develop the client-side Bloch sphere component.
- Backend team solidifies puzzle definitions format.

**Week 3: End-to-End Integration**
- Wire UI into the API layer.
- Ensure the Frontend can successfully submit dynamic circuits to FastAPI, execute on Quokka, and evaluate against puzzle definitions.
- Implement UI feedback for puzzle completion (pass/fail states).

**Week 4: Deployment and Polish**
- Containerize and deploy the backend; host the static frontend.
- Final bug fixing, handle edge cases (e.g., invalid gate placements, Quokka timeouts).
- Finalize presentation materials.
