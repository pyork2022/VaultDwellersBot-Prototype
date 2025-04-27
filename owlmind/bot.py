# owlmind/bot.py

import datetime
from .context import Context

class BotMessage(Context):
    """
    A thin wrapper over Context for Discord messages,
    carrying a `.response` field that your engines fill in.
    """
    VERSION = "1.0"

    def __init__(self, *,
                 layer1, layer2, layer3, layer4,
                 server_name, channel_name, thread_name,
                 author_name, author_fullname, author, bot,
                 timestamp, date, time, message,
                 attachments=None, reactions=None):
        super().__init__(facts={
            "layer1":       layer1,
            "layer2":       layer2,
            "layer3":       layer3,
            "layer4":       layer4,
            "server_name":  server_name,
            "channel_name": channel_name,
            "thread_name":  thread_name,
            "author_name":     author_name,
            "author_fullname": author_fullname,
            "author":          author,
            "bot":             bot,
            "timestamp":       timestamp,
            "date":            date,
            "time":            time,
            "message":         message,
            "attachments":     attachments or [],
            "reactions":       reactions or []
        })
        self.response = None

class BotEngine:
    """
    Base class for all OwlMind engines.
    Subclasses should override `process(self, context:BotMessage)`.
    """
    def __init__(self, id):
        self.id = id
        self.announcement = None
        self.debug = False
