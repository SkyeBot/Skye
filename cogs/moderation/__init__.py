import discord

from discord.ext import commands


# Local Imports
from core.bot import SkyeBot

from .mods import Mods


class Moderation(Mods):
    """Moderation Cog"""


async def setup(bot: SkyeBot):
    await bot.add_cog(Moderation(bot))