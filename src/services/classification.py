from langchain_core.prompts import ChatPromptTemplate
from src.core.schemas import Ticket, Classification
from src.config import settings
from src.core.llm_service import llm_service

def classify_ticket(ticket: Ticket) -> Classification:
    """Classify ticket with empty input handling"""
    if not ticket["subject"] and not ticket["description"]:
        return {"category": "General", "confidence": 0.0}
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Classify this ticket into one category:
        - Billing
        - Technical  
        - Security
        - General
        Return ONLY the category name"""),
        ("human", "Subject: {subject}\nDescription: {description}")
    ])
    
    try:
        chain = prompt | llm_service.get_llm("classification")
        category = chain.invoke({
            "subject": ticket["subject"] or "(No subject)",
            "description": ticket["description"] or "(No description)"
        }).content.strip()
        return {"category": category, "confidence": 1.0}
    except:
        return {"category": "General", "confidence": 0.0}