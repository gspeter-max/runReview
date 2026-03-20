# Plan: Fix Box vs. Gift (Path Confusion) Problem - Final

## Background & Motivation
The "Box vs. Gift" problem occurs when the `ArchitectureAgent` receives a raw filesystem path (the "box") instead of the actual file tree (the "gift"). We will normalize the output to remove UUIDs and provide a clear `Project Root/` structure to the LLM.

## Implementation Steps

### Step 1: Initialize Plan Document
- Store this plan in `docs/plans/2026-03-21-fix-box-vs-gift.md`.

### Step 2: Update `app/services/repo_service.py`
**Goal:** Normalize the root directory name in `get_file_structure` to remove UUIDs.
- **Before:** Shows the actual directory basename or skips the root.
- **After:** Shows `Project Root/` for the top-level directory.
- **Verification:** Call `get_file_structure` on a test directory and verify the output starts with `Project Root/`.

### Step 3: Update `app/agents/architecture_agent.py`
**Goal:** Ensure the agent generates the file structure before building the prompt.
- **Before:** Passes the raw `repo_path` to the prompt builder.
- **After:** Calls `self.repo_service.get_file_structure(repo_path)` and passes the result.
- **Verification:** Unit test mocking `provider.generate` to inspect the prompt content.

### Step 4: Update `app/prompts/architecture.py`
**Goal:** Add explicit instructions to ignore placeholder names.
- **Before:** General instructions about analyzing structure.
- **After:** Added: "If the root folder has a random ID name or UUID, ignore it and look at the content."
- **Verification:** Inspect the `ARCHITECTURE_SYSTEM_PROMPT` string.

## Final Verification
- Run full test suite.
- Specifically run: `./venv/bin/pytest tests/test_e2e_authentication_repo.py -v`.
- Ensure all API calls use `.env` (already handled by `Settings` class in `BaseAgent`).

## Migration & Rollback
- Rollback by reverting the 3 files to their previous git state.
