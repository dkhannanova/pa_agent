from pydantic import BaseModel, Field
from typing import Literal

class ClarifyingQuestion(BaseModel):
    id: str
    question: str

class PlanStep(BaseModel):
    step: int
    goal: str

class Finding(BaseModel):
    finding: str
    confidence: Literal["low", "medium", "high"] = "medium"
    evidence: list[str] = Field(default_factory=list)

class AgentResponse(BaseModel):
    session_id: str
    clarifying_questions: list[ClarifyingQuestion] = Field(default_factory=list)
    analysis_plan: list[PlanStep] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    next_step: str | None = None
