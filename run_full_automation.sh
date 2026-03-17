#!/bin/bash
set -e # Exit immediately if any command fails

# Multi-Provider LLM Gateway: Full E2E Automation Script
# This script verifies the complete flow from cloning to multi-tier LLM analysis.

# ⚠️ SECURITY: API Keys must be set in your terminal or a .env file.
# Do NOT hardcode keys in this script.

echo "🚀 Starting Full E2E Automation..."
echo "Checking for required environment variables..."

REQUIRED_VARS=("GROQ_API_KEY" "GEMINI_API_KEY" "GITHUB_API_KEY")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var is not set. Please export it before running."
        exit 1
    fi
done

echo "-----------------------------------"

# 2. Run standard tests first
echo "Step 1: Running unit and integration tests..."
./venv/bin/pytest tests/test_config.py tests/test_llm_provider.py tests/test_agents.py tests/test_coordinator.py tests/test_services.py tests/test_orchestration_full.py tests/test_main.py tests/test_api_integration.py
echo "✅ Unit tests passed."

# 3. Run the live E2E test
echo "Step 2: Running Live E2E analysis on 'authentication' repo..."
./venv/bin/python tests/test_e2e_authentication_repo.py

echo "-----------------------------------"
echo "🎉 ALL SYSTEMS GO: Full E2E verification successful!"
