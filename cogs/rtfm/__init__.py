import discord
from discord.ext import commands

from core.bot import SkyeBot

from .rtfm import Docs

class rtfm(Docs):
    """RTFM cog"""

async def setup(bot):
   await bot.add_cog(rtfm(bot))