from dotenv import dotenv_values
from owlmind.pipeline import ModelProvider
from owlmind.simple import SimpleEngine
from owlmind.discord import DiscordBot

if __name__ == '__main__':

    # load credentials from .env
    config    = dotenv_values('.env')
    TOKEN     = config.get('DISCORD_TOKEN')
    URL       = config.get('SERVER_URL')
    MODEL     = config.get('SERVER_MODEL')
    TYPE      = config.get('SERVER_TYPE')
    API_KEY   = config.get('SERVER_API_KEY')

    # set up the AI provider
    provider = ModelProvider(
        type=TYPE,
        base_url=URL,
        api_key=API_KEY,
        model=MODEL
    ) if URL else None

    # create engine and attach provider
    engine = SimpleEngine(id='bot-1')
    engine.model_provider = provider

    # launch Discord bot
    bot = DiscordBot(token=TOKEN, engine=engine, debug=True)
    bot.run()
