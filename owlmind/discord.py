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
import io              # for optional file fallback
from .bot import BotMessage, BotEngine

class DiscordBot(discord.Client):
    """
    DiscordBot provides logic to connect the Discord Runner with OwlMind's BotMind, 
    forming a multi-layered context in BotMessage by collecting elements of the Discord conversation
    (layer1=user, layer2=thread, layer3=channel, layer4=guild), and aggregating attachments, reactions, and other elements.
    """

    def __init__(self, token, engine:BotEngine, promiscuous:bool=False, debug:bool=False):
        self.token = token
        self.promiscuous = promiscuous
        self.debug = debug
        self.engine = engine
        if self.engine:
            self.engine.debug = debug

        # Discord intents
        intents = discord.Intents.default()
        intents.messages = True
        intents.reactions = True
        intents.message_content = True

        super().__init__(intents=intents)

    async def on_ready(self):
        print(f'Bot is running as: {self.user.name}.')
        if self.debug:
            print(f'Debug is on!')
        if self.engine:
            print(f'Bot is connected to {self.engine.__class__.__name__}({self.engine.id}).')
            if self.engine.announcement:
                print(self.engine.announcement)
            self.engine.debug = self.debug
        
    async def on_message(self, message):
        # Only process user messages (DMs or mentions, unless promiscuous)
        if message.author == self.user or (
            not self.promiscuous and
            not (self.user in message.mentions or isinstance(message.channel, discord.DMChannel))
        ):
            if self.debug:
                print(f'IGNORING: orig={message.author.name}, dest={self.user}')
            return

        # Strip out any @mention tags
        text = re.sub(r"<@\d+>", "", message.content).strip()

        # Build context
        attachments = [a.url for a in message.attachments]
        reactions   = [str(r.emoji) for r in message.reactions]
        context = BotMessage(
            layer1       = message.guild.id        if message.guild else 0,
            layer2       = message.channel.id      if hasattr(message.channel, 'id') else 0,
            layer3       = message.channel.id      if isinstance(message.channel, discord.Thread) else 0,
            layer4       = message.author.id,
            server_name  = message.guild.name      if message.guild else '#dm',
            channel_name = message.channel.name    if hasattr(message.channel, 'name') else '#dm',
            thread_name  = message.channel.name    if isinstance(message.channel, discord.Thread) else '',
            author_name     = message.author.name,
            author_fullname = message.author.global_name,
            author          = message.author.global_name,
            bot             = self.user,
            timestamp       = datetime.datetime.now(),
            date            = datetime.datetime.now().strftime("%d-%b-%Y"),
            time            = datetime.datetime.now().strftime("%H:%M:%S"),
            message         = text,
            attachments     = attachments,
            reactions       = reactions
        )

        if self.debug:
            print(f'PROCESSING: ctx={context}')

        # Run through engine
        if self.engine:
            self.engine.process(context)

        # Send back the response, chunked if over 2000 chars
        if context.response:
            resp = str(context.response)
            max_len = 2000

            if len(resp) <= max_len:
                await message.channel.send(resp)
            else:
                # Chunking
                for i in range(0, len(resp), max_len):
                    await message.channel.send(resp[i:i+max_len])

                # --- Or, as an alternative, you could send as a file:
                # buf = io.BytesIO(resp.encode('utf-8'))
                # file = discord.File(buf, filename="response.txt")
                # await message.channel.send("Response was too long, sending as file:", file=file)

        return

    def run(self):
        super().run(self.token)
