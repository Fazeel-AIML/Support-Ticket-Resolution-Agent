from langchain_core.prompts import ChatPromptTemplate
from src.core.schemas import Ticket, Draft, Review
from src.core.llm_service import llm_service
from src.core.utils import validate_json_output
import json

def review_draft(ticket: Ticket, draft: Draft) -> Review:
    """Review draft response for quality and compliance."""
    # Simplified prompt template without variable conflicts
    prompt_template = """
    Review this support ticket response against these criteria:
    1. Accuracy (matches provided context)
    2. Policy compliance
    3. Professional tone
    4. Problem resolution
    
    Ticket Details:
    {ticket_details}
    
    Context Used:
    {context}
    
    Draft Response:
    {draft_content}
    
    Respond in strict JSON format with these keys:
    {{
        "approved": boolean,
        "feedback": string (optional)
    }}
    """
    
    prompt = ChatPromptTemplate.from_template(prompt_template)
    
    chain = prompt | llm_service.get_llm("review")
    
    result = chain.invoke({
        "ticket_details": f"Subject: {ticket['subject']}\nDescription: {ticket['description']}",
        "context": "\n".join(draft["context_used"]),
        "draft_content": draft["content"]
    }).content
    
    # Clean the output (sometimes LLMs add markdown code blocks)
    cleaned_result = result.strip().replace("```json", "").replace("```", "").strip()
    
    validated = validate_json_output(cleaned_result, ["approved", "feedback"])
    return {
        "approved": validated["approved"],
        "feedback": validated.get("feedback")
    }