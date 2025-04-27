import random
from typing import Tuple

DEFAULT_QUESTION_BANK = {
    "fallout lore": [
        ("What is the name of the supermutant city in Fallout 3?", "Underworld"),
        ("Which vault number was your character from in Fallout 4?", "111"),
        ("What faction controls New Vegas in Fallout: New Vegas?", "New California Republic"),
        ("Who is the leader of the Brotherhood of Steel in Fallout 4?", "Elder Maxson"),
    ],
    "python syntax": [
        ("How do you comment out a line in Python?", "# This is a comment"),
        ("What's the keyword to define a function?", "def"),
        ("Which symbol is used to create a dictionary in Python?", "{}"),
        ("Which keyword is used for exception handling?", "try"),
    ],
    "german": [
        ("What is the German word for 'thank you'?", "danke"),
        ("Translate 'house' into German.", "haus"),
        ("How do you say 'goodbye' in German?", "auf wiedersehen"),
        ("What is the German word for 'please'?", "bitte"),
    ]
}

class QuizManager:
    @staticmethod
    def create_quiz(subject: str) -> Tuple[str, str]:
        subject = subject.lower()

        if subject in DEFAULT_QUESTION_BANK:
            pool = DEFAULT_QUESTION_BANK[subject]
            return random.choice(pool)

        return (
            f"What is one important fact about {subject}?",
            f"(Any reasonable answer about {subject})"
        )

    @staticmethod
    def evaluate(user_answer: str, correct_answer: str) -> bool:
        user = user_answer.strip().lower()
        correct = correct_answer.strip().lower()

        if correct.startswith("(any reasonable answer"):
            return True

        return user == correct
