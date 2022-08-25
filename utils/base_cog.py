from discord.ext import commands

from core.bot import SkyeBot


class base_cog(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot
