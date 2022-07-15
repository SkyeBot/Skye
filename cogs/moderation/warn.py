import discord

from discord.ext import commands

from core.bot import SkyeBot

from discord import app_commands

class Warns(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    @app_commands.command(name="warn")
    async def warn(self, interaction: discord.Interaction):
<<<<<<< HEAD
        """Doesn't work as of right now"""

=======
>>>>>>> c57e8ae748fd320ceaefb4a0c756110dbe396dc1
        pass
        