# adventure_manager.py

import random

# pick 5–10 Fallout-style opening sites
ENVIRONMENTS = [
    "abandoned factories of Grafton",
    "irradiated wastes of the Glowing Sea",
    "crumbling vault beneath Vault 101",
    "toxic swamps near Point Pleasant",
    "deserted streets of Megaton",
    "burned-out shell of Rivet City",
    "radioactive tunnels under the Capitol",
    "flooded underpass by the Potomac",
    "ruined library of the Jefferson Memorial",
    "mutant-infested reactor control room"
]

def start_adventure() -> str:
    loc = random.choice(ENVIRONMENTS)
    return f"🗺️ Your adventure begins in the {loc}! Let’s see how your SPECIAL guides you…"
