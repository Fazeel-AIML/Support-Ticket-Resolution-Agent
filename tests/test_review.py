from src.services.review import review_draft

test_ticket = {
    "subject": "Login issue",
    "description": "Can't access my account"
}

test_draft = {
    "content": "Please try clearing your browser cache and cookies.",
    "context_used": [
        "For login issues, first try clearing browser cache",
        "Check if cookies are enabled for our domain"
    ]
}

result = review_draft(test_ticket, test_draft)