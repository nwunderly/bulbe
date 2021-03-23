import re
import datetime
import discord
from discord.ext import commands
from aionasa.utils import date_strptime


class FetchedUser(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.isdigit():
            raise commands.BadArgument('Not a valid user ID.')
        try:
            return await ctx.bot.fetch_user(argument)
        except discord.NotFound:
            raise commands.BadArgument('User not found.') from None
        except discord.HTTPException:
            raise commands.BadArgument('An error occurred while fetching the user.') from None


class GlobalChannel(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return await commands.TextChannelConverter().convert(ctx, argument)
        except commands.BadArgument:
            # Not found... so fall back to ID + global lookup
            try:
                channel_id = int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f'Could not find a channel by ID {argument!r}.')
            else:
                channel = ctx.bot.get_channel(channel_id)
                if channel is None:
                    raise commands.BadArgument(f'Could not find a channel by ID {argument!r}.')
                return channel


class OptionFlag(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.startswith('--'):
            raise commands.BadArgument()
        return argument[2:]


class Language(commands.Converter):
    async def convert(self, ctx, argument):
        argument = argument.lower()
        client = ctx.cog.translate_api

        result = await client.convert_lang(argument)
        if result:
            return result

        raise commands.BadArgument("Could not convert to a supported language.")


class Command(commands.Converter):
    async def convert(self, ctx, argument):
        command = ctx.bot.get_command(argument)
        if command:
            return command
        else:
            raise commands.BadArgument("A command with this name could not be found.")


class Module(commands.Converter):
    async def convert(self, ctx, argument):
        cog = ctx.bot.get_cog(argument)
        if cog:
            return cog
        else:
            raise commands.BadArgument("A module with this name could not be found.")


duration_pattern = re.compile(r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?")


class Duration(commands.Converter):
    async def convert(self, ctx, argument):
        match = duration_pattern.match(argument)

        if not match or match.group(0) == "":
            raise commands.BadArgument("Invalid duration.")

        try:
            print("CONVERTING TO HR MIN SEC")
            h = int(match.group(1) or 0)
            m = int(match.group(2) or 0)
            s = int(match.group(3) or 0)
        except ValueError:
            raise commands.BadArgument

        return datetime.timedelta(hours=h, minutes=m, seconds=s)


