from typing import Union
import discord
from discord.ext import commands

from discord import app_commands

from core.bot import SkyeBot

import randfacts


class fun(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot
        
    @app_commands.command(description="Get a random fact")
    async def facts(self,interaction: discord.Interaction):
        loop = self.bot.loop

        ret = await loop.run_in_executor(None, randfacts.get_fact)

        embed = discord.Embed(title="Random Fact Generator!", description=f"**{ret}**")
        embed.set_footer(text=f"Requested By {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
