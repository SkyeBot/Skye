import discord
from discord.ext import commands

from core.bot import SkyeBot

from .antiraid import antiraid

class Antiraid(antiraid):
    """All Antiraid things"""


async def setup(bot: SkyeBot):
    await bot.add_cog(Antiraid(bot))