from langgraph.graph import StateGraph, END
from src.core.schemas import AgentState
from src.services import (
    classify_ticket,
    retrieve_context,
    generate_draft,
    review_draft
)
from src.core.utils import prepare_retry_signal, log_escalation

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

    # Implement all required methods:
    def _classify(self, state: AgentState) -> AgentState:
        state["classification"] = classify_ticket(state["ticket"])
        return state

    def _retrieve(self, state: AgentState) -> AgentState:
        query = f"{state['ticket']['subject']}\n{state['ticket']['description']}"
        state["context"] = retrieve_context(
            state["classification"]["category"],
            query
        )
        return state

    def _generate_draft(self, state: AgentState) -> AgentState:
        state["draft"] = generate_draft(state["ticket"], state["context"])
        return state

    def _review(self, state: AgentState) -> AgentState:
        state["review"] = review_draft(state["ticket"], state["draft"])
        state["attempt"] = state.get("attempt", 0) + 1
        return state

    def _escalate(self, state: AgentState) -> AgentState:
        log_escalation({
            "subject": state["ticket"]["subject"],
            "description": state["ticket"]["description"],
            "category": state["classification"]["category"],
            "attempts": state["attempt"],
            "draft": state["draft"]["content"],
            "feedback": state["review"]["feedback"]
        })
        state["escalated"] = True
        return state

    def _should_retry(self, state: AgentState) -> str:
        signal = prepare_retry_signal(state)
        if state["review"]["approved"]:
            return "approve"
        return "retry" if signal["should_retry"] else "escalate"

    def process_ticket(self, ticket: dict):
        """Public method to process tickets"""
        initial_state = {
            "ticket": ticket,
            "classification": None,
            "context": None,
            "draft": None,
            "review": None,
            "attempt": 0,
            "escalated": False
        }
        return self.graph.invoke(initial_state)