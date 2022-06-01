import discord
from discord.ext import commands

# Local Imports
from core.bot import SkyeBot

from .info import Misc


class Misc(Misc):
    pass


async def setup(bot: SkyeBot):
    await bot.add_cog(Misc(bot))