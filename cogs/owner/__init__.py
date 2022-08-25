import discord

from discord.ext import commands

from .owner import owner
from .sql import SQLCommands

class Owner(owner, SQLCommands):
    """Owner Command Cogs"""

async def setup(bot):
    await bot.add_cog(Owner(bot))