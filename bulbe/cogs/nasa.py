import aiohttp
import aionasa
import discord
from aionasa.utils import date_strptime
from auth import NASA_API_KEY
from discord.ext import commands, tasks

from bulbe.base import Cog
from bulbe.settings import Settings
from utils.constants import red_tick


class NASA(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.apod = aionasa.APOD(NASA_API_KEY, session=self.session)
        # self.insight = aionasa.InSight(NASA_API_KEY, session=self.session)
        # self.epic = aionasa.EPIC(NASA_API_KEY, session=self.session)
        # self.neows = aionasa.NeoWs(NASA_API_KEY, session=self.session)
        # self.exoplanet = aionasa.Exoplanet(NASA_API_KEY, session=self.session)

        self.last_apod_date = None
        self.running = False

    async def setup(self):
        query = r"SELECT data FROM feed_dispatch WHERE name = 'last_apod_date';"
        self.last_apod_date = await self.bot.db.conn.fetch_val(query)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.running:
            self.apod_feed.start()
            self.running = True

    @commands.command()
    async def apod(self, ctx, *, date="today"):
        """Astronomy picture of the day. Date format should be mm-dd-yyyy, mm/dd/yyyy."""
        try:
            date = date_strptime(date)
        except ValueError:
            await ctx.send(
                f"{red_tick} Error converting date. Please make sure you're using a supported format."
            )
            return
        picture = await self.apod.get(date)
        title = picture.title
        explanation = picture.explanation
        site_url = picture.html_url
        img_url = picture.hdurl
        embed = discord.Embed(
            title=title,
            description=explanation,
            url=site_url,
            color=Settings.embed_color,
        ).set_image(url=img_url)
        await ctx.send(embed=embed)

    @tasks.loop(minutes=1)
    async def apod_feed(self):
        pic = await self.apod.get()
        date = pic.date
        if f"{date.year},{date.month},{date.day}" != self.last_apod_date:
            await self.update_last_apod_date(date)
            await self.dispatch_apod(pic)

    async def dispatch_apod(self, picture):
        content = "<@&771796371724173333> New Astronomy Picture of the Day!"
        title = picture.title
        explanation = picture.explanation
        site_url = picture.html_url
        img_url = picture.hdurl
        embed = discord.Embed(
            title=title,
            description=explanation,
            url=site_url,
            color=Settings.embed_color,
        ).set_image(url=img_url)
        await self.bot.get_channel(827644536263671858).send(content, embed=embed)

    async def update_last_apod_date(self, date):
        self.last_apod_date = f"{date.year},{date.month},{date.day}"
        query = r"UPDATE feed_dispatch SET data = :d WHERE name = 'last_apod_date';"
        await self.bot.db.conn.execute(query, {"d": self.last_apod_date})


def setup(bot):
    bot.add_cog(NASA(bot))
