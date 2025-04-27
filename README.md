# VaultDwellersBot - Project Prototype README

### Overview
VaultDwellersBot is a Fallout-themed, Discord-based interactive educational bot that provides users with a dynamic study experience, gamified through an adventure and SPECIAL stats system. The project combines AI-powered quiz generation with character progression, XP leveling, perks, and Fallout-style narrative.

### Key Features

- **Adventure Mode:**
  - Users start an adventure in a randomized Fallout-style environment.
  - Each step of the adventure involves answering quiz questions to progress.

- **Quiz Generation:**
  - College-level questions are generated dynamically via a connected AI model (Ollama, LLaMA).
  - Quiz topics can be anything (e.g., "Fallout lore", "rock music", "math").

- **SPECIAL Stats System:**
  - Users allocate 28 points across 7 SPECIAL stats (Strength, Perception, Endurance, Charisma, Intelligence, Agility, Luck) when starting.
  - (Currently) SPECIAL stats are stored and available for future game mechanics.

- **XP, Leveling, and Perks:**
  - Correct answers award XP.
  - After every 5 XP (for now), users level up.
  - Upon leveling up, users receive a random perk from a perks pool.

- **Fallback Logic:**
  - If the AI's response is malformed, fallback generic questions are generated.
  - Fallback questions automatically accept any reasonable answer.

- **Persistence:**
  - All user data (XP, Level, SPECIAL, Perks) is stored persistently in DynamoDB.

- **User Commands:**
  - `/adventure start` - Start a new adventure.
  - `/adventure quiz <subject>` - Begin a skill check challenge.
  - `/reset` or `/restart` - Reset user profile.
  - `/stats` - View SPECIAL, XP, Level, and Perks.
  - `/start` - Begin SPECIAL stat assignment (first time setup).
  - `/help` - View all bot commands.

### Technology Stack
- **Backend:** Python 3.13
- **Discord Integration:** discord.py
- **Model Provider:** OwlMind (SimpleEngine)
- **Database:** AWS DynamoDB
- **AI/Quiz Generation:** Connected to Ollama running LLaMA 3 models
- **Hosting:** Local prototype or server-based deployment

### File Structure Highlights
- `bot-1.py` - Main bot event loop and command handling.
- `quiz_manager.py` - Quiz generation and answer evaluation logic.
- `adventure_manager.py` - Adventure progression and environment management.
- `user_store.py` - User profile storage and XP award mechanics.

### Current Limitations
- SPECIAL stats currently do not affect gameplay (planned feature).
- All perks are simple strings without functional effects yet.
- Leveling curve is basic (fixed XP per level, though future work included detailed thresholds).
- No difficulty scaling yet based on user level.

### Future Improvements
- Integrate SPECIAL stats into adventure outcomes.
- Refine level XP thresholds for a smoother curve.
- Expand perks with actual passive bonuses.
- Implement dynamic story choices influenced by SPECIAL stats.
- Add mini-quests, collectibles, or rewards beyond XP.
- Improve answer evaluation (e.g., partial credit for near matches).

---

### Quick Start Instructions
1. Clone the repository.
2. Set up `.env` file with your Discord Bot Token and Model Provider details.
3. Launch the bot:
```bash
python bot-1.py
```
4. Interact with the bot on your configured Discord server!

---

Created by: The Vault Dwellers, 2025  
Prototype Status: **Working and Ready for Demo** 🚀



<img src="docs/images/owlmind-banner.png" width=800>

### [Understand](./README.md) | [Get Started](./README.md#getting-started) | [Contribute](./CONTRIBUTING.md)

# OwlMind 

The OwlMind Framework is being developed by The Generative Intelligence Lab at Florida Atlantic University to support education and experimentation with Hybrid Intelligence Systems. These solutions combine rule-based and generative AI (GenAI)-based inference to facilitate the implementation of local AI solutions, improving latency, optimizing costs, and reducing energy consumption and carbon emissions.

The framework is designed for both education and experimentation empowering students and researchers to rapidly build Hybrid AI-based Agentic Systems, achieving tangible results with minimal setup.


## Core Components


<img src="docs/images/owlmind-arch.png" width=800>

* **Bot Runner for Discord Bots:** Hosts and executes bots on platforms like Discord, providing users with an interactive conversational agent.
* **Agentic Core:** Enables deliberation and decision-making by allowing users to define and configure rule-based systems.
* **Configurable GenAI Pipelines:** Supports flexible and dynamic pipelines to integrate large-scale GenAI models into workflows.
* **Workflow Templates:** Provides pre-configured or customizable templates to streamline the Prompt Augmentation Process.
* **Artifacts:** Modular components that connect agents to external functionalities such as web APIs, databases, Retrieval-Augmented Generation (RAG) systems, and more.
* **Model Orchestrator:** Manages and integrates multiple GenAI models within pipelines, offering flexibility and simplicity for developers.


## Hybrid Intelligence Framework

The OwlMind architecture follows the principles of ``Hybrid Intelligence``, combining local rule-based inference with remote GenAI-assisted inference. This hybrid approach allows for multiple inference configurations:

* **GenAI generates the rules:**  The system leverages GenAI to create or refine rule-based logic, ensuring adaptability and efficiency.
* **Rules solve interactions; GenAI intervenes when needed:** if predefined rules are insufficient, the system escalates decision-making to the GenAI model.
* **Rules solve interactions and request GenAI to generate new rules:** instead of directly relying on GenAI for inference, the system asks it to expand its rule set dynamically.
* **Proactive rule generation for new contexts:** the system anticipates novel situations and queries GenAI for relevant rules before issues arise, ensuring continuous learning and adaptability.


## Agentic Core: Belief-Desire-Intention (BDI) Model


The ``Agentic Core`` adheres to the ``Belief-Desire-Intention (BDI) framework``, a cognitive architecture that enables goal-oriented agent behavior. The decision-making process is structured as follows:

* **Beliefs:** The agent's knowledge or perception of its environment, forming the foundation for evaluation and decision-making.
* **Desires:** The agent’s objectives or goals, such as completing workflows, retrieving data, or responding to user queries.
* **Intentions:** The specific plans or strategies the agent commits to in order to achieve its desires, ensuring feasibility and optimization.
* **Plan Base:** A repository of predefined and dynamically generated plans, serving as actionable roadmaps to execute the agent's goals efficiently.
* **Capability Base:** Defines the agent's operational capabilities, specifying available actions and interactions; linked to existing Artifacts.


## Getting Started

* [Install the Owlmind Framework on your Computer](./INSTALLING.md)
* [Set up a simple HybridAI-Based Discord Bot](./INSTALLING.md)
* [Configure GenAI Pipelines](./CONFIG.md) to extend the Bot's conversation capabilities
* Configure Prompt Engineering Workflows to improve the Bot's reasoning.
* Configure Artifacts in the GenAI Pipelines to extend the Bot's reasoning capabilities

