import typing
import aiohttp
import discord

from discord.ext import commands
from aionasa.utils import date_strptime

from utils.constants import red_tick
from utils.helpers import fetch_previous_message
from utils.converters import Language
from utils.translate import Translate
from utils.nasa import NASA
from bulbe.settings import Settings
from bulbe.base import Cog



class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

        self.translate_api = Translate()
        self.nasa_api = NASA(self.session)

    async def cleanup(self):
        await self.session.close()

    @commands.command(aliases=['t'])
    async def translate(self, ctx, lang: typing.Optional[Language] = 'en', *, text: commands.clean_content = None):
        """Translates a message into a language of your choice.
        Defaults to English. If no text to translate is specified, uses the current channel's previous message."""
        if not lang:
            lang = 'en'
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

    @commands.command()
    async def apod(self, ctx, *, date='today'):
        """Astronomy picture of the day. Date format should be mm-dd-yyyy, mm/dd/yyyy."""
        try:
            date = date_strptime(date)
        except ValueError:
            await ctx.send(f"{red_tick} Error converting date. Please make sure you're using a supported format.")
            return
        picture = await self.nasa_api.apod.get(date)
        title = picture.title
        explanation = picture.explanation
        site_url = picture.html_url
        img_url = picture.hdurl
        embed = discord.Embed(title=title, description=explanation, url=site_url, color=Settings.embed_color).set_image(url=img_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
