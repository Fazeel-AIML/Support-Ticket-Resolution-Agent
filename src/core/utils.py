import json
from typing import Any, Dict
from pathlib import Path
import pandas as pd
from src.config import settings

def validate_json_output(output: str, expected_keys: list) -> Dict[str, Any]:
    """Validate LLM JSON output and convert to dict."""
    try:
        data = json.loads(output)
        if not all(key in data for key in expected_keys):
            raise ValueError(f"Missing required keys: {expected_keys}")
        return data
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")

def log_escalation(data: Dict[str, Any]) -> None:
    """Log escalated tickets to CSV."""
    Path(settings.ESCALATION_LOG_PATH).parent.mkdir(exist_ok=True, parents=True)
    
    df = pd.DataFrame([data])
    if not Path(settings.ESCALATION_LOG_PATH).exists():
        df.to_csv(settings.ESCALATION_LOG_PATH, index=False)
    else:
        df.to_csv(settings.ESCALATION_LOG_PATH, mode='a', header=False, index=False)

def prepare_retry_signal(state: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare retry signal based on current state."""
    if state['attempt'] >= settings.MAX_RETRY_ATTEMPTS:
        return {'should_retry': False}
    return {
        'should_retry': True,
        'feedback': state.get('review', {}).get('feedback', None)
    }