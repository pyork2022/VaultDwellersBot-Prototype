## bot-1.py :: VaultDwellersBot with OwlMind + DynamoDB + /start & /stats
##

import os
import re
import datetime
from dotenv import dotenv_values
import discord

from owlmind.pipeline import ModelProvider
from owlmind.simple import SimpleEngine
from owlmind.discord import DiscordBot
from owlmind.bot import BotMessage

from user_store import get_or_create_user, save_user

class PersistingBot(DiscordBot):
    """
    Extends OwlMind’s DiscordBot to:
     • Handle /start & /stats before AI
     • Load/store user state in DynamoDB
    """
    async def on_message(self, message):
        # 1) Ignore the bot itself, or non-mentions if not promiscuous
        if message.author == self.user or (
            not self.promiscuous and
            not (self.user in message.mentions or isinstance(message.channel, discord.DMChannel))
        ):
            return

        # 2) Strip out <@…> mentions
        text = re.sub(r"<@\d+>", "", message.content).strip()
        if not text:
            return

        # 3) /start: allocate SPECIAL for brand-new users
        if text.lower().startswith("/start"):
            uid  = str(message.author.id)
            user = get_or_create_user(uid)
            # only allow if XP==0
            if user.get("XP", 0) != 0:
                return await message.channel.send("You’ve already set up your SPECIAL stats.")
            return await message.channel.send(
                "Welcome to VaultDwellersBot! You have **28** points to assign across your SPECIAL stats.\n"
                "Reply with 7 comma-separated integers (must sum to 28) in order:\n"
                "`Strength, Perception, Endurance, Charisma, Intelligence, Agility, Luck`\n"
                "Example: `5,5,5,5,5,2,1`"
            )

        # 4) Handle the user’s allocation reply
        if re.fullmatch(r"\d+(,\s*\d+){6}", text):
            parts = [int(x) for x in text.split(",")]
            if sum(parts) != 28:
                return await message.channel.send("❌ That doesn’t sum to 28—try again.")
            stats = dict(zip(
                ["Strength","Perception","Endurance","Charisma","Intelligence","Agility","Luck"],
                parts
            ))
            uid  = str(message.author.id)
            user = get_or_create_user(uid)
            user["SPECIAL"] = stats
            save_user(user)
            return await message.channel.send(f"SPECIAL set to {stats}!\nYou can now send `/stats` or just chat.")

        # 5) /stats: show profile
        if text.lower().strip() == "/stats":
            uid  = str(message.author.id)
            user = get_or_create_user(uid)
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

        # 6) Load/create user record & bump XP
        uid  = str(message.author.id)
        user = get_or_create_user(uid)
        user['XP'] = user.get('XP', 0) + 1

        # 7) Build OwlMind context
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
            message         = text,
            attachments     = [a.url for a in message.attachments],
            reactions       = [str(r.emoji) for r in message.reactions]
        )

        # 8) Run through OwlMind engine
        if self.engine:
            self.engine.process(context)

        # 9) If we got an AI response, record & save, then send
        if context.response:
            reply = str(context.response)

            # record history
            user.setdefault('History', []).append({
                'when':   datetime.datetime.utcnow().isoformat(),
                'prompt': text,
                'reply':  reply
            })

            # example perk at 10 XP
            if user['XP'] >= 10 and 'First 10 XP' not in user.get('Perks', []):
                user.setdefault('Perks', []).append('First 10 XP')
                reply = "🎉 You’ve unlocked the “First 10 XP” perk!\n\n" + reply

            # persist update
            save_user(user)

            # chunk & send
            max_len = 2000
            for i in range(0, len(reply), max_len):
                await message.channel.send(reply[i:i+max_len])

if __name__ == "__main__":
    # load env
    cfg = dotenv_values('.env')
    TOKEN = cfg.get('DISCORD_TOKEN')
    URL   = cfg.get('SERVER_URL')
    TYPE  = cfg.get('SERVER_TYPE')
    MODEL = cfg.get('SERVER_MODEL')

    print("→", TYPE, URL, MODEL)

    # set up OwlMind
    provider = ModelProvider(
        type     = TYPE,
        base_url = URL,
        api_key  = cfg.get('SERVER_API_KEY'),
        model    = MODEL
    )
    engine = SimpleEngine(id='bot-1')
    engine.model_provider = provider

    # launch PersistingBot in non-promiscuous mode
    bot = PersistingBot(token=TOKEN, engine=engine, promiscuous=False, debug=True)
    bot.run()
