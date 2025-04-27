## bot-1.py :: VaultDwellersBot with OwlMind + DynamoDB persistence
##

import os
import re
import datetime
from dotenv import dotenv_values

from owlmind.pipeline import ModelProvider
from owlmind.simple import SimpleEngine
from owlmind.discord import DiscordBot
from owlmind.bot import BotMessage

from user_store import get_or_create_user, save_user

class PersistingBot(DiscordBot):
    """
    Extends OwlMind’s DiscordBot to load/store user state in DynamoDB
    before & after each engine run.
    """
    async def on_message(self, message):
        # 1) Ignore non‐DM/non‐mention or bot itself
        if message.author == self.user or (
            not self.promiscuous and
            not (self.user in message.mentions or isinstance(message.channel, discord.DMChannel))
        ):
            return

        # 2) Strip mention tags
        text = re.sub(r"<@\d+>", "", message.content).strip()
        if not text:
            return

        # 3) Load or initialize user state
        user_id = str(message.author.id)
        user    = get_or_create_user(user_id)
        user['XP'] = user.get('XP', 0) + 1  # +1 XP just for showing up

        # 4) Build the OwlMind context
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

        # 5) Run through OwlMind’s engine
        if self.engine:
            self.engine.process(context)

        # 6) If we got a response, record & save user state, then send it
        if context.response:
            reply = str(context.response)

            # Record this interaction
            user.setdefault('History', []).append({
                'when':   datetime.datetime.utcnow().isoformat(),
                'prompt': text,
                'reply':  reply
            })

            # Example perk at 10 XP
            if user['XP'] >= 10 and 'First 10 XP' not in user.get('Perks', []):
                user.setdefault('Perks', []).append('First 10 XP')
                reply = "🎉 You’ve unlocked the “First 10 XP” perk!\n\n" + reply

            # Save back to DynamoDB
            save_user(user)

            # 7) Chunk & send
            max_len = 2000
            for i in range(0, len(reply), max_len):
                await message.channel.send(reply[i:i+max_len])

if __name__ == "__main__":
    # load .env
    cfg = dotenv_values('.env')
    TOKEN = cfg.get('DISCORD_TOKEN')
    URL   = cfg.get('SERVER_URL')
    TYPE  = cfg.get('SERVER_TYPE')
    MODEL = cfg.get('SERVER_MODEL')

    print("→", TYPE, URL, MODEL)

    # wire up OwlMind engine
    provider = ModelProvider(
        type     = TYPE,
        base_url = URL,
        api_key  = cfg.get('SERVER_API_KEY'),
        model    = MODEL
    )
    engine = SimpleEngine(id='bot-1')
    engine.model_provider = provider

    # launch our PersistingBot
    bot = PersistingBot(token=TOKEN, engine=engine, promiscuous=False, debug=True)
    bot.run()
