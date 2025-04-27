from dotenv import dotenv_values
from owlmind.pipeline import ModelProvider
from owlmind.simple   import SimpleEngine
from owlmind.discord  import DiscordBot

if __name__ == '__main__':
    cfg   = dotenv_values('.env')
    TOKEN = cfg['DISCORD_TOKEN']
    URL   = cfg['SERVER_URL']
    MODEL = cfg.get('SERVER_MODEL')

    # Ollama-only provider
    provider = ModelProvider(base_url=URL, model=MODEL)

    engine = SimpleEngine(id='bot-1')
    engine.model_provider = provider

    bot = DiscordBot(token=TOKEN, engine=engine, debug=True)
    bot.run()
