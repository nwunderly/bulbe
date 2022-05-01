import typing

import aiohttp
import aionasa
from auth import NASA_API_KEY
from discord.ext import commands

from bulbe.base import Cog
from utils.converters import Language
from utils.helpers import fetch_previous_message
from utils.translate import Translate


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

        self.translate_api = Translate()
        self.nasa_apod_api = aionasa.APOD(NASA_API_KEY, self.session)

    async def cleanup(self):
        await self.session.close()

    @commands.command(aliases=["t"])
    async def translate(
        self,
        ctx,
        lang: typing.Optional[Language] = "en",
        *,
        text: commands.clean_content = None,
    ):
        """Translates a message into a language of your choice.
        Defaults to English. If no text to translate is specified, uses the current channel's previous message."""
        if not lang:
            lang = "en"
        if not text:
            prev = await fetch_previous_message(ctx.message)
            text = prev.content
        translation, language = await self.translate_api.translate(text, lang=lang)
        await ctx.send(f"(from {language}) {translation}")

    @commands.command()
    async def lmgtfy(self, ctx, *, search):
        """Let me google that for you."""
        q = "+".join(search.split())
        await ctx.send(f"<https://lmgtfy.com/?q={q}>")


def setup(bot):
    bot.add_cog(Fun(bot))
