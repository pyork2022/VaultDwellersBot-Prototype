# owlmind/simple.py

from .base import BotEngine, BotMessage

class SimpleEngine(BotEngine):
    """
    Chat-only engine: honors /help, /info, /reload,
    otherwise shunts the text straight to your ModelProvider.
    """
    VERSION = "1.2"

    def __init__(self, id):
        super().__init__(id)
        self.model_provider = None

    def process(self, context: BotMessage):
        msg = context['message']

        if msg == '/help':
            context.response = (
                f'### Version: {BotMessage.VERSION}\n'
                '### Help\n'
                '* `/info` – show engine info\n'
                '* `/reload` – no-op in chat-only mode\n'
            )

        elif msg == '/info':
            context.response = f'### Version: {BotMessage.VERSION}\n'
            if self.model_provider:
                context.response += (
                    f'* provider: {self.model_provider.type}\n'
                    f'* url:      {self.model_provider.base_url}\n'
                    f'* model:    {self.model_provider.model}\n'
                )
            else:
                context.response += "### No ModelProvider configured\n"

        elif msg == '/reload':
            context.response = (
                f'### Version: {BotMessage.VERSION}\n'
                '*Reload not needed in AI-only mode.*\n'
            )

        else:
            if self.model_provider:
                # forward everything else to the Llama server (or OpenAI, etc)
                context.response = self.model_provider.request(msg)
            else:
                context.response = "!!ERROR!! No model provider configured"
