import json
from typing import Any, Dict
from pathlib import Path
import pandas as pd
from src.config import settings
from datetime import datetime
def validate_json_output(output: str, expected_keys: list) -> Dict[str, Any]:
    """More robust JSON validation with fallback"""
    try:
        # Handle cases where LLM wraps JSON in markdown
        cleaned = output.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        # Parse JSON with fallback
        data = json.loads(cleaned) if cleaned.startswith('{') else {}
        return {k: data.get(k, False) for k in expected_keys}
    except:
        return {k: False for k in expected_keys}
def log_escalation(data: Dict[str, Any]) -> None:
    """Log escalations with guaranteed success"""
    try:
        Path(settings.ESCALATION_LOG_PATH).parent.mkdir(exist_ok=True, parents=True)
        
        # Prepare data with defaults
        record = {
            "timestamp": datetime.now().isoformat(),
            "subject": data.get("ticket", {}).get("subject", "UNKNOWN"),
            "description": data.get("ticket", {}).get("description", "UNKNOWN"),
            "category": data.get("classification", {}).get("category", "UNKNOWN"),
            "attempts": data.get("attempt", 0),
            "error": data.get("error", "No error recorded"),
            "feedback": data.get("review", {}).get("feedback", "No feedback")
        }
        
        # Write to CSV
        df = pd.DataFrame([record])
        header = not Path(settings.ESCALATION_LOG_PATH).exists()
        df.to_csv(settings.ESCALATION_LOG_PATH, mode='a', header=header, index=False)
    except Exception as e:
        # Fallback to print if CSV fails
        print(f"ESCALATION RECORD FAILED: {record}\nError: {str(e)}")

def prepare_retry_signal(state: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare retry signal based on current state."""
    if state['attempt'] >= settings.MAX_RETRY_ATTEMPTS:
        return {'should_retry': False}
    return {
        'should_retry': True,
        'feedback': state.get('review', {}).get('feedback', None)
    }