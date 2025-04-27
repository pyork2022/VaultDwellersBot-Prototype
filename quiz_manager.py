# quiz_manager.py

import random
from typing import Tuple

# Simple pool: subject → list of (Q, correct_answer) tuples
QUESTION_BANK = {
    "python syntax": [
        ("How do you comment out a line in Python?", "# This is a comment"),
        ("What's the keyword to define a function?", "def"),
    ],
    "fallout lore": [
        ("What is the name of the supermutant city in Fallout 3?", "Underworld"),
        ("Which vault number was your character from in Fallout 4?", "111"),
    ],
    # …and so on for each subject you want to support…
}

class QuizManager:
    @staticmethod
    def create_quiz(subject: str) -> Tuple[str,str]:
        """
        Returns (question_text, correct_answer).
        Raises KeyError if no such subject.
        """
        pool = QUESTION_BANK[subject]
        return random.choice(pool)
    
    @staticmethod
    def evaluate(user_answer: str, correct_answer: str) -> bool:
        return user_answer.strip().lower() == correct_answer.strip().lower()
