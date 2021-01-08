import datetime

import aiohttp
from discord.ext import commands

from auth import NASA_API_KEY
from utils.constants import red_tick
from bulbe.base import Cog


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.translator = None
        self.lang_cache = dict()
        self.session = aiohttp.ClientSession()

    # @commands.command(name='translate', aliases=['t'])
    # async def _translate(self, ctx, lang: typing.Optional[Language] = 'en', *, text: commands.clean_content = None):
    #     """Translates a message into a language of your choice.
    #     Defaults to English. If no text to translate is specified, uses the current channel's previous message."""
    #     if not lang:
    #         lang = 'en'
    #     if not text:
    #         prev = await fetch_previous_message(ctx.message)
    #         text = prev.content
    #     client = self.translator
    #     result = client.translate(text, target_language=lang)
    #     if isinstance(result, dict):
    #         text = result['translatedText'].replace('&#39;', '\'')
    #         await ctx.send(f"(from {result['detectedSourceLanguage']}) {text}")

    @commands.command()
    async def lmgtfy(self, ctx, *, search):
        """Let me google that for you."""
        q = search.replace(" ", "+").replace("\n", "+")
        await ctx.send(f"https://lmgtfy.com/?q={q}")

    @commands.command()
    async def apod(self, ctx, *, date=None):
        """Astronomy picture of the day. Date format should be mm-dd-yyyy, mm/dd/yyyy."""
        if not date or (date and date.lower() == 'today'):
            date = datetime.date.today()
        elif date.lower() == 'yesterday':
            date = datetime.date.today() - datetime.timedelta(days=1)
        else:
            try:
                mmddyy = date.split('-')
                if len(mmddyy) == 1:
                    mmddyy = mmddyy[0].split('/')
                if len(mmddyy) == 1:
                    mmddyy = mmddyy[0].split(' ')
                if len(mmddyy) == 2:
                    mm, dd = [int(i) for i in mmddyy]
                    yy = 2020
                elif len(mmddyy) == 3:
                    mm, dd, yy = [int(i) for i in mmddyy]
                else:
                    raise ValueError
                date = datetime.date(year=yy, month=mm, day=dd)
                if not datetime.date(year=2015, month=1, day=1) <= date <= datetime.date.today():
                    raise ValueError
            except ValueError:
                await ctx.send(f"{red_tick} Error converting date. Please make sure you're using a supported format.")
                return
        api_formatted_date = f"{date.year}-{date.month}-{date.day}"
        site_formatted_date = f"{str(date.year)[2:]}{date.month:02d}{date.day:02d}"
        api_url = f"https://api.nasa.gov/planetary/apod?date={api_formatted_date}&api_key={NASA_API_KEY}"
        site_url = f"https://apod.nasa.gov/apod/ap{site_formatted_date}.html"
        response = await self.session.get(api_url)
        data = await response.json()
        title = f"{data['title']} ({data['date']})"
        await ctx.send(embed=self.bot.Embed(title=title, description=data['explanation'], url=site_url).set_image(url=data['hdurl']))


def setup(bot):
    bot.add_cog(Fun(bot))
