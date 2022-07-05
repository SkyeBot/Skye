from typing import Optional
import discord
from discord.ext import commands
from discord import app_commands
from utils.base_cog import base_cog
import re


class osu(base_cog):
    osu = app_commands.Group(name="osu", description="All osu commands")
    set = app_commands.Group(name="set", description="allows you to set various things for osu", parent=osu)

    @osu.command()
    async def user(self, interaction: discord.Interaction, username: str):
        user = await self.bot.osu.get_user(username)
        embed = discord.Embed(title=f":flag_{user.country.lower()}: Profile for {username}",description=f"▹ **Bancho Rank**: #{user.global_rank} ({user.country}#{user.country_rank})\n▹ **Join Date**: {user.joined_at}\n▹ **PP**: {user.pp} **Acc**: {user.accuracy:.2f}%\n▹ **Ranks**: {user.ranks}\n▹ **Profile Order**: \n** ​ ​ ​ ​ ​ ​ ​ ​  - {user.profile_order}**")
        embed.set_thumbnail(url=user.avatar_url)
        await interaction.response.send_message(embed=embed)

    @set.command()
    async def user(self, interaction: discord.Interaction, username: str):
        await interaction.response.send_message(f"Added {username}!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        beatmap_regex =  re.compile(r"http[s]?://osu\.ppy\.sh/b/[0-9]{1,12}")

        try:
            if re.match(beatmap_regex, str(message.content)):
                await message.channel.send("Ass")
        except Exception as e:
            print(e)