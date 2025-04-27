## bot-1.py :: Kick off a chat-only Ollama Discord bot with DynamoDB state
##

import os
import re
import time
import discord
import requests
import datetime
from dotenv import load_dotenv

# DynamoDB helper
from user_store import get_or_create_user, save_user

# ──────────────────────────────────────────────────────────────────────────────
# Minimal Ollama ModelProvider
# ──────────────────────────────────────────────────────────────────────────────
class ModelProvider:
    def __init__(self, base_url, model):
        self.base_url = base_url.rstrip('/')
        self.model    = model

    def request(self, prompt: str) -> str:
        url     = f"{self.base_url}/api/generate"
        payload = {
            "model":  self.model,
            "prompt": prompt,
            "stream": False
        }
        start = time.time()
        resp  = requests.post(url, json=payload, timeout=30)
        if resp.status_code != 200:
            return f"!!ERROR!! HTTP {resp.status_code}: {resp.text}"
        return resp.json().get("response", "")

# ──────────────────────────────────────────────────────────────────────────────
# Discord bot
# ──────────────────────────────────────────────────────────────────────────────
class VaultDwellersBot(discord.Client):
    def __init__(self, token, provider, debug=False):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.token    = token
        self.provider = provider
        self.debug    = debug

    async def on_ready(self):
        print(f"✅ Logged in as {self.user}")

    async def on_message(self, message):
        # ignore the bot itself
        if message.author == self.user:
            return

        # strip out @mentions
        text = re.sub(r"<@\d+>", "", message.content).strip()
        if not text:
            return

        # ───────────────
        # 1) Load (or initialize) user state
        uid  = str(message.author.id)
        user = get_or_create_user(uid)

        # give 1 XP for any message
        user['XP'] += 1
        # ───────────────

        # 2) Call the LLM
        reply = self.provider.request(text)

        # ───────────────
        # 3) Record history and unlock simple perks
        user['History'].append({
            'when':   datetime.datetime.utcnow().isoformat(),
            'prompt': text,
            'reply':  reply
        })

        # Example: at 10 XP unlock a “First 10 XP” perk
        if user['XP'] >= 10 and 'First 10 XP' not in user['Perks']:
            user['Perks'].append('First 10 XP')
            reply = "🎉 You’ve unlocked the “First 10 XP” perk!\n\n" + reply

        # Persist back to DynamoDB
        save_user(user)
        # ───────────────

        # 4) Chunk & send the reply
        max_len = 2000
        for i in range(0, len(reply), max_len):
            await message.channel.send(reply[i:i+max_len])

    def run(self):
        super().run(self.token)

# ──────────────────────────────────────────────────────────────────────────────
# Launcher
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    load_dotenv()  # loads .env into os.environ

    TOKEN = os.getenv("DISCORD_TOKEN")
    URL   = os.getenv("SERVER_URL")
    MODEL = os.getenv("SERVER_MODEL")
    AWS_REGION = os.getenv("AWS_REGION")

    print(f"→ URL: {URL!r}, MODEL: {MODEL!r}, AWS_REGION: {AWS_REGION!r}")

    provider = ModelProvider(base_url=URL, model=MODEL)
    bot      = VaultDwellersBot(token=TOKEN, provider=provider, debug=True)
    bot.run()
