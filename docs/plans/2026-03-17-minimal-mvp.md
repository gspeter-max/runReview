# CodeAgent Professional Orchestration (SDK Pattern) Plan

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a production-grade agentic framework that mimics the **Claude Agent SDK**'s subagent spawning, context isolation, and parallel execution patterns—without using external frameworks.

**Architecture:** Hierarchical "Map-Reduce" orchestration. A **Coordinator** (Main Agent) analyzes the task and spawns **Specialized Experts** (Subagents) with isolated contexts and restricted toolsets.

---

### Task 1: Project Scaffolding & Logging (Resilient Foundation)

**Files:**
- Create: `pyproject.toml`
- Create: `app/core/logging.py`
- Create: `.env`

**Step 1: Implement `pyproject.toml` with Senior Dependencies**
*   `fastapi`, `uvicorn`, `gitpython`, `groq`, `structlog`, `tenacity`.

---

### Task 2: The Agent SDK (Core Definition & Isolation)

**Files:**
- Create: `app/sdk/agent.py`
- Create: `app/providers/groq.py`

**Step 1: Implement the `AgentDefinition` (Claude SDK Pattern)**
*   Define a Pydantic model for agents: `name`, `description`, `system_prompt`, `model`, and `allowed_tools`.
*   This ensures every subagent is an **isolated instance** with its own context window.

**Step 2: Implement `AgentReport` & `Finding` Schemas**
*   Standardize how subagents "phone home" their results.

---

### Task 3: The Coordinator (Map-Reduce Planner)

**Files:**
- Create: `app/agents/coordinator.py`

**Step 1: Implement the "Map" Phase (Dynamic Planning)**
*   Coordinator reads the user prompt and generates a **JSON Task List**.
*   Pattern: "I need a Security Expert for auth/ and a Quality Expert for service/."

---

### Task 4: The Parallel Orchestrator (Subagent Spawning)

**Files:**
- Create: `app/services/orchestrator.py`

**Step 1: Implement "Context Siphoning" Execution**
*   Uses `asyncio.gather()` to launch subagents.
*   Each subagent performs heavy lifting and returns only a **concise summary** + **JSON findings**.
*   *Why:* This keeps the Coordinator's context clean, preventing "context bloat."

---

### Task 5: The Meta-Judge (The "Reduce" Phase)

**Files:**
- Create: `app/agents/meta_judge.py`
- Create: `app/main.py`

**Step 1: Implement Result Aggregation**
*   Meta-Judge reviews all subagent summaries.
*   Calculates a final **Health Score (0-100)**.
*   Generates a final Executive Summary.

**Step 2: API Integration**
*   `POST /analyze` -> `Coordinator` -> `Orchestrator` -> `Subagents` -> `Meta-Judge` -> `Rich Response`.
