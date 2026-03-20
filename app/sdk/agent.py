from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any, Dict, Literal
from enum import Enum

class Severity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class Finding(BaseModel):
    title: str
    severity: Severity
    file_path: str
    description: str
    suggestion: str

class AgentReport(BaseModel):
    agent_name: str
    findings: List[Finding] = []
    summary: str
    raw_output: Optional[str] = None

class AgentTask(BaseModel):
    task_id: str
    agent: str
    instruction: str
    context_files: List[str] = []
    model_priority: Literal["fast", "medium", "reasoning"] = "medium"

    @field_validator("model_priority", mode="before")
    @classmethod
    def validate_model_priority(cls, v: Any) -> str:
        if not isinstance(v, str):
            return "medium"
        
        v_lower = v.lower().strip()
        valid_groups = ["fast", "medium", "reasoning"]
        if v_lower not in valid_groups:
            return "medium"
        return v_lower


class AgentDefinition(BaseModel):
    name: str
    description: str
    system_prompt: str
    model: str = "code-analyzer" # Default model for our router
    allowed_tools: List[str] = []
