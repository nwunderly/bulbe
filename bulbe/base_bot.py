import asyncio
import datetime
import logging
import signal
import traceback

from discord.ext import commands

logger = logging.getLogger('bot.best_starter')


class BestStarter(commands.AutoShardedBot):
    """
    Base class for Bulbe, handles low-level stuff
    """
    def __init__(self, command_prefix=None, **kwargs):
        super().__init__(command_prefix, **kwargs)
        self._exit_code = 0
        self.started_at = datetime.datetime.now()

    async def on_ready(self):
        """
        Override this to override discord.Client on_ready.
        """
        logger.info('Logged in as {0.user}.'.format(self))

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
        logger.info("Setting up.")
        await self.setup()
        logger.info("Setup complete. Logging in.")
        await super().start(*args, **kwargs)

    async def close(self, exit_code=0):
        self._exit_code = exit_code
        await self.cleanup()
        logger.debug("Closing connection to discord.")
        await super().close()

