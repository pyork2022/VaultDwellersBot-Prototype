from .bot import BotEngine, BotMessage

class SimpleEngine(BotEngine):
    """
    A “chat-only” engine: it still honors /help, /info and /reload,
    but otherwise forwards every incoming message to your ModelProvider.
    """

    VERSION = "1.2"

    def __init__(self, id):
        super().__init__(id)
        self.model_provider = None
        return

    def process(self, context: BotMessage):
        msg = context['message']

        if msg == '/help':
            context.response = (
                f'### Version: {BotMessage.VERSION}\n'
                '### Help\n'
                '* `/info` – show configuration and engine state\n'
                '* `/reload` – reload (no‐op)\n'
            )

        elif msg == '/info':
            context.response = f'### Version: {BotMessage.VERSION}\n'
            if self.model_provider:
                context.response += (
                    '### Model Provider:\n'
                    f'* type: {self.model_provider.type}\n'
                    f'* url: {self.model_provider.base_url}\n'
                )
            else:
                context.response += "### No ModelProvider configured\n"

        elif msg == '/reload':
            context.response = (
                f'### Version: {BotMessage.VERSION}\n'
                '*Reload is not needed in AI-only mode.*\n'
            )

        else:
            # Everything else goes to your AI API
            if self.model_provider:
                context.response = self.model_provider.request(msg)
            else:
                context.response = "!!ERROR!! No AI provider configured."

        return
