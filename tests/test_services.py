import sys
import os
from pathlib import Path
import pytest
# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services import (
    classify_ticket,
    retrieve_context,
    generate_draft,
    review_draft
)
from src.core.schemas import Ticket

@pytest.fixture
def sample_ticket():
    return {
        "subject": "Login issues",
        "description": "I can't login to my account"
    }

def test_classification(sample_ticket):
    result = classify_ticket(sample_ticket)
    assert result["category"] in ["Billing", "Technical", "Security", "General"]
    assert 0 <= result["confidence"] <= 1

def test_context_retrieval():
    context = retrieve_context("Technical", "login problems")
    assert isinstance(context["documents"], list)
    assert len(context["documents"]) > 0

def test_draft_generation(sample_ticket):
    context = {"category": "Technical", "documents": ["Test document"]}
    draft = generate_draft(sample_ticket, context)
    assert isinstance(draft["content"], str)
    assert len(draft["content"]) > 0

def test_draft_review(sample_ticket):
    draft = {
        "content": "Please try clearing your cache",
        "context_used": ["Clear cache to resolve login issues"]
    }
    review = review_draft(sample_ticket, draft)
    assert isinstance(review["approved"], bool)
    assert isinstance(review["feedback"], (str, type(None)))