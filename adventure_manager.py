import random
from typing import Dict
from user_store import save_user  # Persist user state
from quiz_manager import QuizManager

# Pre-defined environments with a bit of flavor text
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

# Basic perks granted upon leveling up
PERKS = [
    "Quick Learner",      # XP gain boost
    "Fortitude",         # Resist failure consequences
    "Silver Tongue",     # Better negotiation
    "Sharpshooter",      # Improved precision
    "Lucky"              # Increased chance of success
]

class AdventureManager:
    def __init__(self, user_record: Dict) -> None:
        self.user = user_record
        # AdventureState holds env, step, awaiting, payload
        self.state = self.user.get('AdventureState', {
            'env': None,
            'step': 0,
            'awaiting': None,
            'payload': {}
        })

    def save_state(self) -> None:
        # Persist just the adventure state
        self.user['AdventureState'] = self.state
        save_user(self.user)

    def start(self) -> str:
        # Pick a random environment and introduce the scene
        self.state['env'] = random.choice(ENVIRONMENTS)
        self.state['step'] = 1
        self.state['awaiting'] = None
        self.state['payload'] = {}
        self.save_state()
        return (
            f"🗺️ **Chapter {self.state['step']}**: You find yourself in {self.state['env']}. "
            "The air is thick, and danger could lurk around every corner. "
            "Prepare yourself and use `/adventure quiz <subject>` to face your first challenge."
        )

    def next_quiz(self, subject: str = "fallout lore") -> str:
        # Generate a quiz question and weave it into the narrative
        self.state['awaiting'] = 'quiz'
        self.state['payload']['subject'] = subject
        qa = QuizManager.create_quiz(subject)
        self.state['payload'].update(qa)
        self.save_state()

        question = qa['question']
        return (
            f"🔎 **Skill Check ({subject.capitalize()})**: As you proceed through the {self.state['env']}, "
            f"you are confronted with a mental puzzle:\n\n> {question}"
        )

    def handle_answer(self, user_answer: str) -> str:
        correct_answer = self.state['payload'].get('answer', '')
        env = self.state.get('env', 'the wasteland')
        passed = QuizManager.evaluate(user_answer, correct_answer)

        # Award XP and maybe level up
        xp_gain = 10
        self.user['XP'] = self.user.get('XP', 0) + (xp_gain if passed else 0)
        leveled_up = False
        # Define threshold: e.g., 50 XP per current level
        threshold = self.user.get('Level', 1) * 50
        if passed and self.user['XP'] >= threshold:
            self.user['XP'] -= threshold
            self.user['Level'] = self.user.get('Level', 1) + 1
            # Grant a random perk
            new_perk = random.choice(PERKS)
            self.user.setdefault('Perks', []).append(new_perk)
            leveled_up = True

        # Clear quiz state and advance chapter
        self.state['awaiting'] = None
        self.state['payload'] = {}
        self.state['step'] += 1
        # Persist both state and user stats
        self.save_state()

        # Build narrative response
        if passed:
            resp = (
                f"✅ You answered correctly! You gain {xp_gain} XP in the {env}."
            )
            if leveled_up:
                resp += (
                    f" 🎉 You reached Level {self.user['Level']} and gained the perk '{new_perk}'!"
                )
            resp += f" You press onward to Chapter {self.state['step']}. What new trials await?"
        else:
            resp = (
                f"❌ That was not correct. The {env} seems to mock your misstep."
                f" You stumble into Chapter {self.state['step']} with resolve renewed."
            )
            # Always reveal the correct answer
            resp += f"\n📖 Correct Answer: {correct_answer}"

        # Save user profile with updated XP/Level/Perks
        save_user(self.user)
        return resp
