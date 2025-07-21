import os
from dotenv import load_dotenv
from typing import Literal

load_dotenv()

class Settings:
    
    LLM_PROVIDER: Literal["groq", "openai"] = "groq"  # Updated to prioritize Groq
    GROQ_MODEL: str = "llama3-8b-8192"  # Default Groq model
    OPENAI_MODEL: str = "gpt-4"  # Fallback option
    
    # Model-specific configurations
    CLASSIFIER_TEMPERATURE: float = 0.3
    DRAFT_TEMPERATURE: float = 0.5
    REVIEW_TEMPERATURE: float = 0.2
    
    # RAG Configuration
    MAX_CONTEXT_LENGTH: int = 28000  # Increased for Groq's larger context
    CONTEXT_TOKENS_RESERVED: int = 1000
    
    # Agent Behavior
    MAX_RETRY_ATTEMPTS: int = 2
    
    # Paths
    ESCALATION_LOG_PATH: str = "data/escalations.csv"
    
    @property
    def groq_api_key(self) -> str:
        key = os.getenv("GROQ_API_KEY")
        if not key and self.LLM_PROVIDER == "groq":
            raise ValueError("GROQ_API_KEY not found in environment variables")
        return key
    
    @property
    def openai_api_key(self) -> str:
        key = os.getenv("OPENAI_API_KEY")
        if not key and self.LLM_PROVIDER == "openai":
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        return key

settings = Settings()