from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
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

class AgentDefinition(BaseModel):
    name: str
    description: str
    system_prompt: str
    model: str = "code-analyzer" # Default model for our router
    allowed_tools: List[str] = []
