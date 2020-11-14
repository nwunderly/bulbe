import discord
import signal
import asyncio
import datetime
import yaml
import os
import sys
import traceback
import logging

from discord.ext import commands, tasks

from utils import utility
from utils.utility import setup_logger


logger = logging.getLogger('bot.best_starter')


class BestStarter(commands.AutoShardedBot):
    """
    Base class for Bulbe, handles low-level stuff
    """
    def __init__(self, command_prefix=None, **kwargs):
        super().__init__(command_prefix, **kwargs)
        self.properties = None
        self._exit_code = 0
        self.started_at = datetime.datetime.now()

    async def try_run(self, coro):
        try:
            return await coro
        except:
            logger.error(f"Encountered error in try_run:", exc_info=True)
            return

    async def on_ready(self):
        """
        Override this to override discord.Client on_ready.
        """
        logger.info('Logged in as {0.user}.'.format(self))

    async def ping_response(self, channel):
        await channel.send(embed=discord.Embed(title=f"{self._name} ({datetime.datetime.now() - self.started_at})",
                                               description=f"Prefix: `{self.command_prefix}`"))

    async def on_message(self, message):
        if message.author.bot:
            return
        if (await self.is_owner(message.author)) and message.content in [f'<@!{self.user.id}>', f'<@{self.user.id}>']:
            await self.ping_response(message.channel)
        await self.process_commands(message)

    async def on_error(self, event_method, *args, **kwargs):
        logger.error(f"Ignoring exception in {event_method}:\n{traceback.format_exc()}")

    async def on_command_error(self, ctx, exception):
        if isinstance(exception, commands.CommandInvokeError):
            logger.error(f"Error invoking command '{ctx.command.qualified_name}' / "
                              f"author {ctx.author.id}, guild {ctx.guild.id if ctx.guild else None}, channel {ctx.channel.id}, message {ctx.message.id}\n"
                              f"{traceback.format_exception(type(exception), exception, exception.__traceback__)}")

    async def setup(self):
        """
        Called when bot is started, before login.
        Use this for any async tasks to be performed before the bot starts.
        (THE BOT WILL NOT BE LOGGED IN WHEN THIS IS CALLED)
        """
        pass

    async def cleanup(self):
        """
        Called when bot is closed, before logging out.
        Use this for any async tasks to be performed before the bot exits.
        """
        pass

    async def read_properties(self):
        try:
            if (filename := f"{self._name}.yaml") in os.listdir(f"{utility.HOME_DIR}/configs"):
                with open(f"{utility.HOME_DIR}/configs/" + filename) as f:
                    properties = yaml.load(f, yaml.Loader)
            else:
                with open(f"{utility.HOME_DIR}/configs/default.yaml") as f:
                    properties = yaml.load(f, yaml.Loader)
            self.properties = self.Properties(properties)
            return True
        except yaml.YAMLError:
            return False

    def run(self, *args, **kwargs):
        logger.debug("Run method called.")
        super().run(*args, **kwargs)

    async def start(self, *args, **kwargs):
        logger.debug("Start method called.")
        try:
            self.loop.remove_signal_handler(signal.SIGINT)
            self.loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(self.close()))
        except NotImplementedError:
            pass
        # self.watchdog.start()
        # logger.info("Watchdog loop started.")
        logger.info("Setting up.")
        await self.setup()
        logger.debug("Setup complete.")
        logger.debug("Calling super().start method.")
        await super().start(*args, **kwargs)

    async def close(self, exit_code=0):
        logger.debug("RevBot: Received command to shut down. Beginning safe shutdown sequence.")
        self._exit_code = exit_code
        await self.cleanup()
        logger.debug("Closing connection to discord.")
        await super().close()

    class Properties:
        def __init__(self, properties):
            self.properties_dict = properties
            for key in properties.keys():
                value = properties[key]
                key = key.replace(" ", "_")
                setattr(self, key, value)

        async def convert(self, bot):
            converters = {
                "embed_color": lambda c: discord.Color(int(c, 16)),
                "socket": bool,  # deprecated
                "logging_channel": bot.get_channel
            }
            for key in self.__dict__:
                if key in converters.keys():
                    attr = getattr(self, key)
                    value = converters[key](attr)
                    setattr(self, key, value)

    def Embed(self, **kwargs):
        if not ("color" not in kwargs.keys() or kwargs['color'] is None) or ("colour" not in kwargs.keys() or kwargs['colour'] is None):
            kwargs['color'] = c if (c := getattr(self.properties, 'embed_color')) else discord.Color.blurple()

        return discord.Embed(**kwargs)
