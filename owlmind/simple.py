from .bot import BotEngine, BotMessage

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
            # everything else goes to your Llama server
            if self.model_provider:
                print(f"[AI DEBUG] → POST to: {self.model_provider.req_maker.url_chat(self.model_provider.base_url)}")
                print(f"[AI DEBUG] → payload: {{'model':'{self.model_provider.model}','prompt':'{msg}'}}")
                context.response = self.model_provider.request(msg)
                print(f"[AI DEBUG] ← {self.model_provider.delta}s")
            else:
                context.response = "!!ERROR!! No model provider configured"
