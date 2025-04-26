##
## OwlMind - Platform for Education and Experimentation with Hybrid Intelligent Systems
## discord.py :: Bot Runner for Discord
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
# Disclaimer: 
# Generative AI has been used extensively while developing this package.
# 

import re
import discord
import datetime
from .bot import BotMessage, BotEngine

class DiscordBot(discord.Client):
    """
    DiscordBot provides logic to connect the Discord Runner with OwlMind's BotMind, 
    forming a multi-layered context in BotMessage by collecting elements of the Discord conversation
    (layer1=user, layer2=thread, layer3=channel, layer4=guild), and aggregating attachments, reactions, and other elements.

    @EXAMPLE
    How to use this class:

    engine = MyBotEngine(.) 
    TOKEN = {My Token}
    bot = DiscordBot(token=TOKEN, engine=MyBotMind, debug=True)
    bot.run()
    """
    def __init__(self, token, engine:BotEngine, promiscuous:bool=False, debug:bool=False):
        self.token = token
        self.promiscuous = promiscuous
        self.debug = debug
        self.engine = engine
        if self.engine: self.engine.debug = debug

        ## Discord attributes
        intents = discord.Intents.default()
        intents.messages = True
        intents.reactions = True
        intents.message_content = True
        #intents.guilds = True
        #intents.members = True

        super().__init__(intents=intents)
        return 

    async def on_ready(self):
        print(f'Bot is running as: {self.user.name}.')
        if self.debug: print(f'Debug is on!')
        if self.engine: 
            print(f'Bot is connected to {self.engine.__class__.__name__}({self.engine.id}).') 
            if self.engine.announcement: print(self.engine.announcement)
            self.engine.debug = self.debug
        
    async def on_message(self, message):
        # CUT-SHORT conditions
        # Only process if message does not come from itself, the bot is configured as promiscuous, or this is a DM or mentions the bot
        if message.author == self.user or \
            (not self.promiscuous and not (self.user in message.mentions or isinstance(message.channel, discord.DMChannel))):
           if self.debug: print(f'IGNORING: orig={message.author.name}, dest={self.user}') 
           return

        # Remove calling @Mention if in the message
        text = re.sub(r"<@\d+>", "", message.content,).strip()

        # Collect attachments, reactions and others.
        attachments = [attachment.url for attachment in message.attachments]
        reactions = [str(reaction.emoji) for reaction in message.reactions]

        # Create context
        context = BotMessage(
                layer1       = message.guild.id if message.guild else 0,
                layer2       = message.channel.id if hasattr(message.channel, 'id') else 0,
                layer3       = message.channel.id if isinstance(message.channel, discord.Thread) else 0,
                layer4       = message.author.id,
                server_name  = message.guild.name if message.guild else '#dm',
                channel_name    = message.channel.name if hasattr(message.channel, 'name') else '#dm',
                thread_name     = message.channel.name if isinstance(message.channel, discord.Thread) else '',
                author_name     = message.author.name,
                author_fullname = message.author.global_name,
                author          = message.author.global_name,
                bot             = self.user,
                timestamp=datetime.datetime.now(),
                date=datetime.datetime.now().strftime("%d-%b-%Y"),  # Format date as '25-Feb-2024'
                time=datetime.datetime.now().strftime("%H:%M:%S"),  # Format time as '20:58:14'
                message         = text,
                attachments     = attachments,
                reactions       = reactions)

        if self.debug: print(f'PROCESSING: ctx={context}')
                               
        # Process through engine
        if self.engine:
            self.engine.process(context)

        # If the immediate processing of Context generated a result (sync mode), return it through the bot interface
        # @TODO return attachments, issue reactions, etc
        if context.response:
            await message.channel.send(context.response)
        return

    def run(self):
        super().run(self.token)
