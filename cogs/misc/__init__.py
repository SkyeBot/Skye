import discord
from discord.ext import commands

# Local Imports
from core.bot import SkyeBot

from .info import Misc
from .bot_info import bot_info


class Misc(Misc, bot_info):
    pass


async def setup(bot: SkyeBot):
    await bot.add_cog(Misc(bot))