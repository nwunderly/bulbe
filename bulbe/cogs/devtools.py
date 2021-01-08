import discord
import aiohttp

from discord.ext import commands
from typing import Union

from utils.converters import FetchedUser
from utils.constants import red_tick
from bulbe.base import Cog


class DevTools(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @commands.command()
    async def oauth(self, ctx, bot: Union[discord.User, FetchedUser], *perms):
        """Generates an invite link for a bot with the requested perms."""
        if not bot.bot:
            await ctx.send(f"{red_tick} `{bot}` isn't a bot!")
            return
        if perms:
            p = None
            if len(perms) == 1:
                try:
                    p = discord.Permissions(int(perms[0]))
                except ValueError:
                    pass
            if not p:
                kwargs = {}
                for perm in perms:
                    kwargs[perm] = True
                try:
                    p = discord.Permissions(**kwargs)
                except TypeError as e:
                    await ctx.send(str(e))
                    return
        else:
            p = None
        link = discord.utils.oauth_url(bot.id, permissions=p)
        link = '<' + link + '>'
        await ctx.send(f"Invite link for `{bot}`:\n"+link)

    @commands.command()
    async def oauthperms(self, ctx, *perms):
        """Converts permissions integer to list of permissions, and vice-versa."""
        try:
            value = int(perms[0])
            p = discord.Permissions(value)
        except ValueError:
            p = None
            value = None
        if p:
            # int conversion worked, send list of perms
            desc = f"Permissions integer `{value}` will grant these perms: \n"
            desc += "".join([("- " + perm + "\n") for perm, val in p if val])
            return await ctx.send(desc)
        else:
            # use list of perms
            kwargs = {}
            for perm in perms:
                kwargs[perm] = True
            try:
                p = discord.Permissions(**kwargs)
            except TypeError as e:
                return await ctx.send(e)
            desc = f"These permissions will have permissions integer `{p.value}`"
            await ctx.send(desc)

    class FindIDArgs(commands.Converter):
        async def convert(self, ctx, argument):
            if argument == 'guild':
                return ctx.guild
            elif argument == 'channel':
                return ctx.channel
            elif argument == 'me':
                return ctx.author
            else:
                raise commands.BadArgument

    @commands.group(name='id')
    async def find_id(self, ctx, *, target: Union[FindIDArgs, discord.TextChannel, discord.VoiceChannel, discord.Role, discord.Member, discord.User, discord.PartialEmoji]):
        """Attempts to convert your query to a discord object and returns its id.
        Search order: Special args, TextChannel, VoiceChannel, Role, Member, User, Emoji.
        Special args: 'guild', 'channel', 'me'"""
        await ctx.send(f"`{(type(target)).__name__}` **{target.name}**:  `{target.id}`")

    @find_id.error
    async def find_id_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            await ctx.send("Could not locate a snowflake based on that query.")

    async def channel(self, ctx, *, target):
        pass

    async def role(self, ctx, *, target):
        pass

    async def member(self, ctx, *, target):
        pass

    async def user(self, ctx, *, target):
        pass

    # @commands.command(name='source', aliases=['src'])
    # async def get_source(self, ctx, name=None):
    #     if not name:
    #         await ctx.send("<https://github.com/nwunderly/RevBots>")
    #         return
    #     if name == 'help':
    #         await ctx.send(f"<https://github.com/Rapptz/discord.py/blob/master/discord/ext/commands/help.py>")
    #         return
    #     command = self.bot.get_command(name)
    #     cog = self.bot.get_cog(name)
    #     if command:
    #         obj = command.callback
    #     elif cog:
    #         obj = cog.__class__
    #     else:
    #         await ctx.send("I couldn't find a command or module with that name.")
    #         return
    #     path = inspect.getsourcefile(obj).replace('\\', '/')
    #     git_path = path[len(HOME_DIR)+1:]
    #     git_link = f"https://github.com/nwunderly/RevBots/tree/master/{git_path}"
    #     print(git_link)
    #     async with self.session.get(git_link) as response:
    #         if response.status == 404:
    #             await ctx.send("Command or module is not yet on github.")
    #             return
    #     await ctx.send(f"<{git_link}>")


def setup(bot):
    bot.add_cog(DevTools(bot))
