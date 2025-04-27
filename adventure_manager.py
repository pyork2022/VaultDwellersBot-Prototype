import random
from quiz_manager import QuizManager
from user_store import save_user  # Import save_user from user_store

# Other code in adventure_manager.py

def save_state(self):
    save_user(self.user)  # Save the user’s current state to the database

# Pre-defined Fallout-style environments
ENVIRONMENTS = [
    "abandoned factories of Grafton",
    "irradiated wastes of the Glowing Sea",
    "ruins of Megaton",
    "deserted Vault 13",
    "overrun Brotherhood bunker",
    "a secret Enclave lab",
    "an abandoned Mega Mart",
    "Vault 101, Amata is Overseer",
    "a raider ambush site",
    "a hidden pre-War government facility"
]

class AdventureManager:
    def __init__(self, user_record: dict):
        self.user = user_record
        self.state = user_record.get('AdventureState', {
            'env': None,
            'step': 0,
            'awaiting': None,  # 'quiz' if waiting for answer
            'payload': {}
        })

    def save_state(self):
        self.user['AdventureState'] = self.state
        save_user(self.user)  # Save the user’s current state to the database

    def start(self) -> str:
        self.state['env'] = random.choice(ENVIRONMENTS)
        self.state['step'] = 1
        self.state['awaiting'] = None
        self.state['payload'] = {}
        self.save_state()
        return f"🗺️ Your adventure begins in the {self.state['env']}! Use `/adventure quiz <subject>` to face challenges."

    def next_quiz(self, subject: str = "fallout lore") -> str:
        self.state['awaiting'] = 'quiz'
        self.state['payload']['subject'] = subject
        self.state['payload']['question'], self.state['payload']['answer'] = QuizManager.create_quiz(subject)
        self.save_state()
        return f"🔎 **Skill Check ({subject})**:\n{self.state['payload']['question']}"

    def handle_answer(self, user_answer: str) -> str:
        correct = QuizManager.evaluate(user_answer, self.state['payload'].get('answer', ''))
        env = self.state.get('env', 'the wasteland')

        self.state['awaiting'] = None
        self.state['payload'] = {}
        self.state['step'] += 1  # Increment step to show progression
        self.save_state()

        # Adjust story based on the answer
        if correct:
            story = f"✅ You passed the skill check in the {env}! You are rewarded with knowledge!"
        else:
            story = f"❌ You failed the skill check in the {env}, but your journey continues with new challenges."

        return story
