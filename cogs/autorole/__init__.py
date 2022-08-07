import discord
from discord.ext import commands

from core.bot import SkyeBot


from .autorole import autorole

class Autorole(autorole):
    """Autorole Commands"""

async def setup(bot: SkyeBot):
    await bot.add_cog(Autorole(bot))