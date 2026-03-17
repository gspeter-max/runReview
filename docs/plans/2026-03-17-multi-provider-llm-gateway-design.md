# Multi-Provider LLM Gateway Design

**Date:** 2026-03-17
**Status:** Approved
**Topic:** Production-ready LLM orchestration using LiteLLM Router

## 1. Overview
Build a modular, production-ready LLM provider system (`llmProvider/`) that unifies 10+ free LLM services. The system prioritized high-speed models (Groq, Cerebras) and automatically fails over to high-context or general-purpose models (Gemini, GitHub, Mistral) if rate limits are hit.

## 2. Architecture
The system follows the **Adapter Pattern** with a **Central Orchestrator (Router)**.

### Directory Structure
- `app/llmProvider/`
    - `__init__.py`: Factory to initialize the router.
    - `base.py`: Abstract Base Class for all LLM clients.
    - `router.py`: LiteLLM Router configuration and lifecycle management.
    - `config.yaml`: Registry of all free models, providers, and their priority tiers.
    - `clients/`: Individual adapter classes for each provider.
        - `groq.py`, `gemini.py`, `cloudflare.py`, `github.py`, etc.

## 3. Component Details

### 3.1 YAML Configuration (`config.yaml`)
A registry that defines models and their "Tiers".
- **Tier 1 (Fast):** Groq, Cerebras, Together AI.
- **Tier 2 (Smart):** Gemini, DeepSeek (Reasoning), Claude (via GitHub).
- **Tier 3 (Backup):** Mistral, Cloudflare, Hugging Face.

### 3.2 The Router (`router.py`)
Utilizes `litellm.Router` to:
- Load configurations from `config.yaml`.
- Map all models to a single `model_name="code-analyzer"`.
- Handle `429 (Rate Limit)` and `500 (Internal Server Error)` with automatic retries and failover.

### 3.3 Client Adapters (`clients/`)
Each provider has a dedicated client class that handles:
- Provider-specific API base URLs (e.g., GitHub Models redirect).
- Custom headers or auth logic.
- Returning `litellm_params` to the Router.

## 4. Failover Strategy
1.  **Request received:** App calls `code-analyzer`.
2.  **Fast Path:** Router tries Tier 1 models first (Groq/Cerebras).
3.  **Failover:** If 429 received, Router instantly tries the next model in the same tier.
4.  **Escalation:** If Tier 1 is exhausted, it moves to Tier 2 (Gemini/Smart models).
5.  **Recovery:** Failed models are "cooled down" and reintroduced based on LiteLLM's retry logic.

## 5. Security & Environment
- All API keys are loaded via `Pydantic-Settings`.
- Keys are NEVER stored in `config.yaml` or checked into Git.
- The `.env` file serves as the secure secret store.
