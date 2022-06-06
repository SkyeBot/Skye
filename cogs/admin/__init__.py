import discord

from .admin import Admin

from .jinkies import Yoink

from core.bot import SkyeBot

class admin(Admin, Yoink):
    """Admin Cog"""

async def setup(bot: SkyeBot):
    await bot.add_cog(admin(bot))