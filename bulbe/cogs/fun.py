import datetime
import typing
import aiohttp
import aionasa

from discord.ext import commands
from google.oauth2.service_account import Credentials
from google.cloud.translate_v3.services.translation_service import TranslationServiceAsyncClient
from google.cloud.translate_v3.types.translation_service import TranslateTextRequest

from utils.constants import red_tick
from utils.helpers import fetch_previous_message
from utils.converters import Language
from bulbe.base import Cog
from auth import CLOUD_CREDS_FILE, CLOUD_PROJ_ID, NASA_API_KEY



class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

        credentials = Credentials.from_service_account_file(CLOUD_CREDS_FILE)
        self.translate_client = TranslationServiceAsyncClient(credentials=credentials)
        self.lang_cache = {}

        self.apod = aionasa.APOD(NASA_API_KEY, session=self.session)
        self.insight = aionasa.InSight(NASA_API_KEY, session=self.session)
        self.epic = aionasa.EPIC(NASA_API_KEY, session=self.session)
        self.neows = aionasa.NeoWs(NASA_API_KEY, session=self.session)
        self.exoplanet = aionasa.Exoplanet(NASA_API_KEY, session=self.session)

    async def cleanup(self):
        await self.session.close()

    @commands.command(name='translate', aliases=['t'])
    async def _translate(self, ctx, lang: typing.Optional[Language] = 'en', *, text: commands.clean_content = None):
        """Translates a message into a language of your choice.
        Defaults to English. If no text to translate is specified, uses the current channel's previous message."""
        if not lang:
            lang = 'en'
        if not text:
            prev = await fetch_previous_message(ctx.message)
            text = prev.content
        result = self.translate_client.translate_text(
            request={
                "parent": f"projects/{CLOUD_PROJ_ID}/locations/global",
                "contents": [text],
                "mime_type": "text/plain",  # mime types: text/plain, text/html
                "source_language_code": "en-US",
                "target_language_code": "fr",
            }
        )
        if isinstance(result, dict):
            text = result['translatedText'].replace('&#39;', '\'')
            await ctx.send(f"(from {result['detectedSourceLanguage']}) {text}")

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
