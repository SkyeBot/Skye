import discord
from discord.ext import commands
discord.utils.setup_logging
from .osu_cog import osu

class Osu(osu):
    """All osu commands"""


async def setup(bot):
    await bot.add_cog(Osu(bot))


