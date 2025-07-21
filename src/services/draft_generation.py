from langchain_core.prompts import ChatPromptTemplate
from src.core.schemas import Ticket, Context, Draft
from src.core.llm_service import llm_service

def generate_draft(ticket: Ticket, context: Context) -> Draft:
    """Generate support response draft."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a support agent. Draft a response using:
        
        Context:
        {context}

        Guidelines:
        - Be professional and empathetic
        - Only use verified information
        - Never promise unavailable solutions
        - Keep responses under 300 words"""),
        ("human", "Ticket Subject: {subject}\nDescription: {description}")
    ])
    
    chain = prompt | llm_service.get_llm("draft")
    response = chain.invoke({
        "context": "\n".join(context["documents"]),
        "subject": ticket["subject"],
        "description": ticket["description"]
    }).content
    
    return {
        "content": response,
        "context_used": context["documents"]
    }