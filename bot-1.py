from dotenv import dotenv_values
from owlmind.pipeline import ModelProvider
from owlmind.simple import SimpleEngine
from owlmind.discord import DiscordBot

if __name__ == '__main__':
    # load token from .env
    config = dotenv_values('.env')
    TOKEN    = config['']
    URL      = config.get('SERVER_URL')
    MODEL    = config.get('SERVER_MODEL')
    TYPE     = config.get('SERVER_TYPE')
    API_KEY  = config.get('SERVER_API_KEY')

    # configure the AI provider
    provider = ModelProvider(
        type     = TYPE,
        base_url = URL,
        api_key  = API_KEY,
        model    = MODEL
    ) if URL else None

    # set up our engine without any CSV rules
    engine = SimpleEngine(id='bot-1')
    engine.model_provider = provider
    # engine.load('rules/bot-rules-1.csv')  # no rule-file, AI handles it all

    # start the Discord bot
    bot = DiscordBot(token=TOKEN, engine=engine, debug=True)
    bot.run()
