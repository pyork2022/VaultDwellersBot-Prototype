# quiz_manager.py

import json
import logging
import re
from typing import Tuple
from owlmind.pipeline import ModelProvider

logger = logging.getLogger(__name__)

class QuizManager:
    provider: ModelProvider = None  # Will be set when the bot starts

    @classmethod
    def initialize(cls, model_provider: ModelProvider):
        """Assign the ModelProvider (usually LLaMA through Ollama)."""
        cls.provider = model_provider
        logger.debug("✅ QuizManager initialized with provider %r", model_provider)

    @classmethod
    def create_quiz(cls, subject: str) -> dict:
        """
        Generate a quiz question dynamically based on the user's subject.
        Returns a dict: {'question': str, 'answer': str}
        """
        logger.debug("▶️ Enter create_quiz(subject=%r)", subject)
        if not cls.provider:
            raise ValueError("QuizManager provider is not initialized.")

        prompt = (
            f"Generate exactly one challenging, detailed quiz question about '{subject}', "
            "aimed at a college-level student. "
            "Respond *only* with a valid JSON object with two keys—\"question\" and \"answer\"—"
            "and do not wrap it in any markdown or extra text. Do not escape apostrophes "
            "with backslashes. Example:\n\n"
            "{\n"
            "  \"question\": \"...your question here...?\",\n"
            "  \"answer\": \"...the correct, well-explained answer...\"\n"
            "}"
        )

        raw = cls.provider.request(prompt)
        logger.debug("🔍 Raw from LLM:\n%s", raw)

        # Clean up stray escapes and whitespace
        clean = raw.strip().replace("\\'", "'")
        logger.debug("✨ Cleaned for JSON parsing (before brace-fix):\n%s", clean)

        # Auto-balance braces if needed
        opens = clean.count('{')
        closes = clean.count('}')
        if opens > closes:
            clean += '}' * (opens - closes)
            logger.debug("🛠️ Auto-appended %d closing brace(s)", opens - closes)

        logger.debug("✨ Cleaned for JSON parsing (after brace-fix):\n%s", clean)

        # Try parsing JSON
        try:
            payload = json.loads(clean)
            question = payload["question"].strip()
            answer = payload["answer"].strip()
            logger.debug("✅ Parsed JSON Q/A successfully")
            return {"question": question, "answer": answer}
        except (ValueError, KeyError) as e:
            logger.debug("⚠️ JSON parse failed: %s", e)

            # Fallback parsing for free-form text
            if "Question:" in raw and "Answer:" in raw:
                try:
                    part = raw.split("Question:", 1)[1]
                    q_text, a_text = part.split("Answer:", 1)
                    logger.debug("✅ Parsed fallback Q/A successfully")
                    return {
                        "question": q_text.strip(),
                        "answer":   a_text.strip()
                    }
                except Exception as fallback_error:
                    logger.debug("⚠️ Free-form fallback parsing also failed: %s", fallback_error)

        # Ultimate fallback
        logger.debug("❓ Falling back to generic question for subject=%r", subject)
        return {
            "question": f"What is an advanced concept in {subject}?",
            "answer": "fallback"  # Special flag we handle separately
        }

    @staticmethod
    def evaluate(user_answer: str, correct_answer: str) -> Tuple[bool, bool]:
        """
        Evaluate the user answer against the correct one.
        Returns (passed: bool, fallback: bool)
        """
        # Normalize input: remove punctuation, lowercase
        normalize = lambda s: re.sub(r"[^\w\s]", "", s.lower()).strip()

        user_norm = normalize(user_answer)
        correct_norm = normalize(correct_answer)

        fallback = correct_norm == "fallback"

        if fallback:
            return True, True  # Always correct if fallback question

        if user_norm == correct_norm:
            return True, False

        # Allow minor typos (Levenshtein distance <= 2)
        def levenshtein(s1: str, s2: str) -> int:
            if len(s1) < len(s2):
                return levenshtein(s2, s1)
            if len(s2) == 0:
                return len(s1)
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            return previous_row[-1]

        distance = levenshtein(user_norm, correct_norm)

        if distance <= 2:
            return True, False

        return False, False
