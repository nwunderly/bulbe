import json
import logging
import random
import discord

from discord.ext import tasks, commands

from bulbe.base import BestStarter
from bulbe.settings import Settings
from utils.checks import global_checks
# from utils.db import Database

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
    def __init__(self, token, db_url, **kwargs):
        super().__init__(command_prefix=prefix, case_insensitive=True,
                         description='Best Bot <3', **kwargs)
        self.__token = token
        # self.__db_url = db_url
        self._nwunder = None
        self._running = False
        self._user_blacklist = []
        self._guild_blacklist = []
        # self.db = Database(db_url)
        self.help_command = commands.MinimalHelpCommand()
        self.add_check(global_checks)
        logger.info(f'Initialization complete.')

    async def on_ready(self):
        logger.info('Logged in as {0.user}.'.format(self))
        self._nwunder = await self.fetch_user(204414611578028034)
        if not self._running:
            self.update_presence.start()
        self._running = True
        logger.info(f"Bot is ready, version {Settings.version}!")

    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild:
            await self.process_mention(message)
            await self.process_commands(message)
        else:
            await self.process_direct_messages(message)

    async def on_command_completion(self, ctx):
        logger.debug(f"Command '{ctx.command.qualified_name}' invoked / "
                     f"author {ctx.author.id}, guild {ctx.guild.id if ctx.guild else None}, channel {ctx.channel.id}, message {ctx.message.id}")
        # await self.update_stats(ctx)

    async def process_direct_messages(self, message):
        if message.guild:
            return
        attachments = f'             \n'.join([str(a.url) for a in message.attachments]) if message.attachments else None
        logger.info(f"Received direct message from {message.author} ({message.author.id}): \n"
                    f"{message.content}\n"
                    f"Attachments: {attachments}")
        channel = Settings.logging_channel
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
        e = discord.Embed(title=f"Bulbe v{Settings.version}",
                          color=Settings.embed_color,
                          description=f"Prefix: `{p}`")
        return e

    @tasks.loop(minutes=20)
    async def update_presence(self):
        activity = None
        name = random.choice(Settings.activities)
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

    def run(self):
        super().run(self.__token)

    async def setup(self):
        logger.info('Connecting to database.')
        # await self.db.connect()
        # self.load_blacklists()
        await self.load_cogs(Settings.cogs)

    async def cleanup(self):
        logger.info("Closing cog aiohttp clients.")
        for name, cog in self.cogs.items():
            try:
                await cog.session.close()
            except AttributeError:
                pass
        logger.info("Dumping data.")
        self.dump_blacklists()
