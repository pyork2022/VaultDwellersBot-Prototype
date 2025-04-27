# base.py

class BotEngine:
    """
    Base class for all Bot Engines.
    """
    def __init__(self, id):
        self.id = id
        self.debug = False
        self.model_provider = None
        self.announcement = None

    def process(self, context):
        raise NotImplementedError("You must implement process() in subclass.")

    def reset(self):
        return None

    def is_action(self, text:str):
        return text.startswith('@')

class BotMessage(dict):
    """
    Very simple subclass of dict for BotMessages.
    """
    VERSION = "1.0"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
