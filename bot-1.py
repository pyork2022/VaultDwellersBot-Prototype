##
## bot-1.py :: Kick off a chat-only Ollama Discord bot
##

from dotenv import dotenv_values
from owlmind.pipeline import ModelProvider
from owlmind.simple import SimpleEngine
from owlmind.discord import DiscordBot

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

    engine = SimpleEngine(id='bot-1')
    engine.model_provider = provider

    bot = DiscordBot(token=TOKEN, engine=engine, debug=True)
    bot.run()
