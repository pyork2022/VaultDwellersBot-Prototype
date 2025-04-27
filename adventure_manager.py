# adventure_manager.py

import random
from quiz_manager import QuizManager

# Pre-defined Fallout-style environments
ENVIRONMENTS = [
    "abandoned factories of Grafton",
    "irradiated wastes of the Glowing Sea",
    "ruins of Megaton",
    "deserted Vault 13",
    "overrun Brotherhood bunker",
    "an abandoned Mega Mart",
    "Vault 101 where Amata is Overseer",
    "a raider outpost in the wastes",
    "a secret Enclave lab",
    "the ruins of Rivet City"
]

class AdventureManager:
    def __init__(self, user_record: dict):
        self.user = user_record
        # load or initialize
        self.state = user_record.get('AdventureState', {
            'env': None,
            'step': 0,
            'awaiting': None,   # 'quiz' when waiting for an answer
            'subject': None,
            'payload': {}
        })

    def save_state(self):
        self.user['AdventureState'] = self.state

    def start(self) -> str:
        if not self.state['env']:
            self.state['env'] = random.choice(ENVIRONMENTS)
            self.state['step'] = 1
        self.save_state()
        return (
            f"🗺️ Your adventure begins in the {self.state['env']}!  "
            "Use `/adventure quiz` to face your first challenge."
        )

    def next_quiz(self, subject: str = None) -> str:
        # if user specified a subject (e.g. "python syntax" or "fallout lore")
        if subject:
            subkey = subject.lower()
        else:
            subkey = "fallout lore"

        # store subject for later narrative
        self.state['subject'] = subkey
        question, answer = QuizManager.create_quiz(subkey)

        self.state['awaiting'] = 'quiz'
        self.state['payload'] = {'answer': answer}
        self.save_state()

        return f"🔎 **Skill Check ({subkey})**:\n{question}"

    def handle_answer(self, text: str) -> str:
        correct = QuizManager.evaluate(text, self.state['payload']['answer'])
        self.state['awaiting'] = None
        self.state['payload'].clear()
        self.state['step'] += 1
        self.save_state()

        if correct:
            return (
                "✅ You passed the challenge! The path ahead is clearer.  "
                "Use `/adventure quiz` again or just chat to continue."
            )
        else:
            return (
                "❌ You failed the challenge—watch your step next time.  "
                "Use `/adventure quiz` again or just chat to continue."
            )
