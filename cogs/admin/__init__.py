import discord


from .jinkies import Yoink

from core.bot import SkyeBot

class admin(Yoink):
    """Admin Cog"""

async def setup(bot: SkyeBot):
    await bot.add_cog(admin(bot))