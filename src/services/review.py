from langchain_core.prompts import ChatPromptTemplate
from src.core.schemas import Ticket, Draft, Review
from src.core.llm_service import llm_service
from src.core.utils import validate_json_output
import json

POLICY_RULES = {
    "Billing": [
        "Do not promise refunds",
        "Do not modify payment terms",
        "Escalate credit requests"
    ],
    "Security": [
        "Do not share credentials",
        "Escalate account breaches",
        "Require 2FA verification"
    ],
    "Technical": [
        "Do not guarantee fixes",
        "Escalate data loss cases",
        "Provide troubleshooting steps"
    ],
    "General": [
        "Maintain professional tone",
        "Escalate legal inquiries",
        "Provide clear next steps"
    ]
}

def review_draft(ticket: Ticket, draft: Draft) -> Review:
    """Strict policy-compliant review with category-specific rules"""
    category = ticket.get("classification", {}).get("category", "General")
    
    prompt_template = """[INSTRUCTIONS]
    As a support policy enforcer, evaluate this response against {category} policies:
    {policy_rules}
    
    [TICKET]
    Subject: {subject}
    Description: {description}
    
    [DRAFT RESPONSE]
    {draft_content}
    
    [REQUIREMENTS]
    1. Check for policy violations
    2. Assess professionalism
    3. Verify context usage
    
    Return JSON with:
    - approved: boolean
    - feedback: string (if rejected)
    - violations: list (if any)
    
    [EXAMPLE RESPONSE]
    {{
        "approved": false,
        "feedback": "Violates policy rule 1",
        "violations": ["Do not promise refunds"]
    }}"""
    
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm_service.get_llm("review")
    
    try:
        result = chain.invoke({
            "category": category,
            "policy_rules": "\n- ".join(POLICY_RULES.get(category, [])),
            "subject": ticket["subject"],
            "description": ticket["description"],
            "draft_content": draft["content"]
        }).content
        
        # Extract JSON from response
        json_str = result[result.find("{"):result.rfind("}")+1]
        review = json.loads(json_str)
        
        # Auto-reject if any violations found
        if review.get("violations"):
            review["approved"] = False
            
        return {
            "approved": review.get("approved", False),
            "feedback": review.get("feedback", "Policy check completed"),
            "violations": review.get("violations", [])
        }
        
    except Exception as e:
        return {
            "approved": False,
            "feedback": f"Review system error: {str(e)}",
            "violations": ["System failure"]
        }