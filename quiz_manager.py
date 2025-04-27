import json
import logging
import re
from typing import Dict
from owlmind.pipeline import ModelProvider

logger = logging.getLogger(__name__)

class QuizManager:
    provider: ModelProvider = None

    @classmethod
    def initialize(cls, model_provider: ModelProvider) -> None:
        """Assign the LLM provider (e.g., LLaMA via Ollama)."""
        cls.provider = model_provider
        logger.info("QuizManager initialized with model provider.")

    @classmethod
    def create_quiz(cls, subject: str) -> Dict[str, str]:
        """
        Generate a quiz question on `subject`. Returns a dict with 'question' and 'answer'.
        """
        if cls.provider is None:
            raise RuntimeError("QuizManager provider is not initialized.")

        prompt = (
            f"Generate a challenging, college-level quiz question about '{subject}'. "
            "Respond *only* with valid JSON containing keys 'question' and 'answer'."
        )
        raw = cls.provider.request(prompt).strip()
        logger.info("LLM raw response: %s", raw)

        # Auto-fix common JSON xssues
        clean = raw
        if not clean.startswith('{'):
            clean = '{' + clean
        if clean.count('{') > clean.count('}'):
            clean += '}' * (clean.count('{') - clean.count('}'))

        try:
            payload = json.loads(clean)
            question = payload.get("question", "").strip()
            answer = payload.get("answer", "").strip()
            logger.info("Parsed question: %r", question)
            return {"question": question, "answer": answer}
        except json.JSONDecodeError as e:
            logger.error("JSON parse error: %s", e)

        # Fallback to a dynamic question
        fallback_q = f"What is an advanced concept in {subject}?"
        fallback_a = f"A detailed explanation of an advanced concept in {subject}."
        logger.info("Using fallback question for subject '%s'", subject)
        return {"question": fallback_q, "answer": fallback_a}

    @staticmethod
    def evaluate(user_answer: str, correct_answer: str) -> bool:
        """Case-insensitive, punctuation-insensitive compare (or keyword-based for fallback answers)."""
        # strip punctuation and lowercase
        normalize = lambda s: re.sub(r"[^\w\s]", "", s.lower()).strip()

        user = normalize(user_answer)
        correct = normalize(correct_answer)

        # Specialized fallback logic
        if correct.startswith("a detailed explanation"):
            # pick first few keywords to check relevance
            keywords = correct.split()[:3]
            return all(k in user for k in keywords)

        return user == correct
