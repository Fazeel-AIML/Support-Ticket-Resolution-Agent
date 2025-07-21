from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from src.config import settings
from typing import Literal

Purpose = Literal["classification", "draft", "review"]

class LLMService:
    def __init__(self):
        self._llm_instances = {}

    def get_llm(self, purpose: Purpose) -> ChatGroq | ChatOpenAI:
        """Get configured LLM instance for specific purpose."""
        if purpose in self._llm_instances:
            return self._llm_instances[purpose]

        temperature_map = {
            "classification": settings.CLASSIFIER_TEMPERATURE,
            "draft": settings.DRAFT_TEMPERATURE,
            "review": settings.REVIEW_TEMPERATURE
        }

        llm = self._create_llm(
            provider=settings.LLM_PROVIDER,
            temperature=temperature_map[purpose]
        )
        self._llm_instances[purpose] = llm
        return llm

    def _create_llm(self, provider: str, temperature: float) -> ChatGroq | ChatOpenAI:
        """Instantiate the LLM based on provider."""
        if provider == "groq":
            return ChatGroq(
                model_name=settings.GROQ_MODEL,
                temperature=temperature,
                api_key=settings.groq_api_key
            )
        return ChatOpenAI(
            model_name=settings.OPENAI_MODEL,
            temperature=temperature,
            api_key=settings.openai_api_key
        )

# Singleton instance
llm_service = LLMService()