from discord.ext import commands

from bulbe.base import Cog


class Stats(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        pass


def setup(bot):
    bot.add_cog(Stats(bot))
