##
## OwlMind - Platform for Education and Experimentation with Hybrid Intelligent Systems
## bot.py :: Definitions for bot engine
## 
#  
# Copyright (c) 2024, The Generative Intelligence Lab @ FAU
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# Documentation and Getting Started:
#    https://github.com/genilab-fau/owlmind
#
#
# Disclaimer: 
# Generative AI has been used extensively while developing this package.
# 

from .agent import Agent, Plan
from .context import Context

##
## BASE CLASS FOR BOT MESSAGE
## This is the class received through BotBrain.process()

class BotMessage(Context):
    #BASE_STANDARD = '.;'
    """
    Message format being passed to/from BotBrain logic
    """
    def __init__(self, **kwargs):
        
        # Load default fields and update with parameters
        default_fields = {
            'layer1': 0,               # Server ID (guild ID or 0 for DM)
            'layer2': 0,               # Channel ID (or 0 for DM)
            'layer3': 0,               # Thread ID (0 if no thread)
            'layer4': None,            # Author ID
            'server_name': '',         # Server name (or '#dm' for direct message)
            'channel_name': '',        # Channel name (or '#dm' for DM)
            'thread_name': '',         # Thread name (empty if no thread)
            'author_name': '',         # Author name (username)
            'author_fullname': '',     # Author full name (global_name)
            'message': '',             # Message content
            'attachments': None,       # Attachments in the message
            'reactions': None          # Reactions to the message
        }

        default_fields.update(kwargs)
        
        # Initialize Context
        super().__init__(facts=default_fields)
        return 


##
## BASE CLASS FOR BOT ENGINE
##

class BotEngine(Agent):
    """
    BotBrain logic
    """  
    def __init__(self, id):
        self.debug = False
        self.announcement = None
        super().__init__(id)

    def process(self, context:BotMessage):
        super().process(context=context)


