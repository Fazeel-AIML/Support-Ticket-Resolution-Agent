import sys
import os
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import SupportAgent
from src.core.schemas import Ticket

@pytest.fixture
def agent():
    return SupportAgent()

@pytest.fixture
def technical_ticket():
    return {
        "subject": "API not working",
        "description": "Getting 500 errors from the API"
    }

def test_agent_workflow(agent, technical_ticket):
    result = agent.process_ticket(technical_ticket)
    
    assert "draft" in result
    assert "review" in result
    assert isinstance(result["attempt"], int)
    
    if result["escalated"]:
        assert result["attempt"] > 1
    else:
        assert result["review"]["approved"] is True

def test_agent_retry_mechanism(agent, mocker):
    # Mock services to test retry logic
    mocker.patch(
        "src.services.review_draft",
        return_value={"approved": False, "feedback": "Needs improvement"}
    )
    
    ticket = {
        "subject": "Test",
        "description": "Test description"
    }
    result = agent.process_ticket(ticket)
    
    assert result["attempt"] == 2  # Initial + 1 retry
    assert result["escalated"] is True