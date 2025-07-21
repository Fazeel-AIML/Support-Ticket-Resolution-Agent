from typing import TypedDict, List, Literal, Optional
from dataclasses import dataclass

class Ticket(TypedDict):
    subject: str
    description: str

class Classification(TypedDict):
    category: Literal["Billing", "Technical", "Security", "General"]
    confidence: float

class Context(TypedDict):
    category: str
    documents: List[str]

class Draft(TypedDict):
    content: str
    context_used: List[str]

class Review(TypedDict):
    approved: bool
    feedback: Optional[str]

class AgentState(TypedDict):
    ticket: Ticket
    classification: Optional[Classification]
    context: Optional[Context]
    draft: Optional[Draft]
    review: Optional[Review]
    attempt: int
    escalated: bool

@dataclass
class RetrySignal:
    should_retry: bool
    feedback: Optional[str] = None