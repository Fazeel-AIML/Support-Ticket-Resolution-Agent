from langchain_core.prompts import ChatPromptTemplate
from src.core.schemas import Ticket, Classification
from src.config import settings
from src.core.llm_service import llm_service

def classify_ticket(ticket: Ticket) -> Classification:
    """Classify support ticket into category."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Classify this ticket into exactly one category:
Billing - Payments, subscriptions, invoices
Technical - App errors, bugs, technical issues
Security - Account security, phishing, 2FA
General - Other questions, feedback, non-urgent

Respond ONLY with the category name."""),
        ("human", "Subject: {subject}\nDescription: {description}")
    ])
    
    chain = prompt | llm_service.get_llm("classification")
    category = chain.invoke({
        "subject": ticket["subject"],
        "description": ticket["description"]
    }).content
    
    return {
        "category": category.strip(),
        "confidence": 1.0
    }