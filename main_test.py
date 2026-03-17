import asyncio
import yaml
import os
from app.llmProvider.router import LLMRouter

async def test_providers():
    print(f"\n--- Testing API Keys in Main Environment ---")
    
    try:
        router = LLMRouter()
        print("Sending request to LLMRouter...")
        response = await router.generate("Say 'GATEWAY_SUCCESS' if you can read this.")
        print(f"Response: {response.strip()}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_providers())
