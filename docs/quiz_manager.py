# quiz_manager.py

import random
import difflib
from typing import Tuple, Optional, Callable

# ——— your fixed bank of questions ————————————————
QUESTION_BANK = {
    "python syntax": [
        ("How do you comment out a line in Python?", "# This is a comment"),
        ("What's the keyword to define a function?", "def"),
    ],
    "fallout lore": [
        ("What is the name of the supermutant city in Fallout 3?", "Underworld"),
        ("Which vault number was your character from in Fallout 4?", "111"),
    ],
    # …add more subjects here…
}

class QuizManager:
    def __init__(self, llm_requester: Optional[Callable[[str], str]] = None, cutoff: float = 0.6):
        """
        llm_requester(prompt)->str  –  use to generate a one-off question when your bank misses.
        cutoff: fuzzy‐match threshold for subject names.
        """
        self.bank = QUESTION_BANK
        self.llm = llm_requester
        self.cutoff = cutoff

    def _fuzzy_match(self, subject: str) -> Optional[str]:
        choices = list(self.bank.keys())
        matches = difflib.get_close_matches(subject, choices, n=1, cutoff=self.cutoff)
        return matches[0] if matches else None

    def create_quiz(self, subject: str) -> Tuple[str, str]:
        sub = subject.lower().strip()
        key = sub if sub in self.bank else self._fuzzy_match(sub)
        if key:
            return random.choice(self.bank[key])

        if self.llm:
            prompt = (
                f"Generate a single quiz question about “{subject}”\n"
                "Then on the next line provide the correct answer, exactly:\n"
                "Q: <question>\nA: <answer>"
            )
            resp = self.llm(prompt)
            # Expect:
            # Q: What …?
            # A: Because …
            try:
                q_line, a_line = resp.splitlines()[:2]
                question = q_line.split(":",1)[1].strip()
                answer   = a_line.split(":",1)[1].strip()
                # cache
                self.bank.setdefault(subject, []).append((question, answer))
                return question, answer
            except Exception as e:
                raise KeyError(f"Couldn't parse LLM fallback for “{subject}”") from e

        raise KeyError(f"No quiz available on “{subject}”")

    @staticmethod
    def evaluate(user_answer: str, correct_answer: str) -> bool:
        return user_answer.strip().lower() == correct_answer.strip().lower()
