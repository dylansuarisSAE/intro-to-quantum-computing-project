# Task
You are a senior software architect helping design the technical architecture for an educational quantum computing puzzle game. 

The project is called **Quantum Pipelines**.

Your goal is to produce a **component architecture plan suitable for a small student team implementing the game over several weeks.** Based on the requirements contained within this document and the existing proof-of-concept backend code contained within this repository.

The following documents and deliverables are expected:
* An uplifted project structure within `README.md`
* High level design document
* System Architecture Diagram
* Technical Design Document

The team consists of **5 members** with different specialisations.

The architecture must clearly separate **classical game logic from quantum computation logic.**

---

# Architectual principles
The design must embody Service-Oriented Architecture and SOLID design principles.

## Service-Oriented Architecture core components 
* **Services:** Self-contained, well-defined functionalities that are independent of any technology or vendor.
* **Loose Coupling:** Services have minimal dependencies on each other, allowing them to be updated or modified without affecting the overall application.
* **Reusability:** Components can be reused across different applications within an enterprise.
* **Enterprise Service Bus (ESB):** A, often, centralized component that manages communications, data transformation, and routing between services.
* **Service Consumer/Provider:** The consumer calls a service, which is delivered by the provider.

## SOLID design principles
* **Single Responsibility Principle (SRP):** A class should have only one reason to change, meaning it should have only one job.
* **Open-Closed Principle (OCP):** Software entities should be open for extension but closed for modification.
* **Liskov Substitution Principle (LSP):** Subtypes must be substitutable for their base types without altering the correctness of the program.
* **Interface Segregation Principle (ISP):** Clients should not be forced to depend on methods they do not use; many specific interfaces are better than one general-purpose interface.
* **Dependency Inversion Principle (DIP):** High-level modules should not depend on low-level modules; both should depend on abstractions.


# Game Concept

Quantum Pipelines is a puzzle-based educational game where players learn quantum programming by visually constructing quantum circuits.

Players interact with:

• 4 qubit lines represented visually  
• Bloch spheres showing qubit state rotations  
• Drag-and-drop quantum gates  
• A target probability distribution for measurement results  

Each player action dynamically generates a **quantum circuit**.

This circuit is programmatically constructed using **PennyLane**, translated into **OpenQASM**, and executed using **Quokka** as the backend.

The output is a **sample distribution of measurement results**.

The player wins when the measured distribution matches the target distribution within a statistical tolerance.

---

# Technology Stack

Backend
- Python
- PennyLane
- OpenQASM
- Quokka quantum backend
- FastAPI

Frontend
- Python UI or lightweight web UI or HTML
- Bloch sphere visualisation
- Drag-and-drop circuit builder

Other libraries
- NumPy
- JSON

---

# Architecture Requirements

The system should include components for:

1. Game UI rendering
2. Circuit builder logic
3. Circuit validation
4. Quantum circuit generation
5. QASM generation
6. Quantum execution (Quokka)
7. Measurement sampling
8. Distribution evaluation
9. Puzzle definition and loading
10. Game state management

The architecture must support **dynamic generation of circuits during gameplay**.

---

# Deliverables

Produce the following sections.

## 1. High-Level System Architecture

Explain the major subsystems:

- Frontend UI
- Game Engine
- Quantum Execution Layer
- Data & Puzzle Layer

Describe how data flows between them.

---

## 2. Component Architecture Diagram

Generate a **clear ASCII diagram** showing components and data flow.

Example style:

```
Player Input
│
▼
UI Layer
│
▼
Game Engine
│
├── Circuit Builder
├── Circuit Validator
└── Puzzle Manager
│
▼
Quantum Layer
├── PennyLane Circuit Generator
├── QASM Translator
└── Quokka Executor
│
▼
Measurement Analyzer
│
▼
Result Visualization
```

---

## 3. Core Data Structures

Define the main data models for:

- QubitLine
- QuantumGate
- PlayerCircuit
- PuzzleDefinition
- MeasurementDistribution

Provide example JSON representations.

---

## 4. Gameplay Execution Pipeline

Describe step-by-step what happens when a player places a gate:

1. Player action
2. Circuit update
3. QASM generation
4. Quantum execution
5. Measurement sampling
6. Distribution comparison
7. UI update

---

## 5. Team Roles

The team has **5 members**.

Assign architectural ownership based on these roles:

1. **Quantum Systems Lead**
2. **Backend / API Engineer**
3. **Frontend UI Engineer**
4. **Game Design & Puzzle Engineer**
5. **Integration & DevOps Engineer**

Explain what each role owns.

---

## 6. Epics and Stories

Create **8–10 epics** required to build the game.

For each epic include:

- Description
- Owner role
- List of user stories

Example format:

Epic: Circuit Builder

Owner: Frontend Engineer

Stories:
- Implement qubit line UI
- Drag-and-drop gate placement
- Gate snapping to circuit grid
- Multi-qubit gate connection logic

---

## 7. Suggested Milestone Plan

Provide a rough **4-week development plan**:

Week 1: Prototype foundation  
Week 2: Quantum pipeline integration  
Week 3: Gameplay mechanics  
Week 4: polish + presentation

---

# Important Constraints

The architecture must:

• support **dynamic circuit generation**  
• integrate **PennyLane and QASM**  
• execute circuits using **Quokka**  
• allow statistical evaluation of measurement distributions  
• remain simple enough for a student team to implement

Focus on **clarity and practicality rather than enterprise complexity.**