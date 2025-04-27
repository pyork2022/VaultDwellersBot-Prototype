import os
import re
import random
import logging
from dotenv import dotenv_values
import discord

from owlmind.pipeline import ModelProvider
from owlmind.simple import SimpleEngine
from owlmind.discord import DiscordBot
from user_store import get_or_create_user, save_user, table
from adventure_manager import AdventureManager
from quiz_manager import QuizManager

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# XP needed to level up
LEVEL_XP = 5
# Basic perks pool
PERKS_POOL = [
    "Novice Scholar",
    "Insightful",
    "Quick Thinker",
    "Resourceful",
    "Lucky Streak"
]

class PersistingBot(DiscordBot):
    async def on_ready(self):
        logger.debug("Bot is ready and connected.")
        if QuizManager.provider is None:
            logger.debug("Initializing QuizManager provider.")
            QuizManager.initialize(self.engine.model_provider)
            logger.debug("QuizManager provider initialized.")

    async def on_message(self, message):
        if message.author == self.user or (
            not self.promiscuous and
            not (self.user in message.mentions or isinstance(message.channel, discord.DMChannel))
        ):
            return

        text = re.sub(r"<@!?\d+>", "", message.content).strip()
        text = text.replace(f"@{self.user.name}", "").strip()
        if not text:
            return

        logger.debug(f"Received message: {text}")
        uid = str(message.author.id)
        user = get_or_create_user(uid)
        manager = AdventureManager(user)

        # Help command
        if text.lower().startswith("/help"):
            reply = (
                "**VaultDwellersBot Commands**\n"
                "• /adventure start — Begin a new adventure\n"
                "• /adventure quiz <subject> — Face a skill check on any topic\n"
                "• /reset or /restart — Wipe your profile and start over\n"
                "• /stats — View your SPECIAL, XP, and Level\n"
                "• /start — Allocate your SPECIAL points (initial setup)"
            )
            return await message.channel.send(reply)

        # Reset/restart
        if text.lower().startswith("/reset") or text.lower().startswith("/restart"):
            table.delete_item(Key={"discordUserID": uid})
            return await message.channel.send(
                "🔄 Your VaultDweller profile has been reset. Run `/adventure start` to begin again!"
            )

        # Start adventure
        if text.lower().startswith("/adventure start"):
            resp = manager.start()
            save_user(user)
            return await message.channel.send(resp)

        # Quiz command
        if text.lower().startswith("/adventure quiz"):
            parts = text.split(" ", 2)
            subject = parts[2] if len(parts) >= 3 else "fallout lore"
            resp = manager.next_quiz(subject)
            logger.debug("<< Quiz payload: %r", manager.state['payload'])
            save_user(user)
            return await message.channel.send(resp)

        # Stats command
        if text.lower().strip() == "/stats":
            xp = user.get("XP", 0)
            level = user.get("Level", 1)
            stats = user.get("SPECIAL", {})
            perks = user.get("Perks", [])
            reply = f"**Vault Dweller Profile**\n• XP: {xp}   Level: {level}\n• SPECIAL:\n"
            reply += "\n".join(f"  – {k}: {v}" for k, v in stats.items())
            reply += f"\n• Perks: {', '.join(perks) or 'None'}"
            return await message.channel.send(reply)

        # Handle quiz answer if awaiting
        if manager.state.get("awaiting") == "quiz":
            user_answer = text.strip()
            logger.debug(f"User answer: {user_answer}")

            passed, fallback = QuizManager.evaluate(user_answer, manager.state['payload'].get('answer', ''))
            correct_answer_text = manager.state['payload'].get('answer', '')

            # If fallback question (open-ended), always count as passed
            if fallback:
                passed = True

            level_msg = ''
            if passed:
                user['XP'] = user.get('XP', 0) + 1
                if user['XP'] % LEVEL_XP == 0:
                    user['Level'] = user.get('Level', 1) + 1
                    perk = random.choice(PERKS_POOL)
                    user.setdefault('Perks', []).append(perk)
                    level_msg = f"🎉 You leveled up to Level {user['Level']}! Perk gained: {perk}."

            story = manager.handle_answer(user_answer)

            # Only show correct answer if it was NOT a fallback
            if not passed and not fallback:
                story += f"\n📖 Correct Answer: {correct_answer_text}"

            if level_msg:
                story += f"\n{level_msg}"

            save_user(user)
            return await message.channel.send(story)

        # Initial SPECIAL allocation (/start)
        if text.lower().startswith("/start"):
            if user.get("XP", 0) != 0 or user.get('SPECIAL'):
                return await message.channel.send("You’ve already set up your SPECIAL stats.")
            return await message.channel.send(
                "Welcome to VaultDwellersBot! You have **28** points to assign across your SPECIAL stats.\n"
                "Reply with 7 comma-separated integers (must sum to 28) in order:\n"
                "`Strength, Perception, Endurance, Charisma, Intelligence, Agility, Luck`"
            )

        # Handle SPECIAL allocation
        if re.fullmatch(r"\d+(,\s*\d+){6}", text):
            parts = [int(x) for x in text.split(",")]
            if sum(parts) != 28:
                return await message.channel.send("❌ That doesn’t sum to 28—try again.")
            labels = ["Strength", "Perception", "Endurance", "Charisma", "Intelligence", "Agility", "Luck"]
            stats = dict(zip(labels, parts))
            user['SPECIAL'] = stats
            user['XP'] = 0
            user['Level'] = 1
            user['Perks'] = []
            save_user(user)
            return await message.channel.send(
                f"SPECIAL set to {stats}!\nYou can now send `/stats` or just chat."
            )

if __name__ == "__main__":
    cfg = dotenv_values(".env")
    TOKEN = cfg.get("DISCORD_TOKEN")
    URL = cfg.get("SERVER_URL")
    TYPE = cfg.get("SERVER_TYPE")
    MODEL = cfg.get("SERVER_MODEL")

    if not all([TOKEN, URL, TYPE, MODEL]):
        raise ValueError("One or more required environment variables are missing.")

    provider = ModelProvider(
        type=TYPE,
        base_url=URL,
        api_key=cfg.get("SERVER_API_KEY"),
        model=MODEL
    )
    engine = SimpleEngine(id="bot-1")
    engine.model_provider = provider

    bot = PersistingBot(token=TOKEN, engine=engine, promiscuous=False, debug=True)
    bot.run()
