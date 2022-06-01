import discord

from discord.ext import commands

from .owner import owner

class Owner(owner):
    """Owner Command Cogs"""

async def setup(bot):
    await bot.add_cog(Owner(bot))