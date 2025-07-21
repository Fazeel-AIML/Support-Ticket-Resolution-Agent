from langgraph.graph import StateGraph, END
from src.core.schemas import AgentState
from src.services import (
    classify_ticket,
    retrieve_context,
    generate_draft,
    review_draft
)
from src.core.utils import prepare_retry_signal, log_escalation
from typing import Optional
import logging
from src.config.settings import Settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupportAgent:
    def __init__(self):
        self.workflow = StateGraph(AgentState)
        self._build_workflow()
        self.graph = self.workflow.compile()
    
    def _build_workflow(self):
        """Construct the LangGraph workflow with all required nodes"""
        # Add all nodes with their corresponding methods
        self.workflow.add_node("classify", self._classify)
        self.workflow.add_node("retrieve", self._retrieve)
        self.workflow.add_node("draft", self._generate_draft)
        self.workflow.add_node("review", self._review)
        self.workflow.add_node("escalate", self._escalate)

        # Set edges
        self.workflow.set_entry_point("classify")
        self.workflow.add_edge("classify", "retrieve")
        self.workflow.add_edge("retrieve", "draft")
        self.workflow.add_edge("draft", "review")
        
        # Conditional edges
        self.workflow.add_conditional_edges(
            "review",
            self._should_retry,
            {
                "approve": END,
                "retry": "retrieve",
                "escalate": "escalate"
            }
        )
        self.workflow.add_edge("escalate", END)

    def _classify(self, state: AgentState) -> AgentState:
        try:
            state["classification"] = classify_ticket(state["ticket"])
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            state["classification"] = {"category": "General", "confidence": 0.0}
        return state

    def _retrieve(self, state: AgentState) -> AgentState:
        try:
            query = f"{state['ticket']['subject']}\n{state['ticket']['description']}"
            state["context"] = retrieve_context(
                state["classification"]["category"],
                query
            )
        except Exception as e:
            logger.error(f"Context retrieval failed: {str(e)}")
            state["context"] = {"category": state["classification"]["category"], "documents": []}
        return state

    def _generate_draft(self, state: AgentState) -> AgentState:
        try:
            state["draft"] = generate_draft(state["ticket"], state["context"])
        except Exception as e:
            logger.error(f"Draft generation failed: {str(e)}")
            state["draft"] = {
                "content": "We're experiencing technical difficulties. Please contact support directly.",
                "context_used": []
            }
        return state

    def _review(self, state: AgentState) -> AgentState:
        """Enhanced review with policy enforcement"""
        review_result = review_draft(state["ticket"], state["draft"])
        
        state["review"] = {
            "approved": review_result["approved"],
            "feedback": review_result["feedback"],
            "violations": review_result.get("violations", [])
        }
        
        # Auto-escalate for certain violations
        if any(v in Settings.POLICY_ESCALATION_TRIGGERS for v in review_result.get("violations", [])):
            state["escalated"] = True
            
        state["attempt"] = state.get("attempt", 0) + 1
        return state

    def _escalate(self, state: AgentState) -> AgentState:
        try:
            log_escalation({
                "subject": state["ticket"]["subject"],
                "description": state["ticket"]["description"],
                "category": state["classification"].get("category", "Unknown"),
                "attempts": state.get("attempt", 0),
                "draft": state.get("draft", {}).get("content", "No draft generated"),
                "feedback": state.get("review", {}).get("feedback", "No feedback available")
            })
        except Exception as e:
            logger.error(f"Escalation logging failed: {str(e)}")
        state["escalated"] = True
        return state

    def _should_retry(self, state: AgentState) -> str:
        """Strict retry logic"""
        if state.get("escalated", False):
            return "escalate"
            
        if not state.get("review"):
            return "escalate"
            
        if state["review"].get("approved", False):
            return "approve"
            
        return "retry" if state.get("attempt", 0) < 2 else "escalate"
            
        return "retry" if state.get("attempt", 0) < 1 else "escalate"  # Only 1 retry
    def process_ticket(self, ticket: dict) -> dict:
        """Process tickets with empty input handling"""
        # Validate input
        if not isinstance(ticket, dict):
            ticket = {"subject": "INVALID", "description": str(ticket)}
        
        subject = str(ticket.get('subject', '')).strip()
        description = str(ticket.get('description', '')).strip()
        
        # Immediate escalation for empty tickets
        if not subject and not description:
            error_state = {
                "ticket": {"subject": "(empty)", "description": "(empty)"},
                "classification": {"category": "General", "confidence": 0.0},
                "context": None,
                "draft": None,
                "review": None,
                "attempt": 0,
                "escalated": True,
                "error": "Empty ticket content"
            }
            self._escalate(error_state)
            return error_state
        
        # Normal processing
        initial_state = {
            "ticket": {"subject": subject, "description": description},
            "classification": None,
            "context": None,
            "draft": None,
            "review": None,
            "attempt": 0,
            "escalated": False
        }
        
        try:
            result = self.graph.invoke(initial_state)
            return result
        except Exception as e:
            error_state = {
                **initial_state,
                "error": str(e),
                "escalated": True
            }
            self._escalate(error_state)
            return error_state

    def _handle_invalid_ticket(self, ticket: dict) -> dict:
        """Handle completely invalid ticket structure"""
        error_state = {
            "ticket": {"subject": "INVALID", "description": str(ticket)},
            "classification": {"category": "General", "confidence": 0.0},
            "context": {"category": "General", "documents": []},
            "draft": {"content": "Invalid ticket format", "context_used": []},
            "review": {"approved": False, "feedback": "Invalid input format"},
            "attempt": 0,
            "escalated": True,
            "error": "Invalid ticket structure"
        }
        self._escalate(error_state)
        return error_state

    def _handle_empty_ticket(self, state: dict) -> dict:
        """Handle empty ticket content"""
        error_state = {
            **state,
            "classification": {"category": "General", "confidence": 0.0},
            "draft": {"content": "Empty ticket received", "context_used": []},
            "review": {"approved": False, "feedback": "No content provided"},
            "escalated": True
        }
        self._escalate(error_state)
        return error_state

    def _handle_processing_error(self, state: dict, error: Exception) -> dict:
        """Handle processing failures"""
        error_state = {
            **state,
            "classification": {"category": "General", "confidence": 0.0},
            "draft": {"content": "Processing error", "context_used": []},
            "review": {"approved": False, "feedback": str(error)},
            "escalated": True,
            "error": "Processing failed"
        }
        self._escalate(error_state)
        return error_state