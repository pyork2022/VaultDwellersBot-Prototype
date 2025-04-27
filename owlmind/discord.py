import re
import discord
import datetime
import io
from owlmind.bot import BotMessage, BotEngine  # Absolute import

class DiscordBot(discord.Client):
    """
    DiscordBot provides logic to connect the Discord Runner with OwlMind's BotMind, 
    forming a multi-layered context in BotMessage by collecting elements of the Discord conversation
    (layer1=user, layer2=thread, layer3=channel, layer4=guild), and aggregating attachments, reactions, and other elements.
    """

    def __init__(self, token, engine: BotEngine, promiscuous: bool = False, debug: bool = False):
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

        # Initialize the parent class correctly
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
        if message.author == self.user or (
            not self.promiscuous and
            not (self.user in message.mentions or isinstance(message.channel, discord.DMChannel))
        ):
            return

        # Strip out any @mention tags
        text = re.sub(r"<@\d+>", "", message.content).strip()

        # Build context
        attachments = [a.url for a in message.attachments]
        reactions = [str(r.emoji) for r in message.reactions]
        context = BotMessage(
            layer1=message.guild.id if message.guild else 0,
            layer2=message.channel.id if hasattr(message.channel, 'id') else 0,
            layer3=message.channel.id if isinstance(message.channel, discord.Thread) else 0,
            layer4=message.author.id,
            server_name=message.guild.name if message.guild else '#dm',
            channel_name=message.channel.name if hasattr(message.channel, 'name') else '#dm',
            thread_name=message.channel.name if isinstance(message.channel, discord.Thread) else '',
            author_name=message.author.name,
            author_fullname=message.author.global_name,
            author=message.author.global_name,
            bot=self.user,
            timestamp=datetime.datetime.now(),
            date=datetime.datetime.now().strftime("%d-%b-%Y"),
            time=datetime.datetime.now().strftime("%H:%M:%S"),
            message=text,
            attachments=attachments,
            reactions=reactions
        )

        if self.debug:
            print(f'PROCESSING: ctx={context}')

        if self.engine:
            self.engine.process(context)

        # Send back the response, chunked if over 2000 chars
        if context.response:
            resp = str(context.response)
            max_len = 2000

            if len(resp) <= max_len:
                await message.channel.send(resp)
            else:
                for i in range(0, len(resp), max_len):
                    await message.channel.send(resp[i:i + max_len])

        return

    def run(self):
        super().run(self.token)
