import discord

from .admin import Admin

from core.bot import SkyeBot

class admin(Admin):
    """Admin Cog"""

async def setup(bot: SkyeBot):
    await bot.add_cog(admin(bot))