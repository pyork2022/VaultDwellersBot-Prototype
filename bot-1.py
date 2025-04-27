# bot-1.py :: VaultDwellersBot with OwlMind + DynamoDB + /start & /stats + Quiz + SPECIAL-aware XP/Leveling

import os
import re
import datetime
from dotenv import dotenv_values
import discord

from owlmind.pipeline import ModelProvider
from owlmind.simple import SimpleEngine
from owlmind.discord import DiscordBot
from owlmind.bot import BotMessage

from user_store import get_or_create_user, save_user, table
from quiz_manager import QuizManager

# ——— XP & Leveling setup —————————————————————————————
LEVEL_THRESHOLDS = {
    1:     0,   2:   100,  3:   300,  4:   600,  5:  1000,
    6:   1500,  7:  2100,  8:  2800,  9:  3600, 10:  4500,
   11:   5500, 12:  6600, 13:  7800, 14:  9100, 15: 10500,
   16:  12000, 17: 13600, 18: 15300, 19: 17100, 20: 19000
}

def award_xp(user: dict, base_xp: int = 1):
    intel = user.get("SPECIAL", {}).get("Intelligence", 0)
    bonus = intel // 3
    total = base_xp + bonus
    user["XP"] = user.get("XP", 0) + total

    old = user.get("Level", 1)
    new = old
    for lvl, req in sorted(LEVEL_THRESHOLDS.items()):
        if user["XP"] >= req:
            new = lvl
    user["Level"] = new
    return total, old, new
# ——————————————————————————————————————————————————————————

# placeholder; will be set in __main__
quiz_mgr: QuizManager

class PersistingBot(DiscordBot):
    """
    Extends OwlMind’s DiscordBot to:
     • Handle /start, /stats, /reset
     • Load/store user state in DynamoDB
     • Embed SPECIAL into prompts
     • Award XP, Level-up, and Quiz flows
    """
    async def on_message(self, message):
        # 1) Ignore the bot itself, or non-mentions if not promiscuous
        if message.author == self.user or (
            not self.promiscuous and
            not (self.user in message.mentions or isinstance(message.channel, discord.DMChannel))
        ):
            return

        # 2) Strip out mentions
        text = re.sub(r"<@\d+>", "", message.content).strip()
        text = text.replace(f"@{self.user.name}", "").strip()
        if not text:
            return

        uid  = str(message.author.id)
        user = get_or_create_user(uid)

        # — reset
        if text.lower().startswith("/reset"):
            table.delete_item(Key={"discordUserID": uid})
            return await message.channel.send(
                "🔄 Your VaultDweller profile has been reset. Run `/start` to set your SPECIAL stats anew!"
            )

        # — start
        if text.lower().startswith("/start"):
            if user.get("XP", 0) != 0:
                return await message.channel.send("You’ve already set up your SPECIAL stats.")
            return await message.channel.send(
                "Welcome to VaultDwellersBot! You have **28** points to assign across your SPECIAL stats.\n"
                "Reply with 7 comma-separated integers (must sum to 28) in order:\n"
                "`Strength, Perception, Endurance, Charisma, Intelligence, Agility, Luck`\n"
                "Example: `5,5,5,5,5,2,1`"
            )

        # — handle SPECIAL allocation
        if re.fullmatch(r"\d+(,\s*\d+){6}", text):
            parts = [int(x) for x in text.split(",")]
            if sum(parts) != 28:
                return await message.channel.send("❌ That doesn’t sum to 28—try again.")
            stats = dict(zip(
                ["Strength","Perception","Endurance","Charisma","Intelligence","Agility","Luck"],
                parts
            ))
            user["SPECIAL"] = stats
            save_user(user)
            return await message.channel.send(
                f"SPECIAL set to {stats}!\nYou can now send `/stats` or just chat."
            )

        # — stats
        if text.lower().strip() == "/stats":
            xp    = user.get("XP", 0)
            level = user.get("Level", 1)
            stats = user.get("SPECIAL", {})
            perks = user.get("Perks", [])
            reply = (
                f"**Vault Dweller Profile**\n"
                f"• XP: {xp}   Level: {level}\n"
                f"• SPECIAL:\n"
                + "\n".join(f"  – {k}: {v}" for k,v in stats.items()) +
                f"\n• Perks: {', '.join(perks) or 'None'}"
            )
            return await message.channel.send(reply)

        # — quiz start
        if text.lower().startswith("quiz me on"):
            subject = text[10:].strip()
            try:
                q, a = quiz_mgr.create_quiz(subject)
            except KeyError:
                return await message.channel.send(f"❓ I don’t have quizzes on “{subject}”!")
            user['pending_quiz'] = {'question': q, 'answer': a}
            save_user(user)
            return await message.channel.send(f"❓ {q}")

        # — quiz answer
        pending = user.get('pending_quiz')
        if pending and not text.startswith("/"):
            correct   = pending['answer']
            is_right  = QuizManager.evaluate(text, correct)
            user.pop('pending_quiz', None)
            save_user(user)
            resp = "✅ Correct!" if is_right else f"❌ Nope, the answer was: {correct}"
            return await message.channel.send(resp)

        # — default: AI chat
        special = user.get("SPECIAL", {})
        prompt_text = f"Your SPECIAL stats: {special}\nUser says: {text}"
        context = BotMessage(
            layer1       = message.guild.id        if message.guild else 0,
            layer2       = message.channel.id      if hasattr(message.channel, 'id') else 0,
            layer3       = message.channel.id      if isinstance(message.channel, discord.Thread) else 0,
            layer4       = message.author.id,
            server_name  = message.guild.name      if message.guild else '#dm',
            channel_name = message.channel.name    if hasattr(message.channel, 'name') else '#dm',
            thread_name  = message.channel.name    if isinstance(message.channel, discord.Thread) else '',
            author_name     = message.author.name,
            author_fullname = message.author.global_name,
            author          = message.author.global_name,
            bot             = self.user,
            timestamp       = datetime.datetime.now(),
            date            = datetime.datetime.now().strftime("%d-%b-%Y"),
            time            = datetime.datetime.now().strftime("%H:%M:%S"),
            message         = prompt_text,
            attachments     = [a.url for a in message.attachments],
            reactions       = [str(r.emoji) for r in message.reactions]
        )

        if self.engine:
            self.engine.process(context)

        if context.response:
            reply = str(context.response)
            user.setdefault('History', []).append({
                'when':   datetime.datetime.utcnow().isoformat(),
                'prompt': text,
                'reply':  reply
            })

            xp_got, lvl_old, lvl_new = award_xp(user, base_xp=1)
            reply = f"💠 You earned **{xp_got} XP**.\n\n" + reply

            if lvl_new > lvl_old:
                perk = f"Level {lvl_new} Reward"
                user.setdefault('Perks', []).append(perk)
                reply += f"\n\n🎉 **Level Up!** You’re now Level {lvl_new} and unlocked **{perk}**."

            save_user(user)
            max_len = 2000
            for i in range(0, len(reply), max_len):
                await message.channel.send(reply[i:i+max_len])

if __name__ == "__main__":
    cfg   = dotenv_values('.env')
    TOKEN = cfg.get('DISCORD_TOKEN')
    URL   = cfg.get('SERVER_URL')
    TYPE  = cfg.get('SERVER_TYPE')
    MODEL = cfg.get('SERVER_MODEL')

    provider = ModelProvider(
        type     = TYPE,
        base_url = URL,
        api_key  = cfg.get('SERVER_API_KEY'),
        model    = MODEL
    )
    engine = SimpleEngine(id='bot-1')
    engine.model_provider = provider

    # now that we have a live LLM endpoint...
    quiz_mgr = QuizManager(llm_requester=engine.model_provider.request)

    bot = PersistingBot(token=TOKEN, engine=engine, promiscuous=False, debug=True)
    bot.run()
