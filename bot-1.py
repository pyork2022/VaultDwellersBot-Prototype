## bot-1.py :: Kick off a chat-only Ollama Discord bot
##

import owlmind.pipeline as _p
if hasattr(_p, 'BotPipeline'):    # or whatever class you found
    # override the method that does the fallback:
    orig = _p.BotPipeline.process
    def patched(self, ctx):
        # clear any lingering defaults
        if hasattr(ctx, 'response') and isinstance(ctx.response, str) and ctx.response.startswith("#### DEFAULT"):
            ctx.response = None
        return orig(self, ctx)
    _p.BotPipeline.process = patched

from dotenv import dotenv_values
from owlmind.pipeline import ModelProvider
from owlmind.simple import SimpleEngine
from owlmind.discord import DiscordBot

class CleanEngine(SimpleEngine):
    """
    A SimpleEngine override that retains /help, /info, /reload
    but bypasses OwlMind’s legacy rule fallback for all other messages.
    """
    def process(self, context):
        msg = context['message'].strip()

        # Handle built-in commands via the parent implementation
        if msg in ('/help', '/info', '/reload'):
            return super().process(context)

        # Otherwise, skip any rule-engine default and call the LLM directly
        if self.model_provider:
            context.response = self.model_provider.request(msg)
        else:
            context.response = None

if __name__ == '__main__':
    config = dotenv_values('.env')
    TOKEN = config.get('DISCORD_TOKEN')
    URL   = config.get('SERVER_URL')
    TYPE  = config.get('SERVER_TYPE')
    MODEL = config.get('SERVER_MODEL')

    # make sure these loaded
    print("→", TYPE, URL, MODEL)

    provider = ModelProvider(
        type=TYPE,
        base_url=URL,
        api_key=None,
        model=MODEL
    )

    engine = CleanEngine(id='bot-1')
    engine.model_provider = provider

    bot = DiscordBot(token=TOKEN, engine=engine, debug=True)
    bot.run()
