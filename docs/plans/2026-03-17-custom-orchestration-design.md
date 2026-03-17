# CodeAgent Custom Orchestration Design (Parallel Planner)

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:writing-plans to implement this design task-by-task.

**Goal:** Implement a model-driven, hierarchical agent orchestration system that dynamically plans, spawns, and judges specialized subagents for codebase analysis.

**Architecture:** A custom "Planner -> Spawner -> Worker -> Judge" pattern using Python's `asyncio` for parallel execution and a strict JSON-driven task interface.

**Tech Stack:**
- Python 3.10+
- FastAPI
- Groq (LLM)
- Pydantic (Schema validation)
- Asyncio (Concurrency)

---

## 1. The Dynamic Planner (LLM-Driven)
The **Manager** (The Parent) initiates the analysis by calling a **Planner Agent**. 

- **Input:** User prompt (e.g., "Analyze this repository for security and quality").
- **Output:** A structured JSON list of tasks.
- **Why:** This makes the system "dynamic." If the user only asks for security, only the security agent is recruited.

### Task Schema:
```json
[
  {
    "task_id": "T1",
    "agent": "security",
    "instruction": "Analyze auth/ module for hardcoded secrets."
  },
  {
    "task_id": "T2",
    "agent": "quality",
    "instruction": "Check service/ layer for high cyclomatic complexity."
  }
]
```

---

## 2. The Agent Registry & Worker Interface
The **Orchestrator** (Python script) maps the "agent" field to a specialized class.

- **The Registry:** A dictionary mapping agent names to their respective classes.
- **The Worker Contract:** Every subagent MUST implement an `analyze(repo_path, instruction)` method.
- **The Standard Output:** Every subagent MUST return a JSON finding list with a standardized schema (Title, Severity, File, Suggestion).

---

## 3. Parallel Spawner (Async Execution)
The Orchestrator parses the Planner's JSON and "spawns" (initiates) all subagents simultaneously.

- **Concurrency:** Uses `asyncio.gather(*tasks)` to run all analysis in parallel.
- **Isolation:** Each agent runs its own specialized prompt and logic without interfering with others.
- **Timeout & Error Handling:** The Spawner manages timeouts for individual agents to ensure one slow agent doesn't hang the entire process.

---

## 4. The Meta-Judge (Result Aggregation)
Once all subagents return their standardized JSON forms, the **Parent Manager** performs a final "Judgment" pass.

- **Deduplication:** Merges overlapping findings from different agents.
- **Scoring:** Calculates an overall "Codebase Health Score" (0-100) based on weighted findings.
- **Executive Summary:** A final LLM pass to synthesize all findings into a 1-paragraph human-readable summary.
- **Final Report:** Returns the "Rich Report" (JSON) to the user via the FastAPI endpoint.

---

## 5. Sequence Diagram
1. **User** -> `POST /analyze` -> **Manager**
2. **Manager** -> **Planner Agent** (What should I do?)
3. **Planner Agent** -> **Manager** (Run Security and Quality tasks)
4. **Manager** -> **Security Agent** & **Quality Agent** (Run simultaneously)
5. **Security Agent** & **Quality Agent** -> **Manager** (Individual JSON Reports)
6. **Manager** -> **Meta-Judge** (Merge and Score)
7. **Manager** -> **User** (Final Rich Report)
