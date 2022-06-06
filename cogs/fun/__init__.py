import discord
from discord.ext import commands

from core.bot import SkyeBot

from .fun import fun

class Fun(fun):
    """Fun Cog"""

async def setup(bot: SkyeBot):
    await bot.add_cog(Fun(bot))