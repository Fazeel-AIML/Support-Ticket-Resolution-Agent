from typing import Dict, List
from dataclasses import dataclass
from src.core.schemas import Ticket

@dataclass
class Conversation:
    ticket: Ticket
    history: List[Dict[str, str]]
    
class AgentMemory:
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
    
    def add_interaction(self, ticket_id: str, role: str, content: str):
        if ticket_id not in self.conversations:
            raise ValueError("Ticket not initialized")
        self.conversations[ticket_id].history.append({
            "role": role,
            "content": content
        })
    
    def get_conversation(self, ticket_id: str) -> Conversation:
        return self.conversations.get(ticket_id)
    
    def initialize_conversation(self, ticket: Ticket) -> str:
        import uuid
        ticket_id = str(uuid.uuid4())
        self.conversations[ticket_id] = Conversation(
            ticket=ticket,
            history=[]
        )
        return ticket_id

# Singleton instance
memory = AgentMemory()