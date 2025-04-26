# owlmind/simple.py
"""
SimpleEngine — forwards every incoming message straight to your ModelProvider.
"""

from .bot import BotEngine, BotMessage

class SimpleEngine(BotEngine):
    VERSION = "2.0"

    def __init__(self, id):
        super().__init__(id)
        # after you create your engine, don’t forget to assign:
        #    engine.model_provider = provider
        if not hasattr(self, 'model_provider') or self.model_provider is None:
            raise ValueError("SimpleEngine needs a model_provider (set engine.model_provider in bot-1.py)")
        return

    def process(self, context: BotMessage):
        # keep a little help command, if you like
        if context['message'] == '/help':
            context.response = (
                f"### SimpleEngine {self.id}\n"
                "* Just echoes anything you type through your AI model.\n"
                "* Type anything to see a response.\n"
            )
            return

        # everything else goes to the AI
        prompt = context['message']
        context.response = self.model_provider.request(prompt)
        return
