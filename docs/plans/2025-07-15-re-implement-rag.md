# Production Codebase RAG Implementation Plan

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Re-implement the Production Codebase RAG system based on `rag_plan.md`, integrating it into the `app/rag` directory and ensuring all tests pass.

**Architecture:** A modular RAG pipeline consisting of Scanner, Chunker (AST-aware), Context Generator (Contextual Retrieval), Embedder, Storage (LanceDB), and Retrieval (Hybrid + Reranking) components.

**Tech Stack:** Python 3.11+, LanceDB, PyArrow, Anthropic (Claude), OpenAI, Tiktoken, Pydantic, structlog, tree-sitter, tantivy.

---

### Task 1: Update Dependencies and Environment

**Files:**
- Modify: `pyproject.toml`
- Create: `.env.example` (copy from `rag_plan.md`)

**Step 1: Add missing dependencies to `pyproject.toml`**
**Step 2: Create `.env.example`**
**Step 3: Run `pip install -e .` to install new dependencies**

---

### Task 2: Implement Utilities

**Files:**
- Create: `app/rag/utils/__init__.py`
- Create: `app/rag/utils/hashing.py`
- Create: `app/rag/utils/logger.py`
- Create: `app/rag/utils/tokens.py`

**Step 1: Implement `hashing.py`**
**Step 2: Implement `logger.py`**
**Step 3: Implement `tokens.py`**
**Step 4: Implement `__init__.py`**

---

### Task 3: Implement Configuration

**Files:**
- Create: `app/rag/config/__init__.py`
- Create: `app/rag/config/settings.py`
- Create: `app/rag/configs/settings.yaml`
- Create: `app/rag/configs/logging.yaml`

**Step 1: Implement `settings.py` (adjusting package names to `app.rag`)**
**Step 2: Create YAML config files**
**Step 3: Implement `__init__.py`**

---

### Task 4: Implement Ingestion (Scanner & Validators)

**Files:**
- Create: `app/rag/ingestion/__init__.py`
- Create: `app/rag/ingestion/scanner.py`
- Create: `app/rag/ingestion/validators.py`

**Step 1: Implement `validators.py`**
**Step 2: Implement `scanner.py`**
**Step 3: Implement `__init__.py`**

---

### Task 5: Implement Parsers

**Files:**
- Create: `app/rag/ingestion/parsers/__init__.py`
- Create: `app/rag/ingestion/parsers/base.py`
- Create: `app/rag/ingestion/parsers/python_parser.py`
- Create: `app/rag/ingestion/parsers/javascript_parser.py`
- Create: `app/rag/ingestion/parsers/generic_parser.py`
- Create: `app/rag/ingestion/parsers/factory.py`

**Step 1: Implement base and generic parsers**
**Step 2: Implement Python and JS/TS parsers**
**Step 3: Implement factory and init**

---

### Task 6: Implement Chunking

**Files:**
- Create: `app/rag/chunking/__init__.py`
- Create: `app/rag/chunking/models.py`
- Create: `app/rag/chunking/base.py`
- Create: `app/rag/chunking/strategies.py`
- Create: `app/rag/chunking/code_chunker.py`

**Step 1: Implement models and base**
**Step 2: Implement strategies**
**Step 3: Implement code_chunker and init**

---

### Task 7: Implement Contextual Retrieval

**Files:**
- Create: `app/rag/context/__init__.py`
- Create: `app/rag/context/prompts.py`
- Create: `app/rag/context/context_generator.py`
- Create: `app/rag/context/contextual_retrieval.py`

**Step 1: Implement prompts**
**Step 2: Implement context_generator**
**Step 3: Implement contextual_retrieval and init**

---

### Task 8: Implement Embedding

**Files:**
- Create: `app/rag/embedding/__init__.py`
- Create: `app/rag/embedding/base.py`
- Create: `app/rag/embedding/openai_embedder.py`
- Create: `app/rag/embedding/voyageai_embedder.py`
- Create: `app/rag/embedding/factory.py`

**Step 1: Implement base and providers**
**Step 2: Implement factory and init**

---

### Task 9: Implement Storage (LanceDB)

**Files:**
- Create: `app/rag/storage/__init__.py`
- Create: `app/rag/storage/models.py`
- Create: `app/rag/storage/lancedb_store.py`

**Step 1: Implement models**
**Step 2: Implement lancedb_store**
**Step 3: Implement init**

---

### Task 10: Implement Retrieval

**Files:**
- Create: `app/rag/retrieval/__init__.py`
- Create: `app/rag/retrieval/retriever.py`
- Create: `app/rag/retrieval/reranker.py`
- Create: `app/rag/retrieval/hybrid.py`

**Step 1: Implement hybrid and reranker**
**Step 2: Implement retriever**
**Step 3: Implement init**

---

### Task 11: Implement Pipelines and Main Entry Point

**Files:**
- Create: `app/rag/pipeline/__init__.py`
- Create: `app/rag/pipeline/ingestion_pipeline.py`
- Create: `app/rag/pipeline/query_pipeline.py`
- Create: `app/rag/main.py`

**Step 1: Implement pipelines**
**Step 2: Implement main.py**
**Step 3: Implement init**

---

### Task 12: Implement Tests

**Files:**
- Create: `tests/rag/conftest.py`
- Create: `tests/rag/unit/test_scanner.py`
- Create: `tests/rag/unit/test_chunking.py`
- Create: `tests/rag/unit/test_context.py`
- Create: `tests/rag/unit/test_storage.py`
- Create: `tests/rag/unit/test_embedding.py`
- Create: `tests/rag/integration/test_ingestion_pipeline.py`

**Step 1: Implement conftest**
**Step 2: Implement unit tests**
**Step 3: Implement integration tests**

---

### Task 13: Scripts and Final Verification

**Files:**
- Create: `scripts/rag/ingest.py`
- Create: `scripts/rag/query.py`

**Step 1: Create scripts**
**Step 2: Run all tests**
**Step 3: Verify with sample ingestion**
