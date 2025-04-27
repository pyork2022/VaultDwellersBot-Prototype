from dotenv import dotenv_values
from owlmind.pipeline import ModelProvider
from owlmind.simple import SimpleEngine
from owlmind.discord import DiscordBot
import sys

if __name__ == '__main__':

    # load token from .env
    config = dotenv_values('.env')

    # use .get() so missing values return None instead of raising:
    TOKEN    = config.get('DISCORD_TOKEN')
    URL      = config.get('SERVER_URL')
    MODEL    = config.get('SERVER_MODEL')
    TYPE     = config.get('SERVER_TYPE')
    API_KEY  = config.get('SERVER_API_KEY')

    # sanity check that you actually got a token
    if not TOKEN:
        print("Missing DISCORD_TOKEN in .env")
        sys.exit(1)

    # configure the model provider (OpenAI, Ollama, etc)
    provider = None
    if URL:
        provider = ModelProvider(type=TYPE, base_url=URL, api_key=API_KEY, model=MODEL)

    # instantiate your engine and inject the provider
    engine = SimpleEngine(id='bot-1')
    engine.model_provider = provider
    # you can remove the CSV‐loading line tomorrow once you rip out the rules:
    engine.load('rules/bot-rules-1.csv')

    # start the Discord bot
    bot = DiscordBot(token=TOKEN, engine=engine, debug=True)
    bot.run()
