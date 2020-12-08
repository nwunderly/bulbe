import json
import logging
import random

import discord
from discord.ext import tasks, commands

from bulbe.base_bot import BestStarter
from bulbe.settings import Settings
from utils import checks

logger = logging.getLogger('bot.bulbe')


def prefix(_bot, message, only_guild_prefix=False):
    default = Settings.prefix
    if not message.guild:
        return commands.when_mentioned(_bot, message) + [default]
    if _bot.config:
        config = _bot.config.get_config(message.guild)
        p = config['prefix']
    else:
        p = None
    p = p if p else default
    if only_guild_prefix:
        return p
    else:
        return commands.when_mentioned(_bot, message) + [p]


class Bulbe(BestStarter):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=prefix, case_insensitive=True,
                         description='Best Bot <3', **kwargs)
        self._nwunder = None
        self.config = None
        self.properties = None
        self._user_blacklist = []
        self._guild_blacklist = []
        self.table = None
        self.help_command = commands.MinimalHelpCommand()
        logger.info(f'Initialization complete.')
        self.add_check(checks.global_checks)

    async def on_ready(self):
        logger.info('Logged in as {0.user}.'.format(self))
        self._nwunder = await self.fetch_user(204414611578028034)
        if self.properties:
            logger.info("Converting properties.")
            await self.properties.convert(self)
        else:
            logger.error("on_ready called but Properties object has not been defined.")
        self.update_presence.start()
        logger.info(f"Bot is ready, version {self.properties.version}!")

    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild:
            await self.process_mention(message)
            await self.process_commands(message)
        else:
            await self.process_direct_messages(message)

    async def on_command_completion(self, ctx):
        logger.info(f"Command '{ctx.command.qualified_name}' invoked / "
                    f"author {ctx.author.id}, guild {ctx.guild.id if ctx.guild else None}, channel {ctx.channel.id}, message {ctx.message.id}")
        # await self.update_stats(ctx)

    async def process_direct_messages(self, message):
        if message.guild:
            return
        attachments = f'             \n'.join([str(a.url) for a in message.attachments]) if message.attachments else None
        logger.info(f"Received direct message from {message.author} ({message.author.id}): \n"
                    f"{message.content}\n"
                    f"Attachments: {attachments}")
        channel = self.properties.logging_channel
        if len(message.content) > 1500:
            content = message.clean_content[:1500] + f".... {len(message.clean_content)}"
        else:
            content = message.clean_content
        forward_message = f"Received direct message from {message.author} ({message.author.id}):\n{content}"
        forward_message += ("\nAttachments:\n" + '\n'.join([str(a.url) for a in message.attachments])) if message.attachments else ""
        await channel.send(forward_message)

    async def process_mention(self, message):
        if message.content in [self.user.mention, '<@!%s>' % self.user.id]:
            await message.channel.send(embed=self.get_embed(message))

    def get_embed(self, message=None):
        p = self.command_prefix(self, message, only_guild_prefix=True)
        e = discord.Embed(title=f"Bulbe v{self.properties.version}",
                          color=self.properties.embed_color,
                          description=f"Prefix: `{p}`")
        return e

    @tasks.loop(minutes=20)
    async def update_presence(self):
        activity = None
        name = random.choice(self.properties.activities)
        if name.lower().startswith("playing "):
            activity = discord.Game(name.replace("playing ", ""))
        elif name.lower().startswith("watching "):
            activity = discord.Activity(type=discord.ActivityType.watching,
                                        name=name.replace("watching", ""))
        elif name.lower().startswith("listening to "):
            activity = discord.Activity(type=discord.ActivityType.listening,
                                        name=name.replace("listening to ", ""))
        if activity:
            await self.change_presence(activity=activity)

    def blacklisted(self, *ids):
        for i in ids:
            if i in self._user_blacklist or i in self._guild_blacklist:
                return True
        return False

    def load_blacklists(self):
        with open('/data/user_blacklist.json') as fp:
            data = json.load(fp)
            self._user_blacklist = set(data)
        with open('/data/guild_blacklist.json') as fp:
            data = json.load(fp)
            self._guild_blacklist = set(data)

    def dump_blacklists(self):
        with open('/data/user_blacklist.json') as fp:
            data = list(self._user_blacklist)
            json.dump(data, fp)
        with open('/data/guild_blacklist.json') as fp:
            data = list(self._guild_blacklist)
            json.dump(data, fp)

    async def setup(self):
        logger.info('Loading configurations.')
        # TODO: any config data that needs to be loaded

        logger.info('Connecting to database.')
        # TODO: establish database connection

        logger.info('Loading json data.')
        self.load_blacklists()

        logger.info("Loading cogs.")
        for cog in self.properties.cogs:
            try:
                self.load_extension(cog)
                logger.info(f"-> Loaded {cog}.")
            except Exception:
                logger.exception(f"-> Failed to load extension {cog}.")

    async def cleanup(self):
        logger.info("Closing cog aiohttp clients.")
        for name, cog in self.cogs.items():
            try:
                await cog.session.close()
            except AttributeError:
                pass
        logger.info("Dumping data.")
        self.dump_blacklists()


bot = Bulbe()
