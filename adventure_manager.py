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
    "Filian the VTuber's abandoned home",
    "an abandoned Mega Mart",
    "Vault 101, where Amata is Overseer",
    "a raider ambushing you with a firearm",
    "a crazed scientist sprinting at you with a syringe"
]

STEPS_PER_ENVIRONMENT = 5  # After 5 challenges, move to new location

class AdventureManager:
    def __init__(self, user_record: dict):
        self.user = user_record
        self.state = user_record.get('AdventureState', {
            'env': None,
            'step': 0,
            'awaiting': None,
            'payload': {}
        })

    def save_state(self):
        self.user['AdventureState'] = self.state

    def start(self) -> str:
        self.state['env'] = random.choice(ENVIRONMENTS)
        self.state['step'] = 0
        self.save_state()
        return f"🗺️ Your adventure begins in the {self.state['env']}! Use `/adventure quiz` to face your first challenge."

    def next_quiz(self, subject: str = "fallout lore") -> str:
        if self.state['step'] > 0 and self.state['step'] % STEPS_PER_ENVIRONMENT == 0:
            # Move to new environment
            self.state['env'] = random.choice(ENVIRONMENTS)
            self.state['step'] = 0
            env_message = f"🌎 You’ve traveled onward and arrived at the {self.state['env']}!"
        else:
            env_message = f"🛤️ You’re still navigating the {self.state['env']}..."

        question, answer = QuizManager.create_quiz(subject)
        self.state['awaiting'] = 'quiz'
        self.state['payload'] = {'answer': answer, 'subject': subject}
        self.save_state()

        return (
            f"{env_message}\n\n"
            f"🔎 **Skill Check ({subject})**:\n{question}"
        )

    def handle_answer(self, text: str) -> str:
        env = self.state['env']
        expected = self.state['payload'].get('answer', '')
        correct = QuizManager.evaluate(text, expected)
        self.state['awaiting'] = None
        self.state['payload'] = {}

        result_message = ""

        if correct:
            result_message = (
                f"✅ Success! In the {env}, you handled the situation brilliantly. "
                "You press on with confidence.\n"
            )
        else:
            result_message = (
                f"❌ Failure! In the {env}, you stumble, but survive to fight another day.\n"
            )

        self.state['step'] += 1
        self.save_state()
        return result_message + "Use `/adventure quiz` to continue."
