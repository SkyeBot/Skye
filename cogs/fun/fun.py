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

    @app_commands.command()
    async def osutest(self, itr: discord.Interaction, username: str):
        user = await self.bot.osu.get_user(username)
        embed = discord.Embed(title=f"Profile for {username}", description=f"▹ **Bancho Rank**: #{user.global_rank} ({user.country}#{user.country_rank})\n▹ **Join Date**: {user.joined_at}\n▹ **PP**: {user.pp} **Acc**: {user.accuracy:.2f}%\n▹ **Ranks**: {user.ranks}\n▹ **Profile Order**: \n** ​ ​ ​ ​ ​ ​ ​ ​  - {user.profile_order}**")
        embed.set_thumbnail(url=user.avatar_url)
        await itr.response.send_message(embed=embed)