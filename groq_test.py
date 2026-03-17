import asyncio
import yaml
import os
from app.llmProvider.router import LLMRouter

async def test_groq():
    print(f"\n--- Testing Refactored Environment Loading ---")
    config = {
        "providers": [
            {"name": "groq", "model": "groq/llama-3.3-70b-versatile"}
        ]
    }
    with open("groq_test_config.yaml", "w") as f:
        yaml.dump(config, f)
        
    try:
        # Should now load from .env correctly without hardcoding
        router = LLMRouter(config_path="groq_test_config.yaml")
        print("Sending request via Groq...")
        response = await router.generate("Say 'REFACTORED_SUCCESS' if you can read this.")
        print(f"Response: {response.strip()}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists("groq_test_config.yaml"):
            os.remove("groq_test_config.yaml")

if __name__ == "__main__":
    asyncio.run(test_groq())
