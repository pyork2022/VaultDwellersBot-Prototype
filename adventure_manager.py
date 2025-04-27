# adventure_manager.py

import random
from quiz_manager import QuizManager

# Pre-defined Fallout-style environments
ENVIRONMENTS = [
    "abandoned factories of Grafton",
    "irradiated wastes of the Glowing Sea",
    "ruins of Megaton",
    "deserted vault 13",
    "overrun Brotherhood bunker",
    "Filian the Vtuber's abandoned home",
    "An abandoned Mega Mart",
    "Vault 101, Amata is Overseer",
    "A raider is approaching you, brandishing a firearm",
    "A dazed scientist sprints towards you with a syringe in his hand"
]

class AdventureManager:
    def __init__(self, user_record: dict):
        self.user = user_record
        # load or initialize
        self.state = user_record.get('AdventureState', {
            'env': None,
            'step': 0,
            'awaiting': None,   # 'quiz' when waiting for an answer
            'payload': {}
        })

    def save_state(self):
        self.user['AdventureState'] = self.state

    def start(self) -> str:
        if not self.state['env']:
            self.state['env'] = random.choice(ENVIRONMENTS)
            self.state['step'] = 1
        self.save_state()
        return f"🗺️ Your adventure begins in the {self.state['env']}! Use `/adventure quiz` to face your first challenge."

    def next_quiz(self) -> str:
        # for now, all environments use the "fallout lore" pool
        subject = "fallout lore"
        question, answer = QuizManager.create_quiz(subject)
        self.state['awaiting'] = 'quiz'
        self.state['payload']['answer'] = answer
        self.save_state()
        return f"🔎 **Skill Check ({subject})**:\n{question}"

    def handle_answer(self, text: str) -> str:
        correct = QuizManager.evaluate(text, self.state['payload']['answer'])
        self.state['awaiting'] = None
        self.state['payload'].clear()
        # advance story step if you like:
        self.state['step'] += 1
        self.save_state()
        if correct:
            return "✅ You passed the challenge! The path ahead is clearer.\nUse `/adventure quiz` again or just chat to continue."
        else:
            return "❌ You failed the challenge—watch your step next time.\nUse `/adventure quiz` again or just chat to continue."
