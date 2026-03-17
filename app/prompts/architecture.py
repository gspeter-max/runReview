"""
Prompts for the Architecture Agent.
These are designed to extract maximum value from the LLM regarding project structure,
tech stack, and architectural patterns.
"""

ARCHITECTURE_SYSTEM_PROMPT = """You are an expert software architect.
Your task is to analyze the provided directory structure of a software project.
Based on the structure, file names, and common conventions, please:
1. Identify the likely tech stack (languages, frameworks, tools).
2. Describe the overall architectural pattern (e.g., MVC, Hexagonal, Microservices, Monolith, Clean Architecture).
3. Highlight any notable organization practices or potential structural issues.

Provide a concise, professional, and structured analysis.
"""

def build_architecture_prompt(structure: str) -> str:
    """
    Builds the user prompt containing the project structure to be analyzed.
    """
    return f"""Please analyze the following project structure:

```text
{structure}
```

Provide your architectural analysis based on the structure above.
"""
