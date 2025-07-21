from langchain_core.prompts import ChatPromptTemplate
from src.core.schemas import Ticket, Draft, Review
from src.core.llm_service import llm_service
from src.core.utils import validate_json_output
import json

def review_draft(ticket: Ticket, draft: Draft) -> Review:
    """Robust review with JSON fallback handling"""
    prompt_template = """[SYSTEM]
    Evaluate this support response. Return JSON with:
    - "approved": boolean
    - "feedback": string
    
    [TICKET]
    {ticket_details}
    
    [CONTEXT]
    {context}
    
    [DRAFT]
    {draft_content}
    
    [OUTPUT FORMAT]
    {{"approved": false, "feedback": "Your response here"}}"""
    
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm_service.get_llm("review")
    
    try:
        result = chain.invoke({
            "ticket_details": f"SUBJECT: {ticket['subject']}\nDESCRIPTION: {ticket['description']}",
            "context": "\n".join(draft["context_used"]),
            "draft_content": draft["content"]
        }).content

        # Robust JSON extraction
        json_str = result.replace("```json", "").replace("```", "").strip()
        if not json_str.startswith("{"):
            json_str = "{" + json_str.split("{", 1)[-1]
        
        validated = validate_json_output(json_str, ["approved"])
        return {
            "approved": validated.get("approved", False),
            "feedback": validated.get("feedback", "Automatic rejection due to policy violation")
        }
        
    except Exception as e:
        # Fallback for complete failures
        return {
            "approved": False,
            "feedback": f"Review system error: {str(e)}"
        }