from typing import Optional
import discord
from discord.ext import commands
from discord import app_commands
from utils.base_cog import base_cog
import re
from utils import default, osu_errors

class osu(base_cog):
    osu = app_commands.Group(name="osu", description="All osu commands")
    set = app_commands.Group(name="set", description="allows you to set various things for osu", parent=osu)

    @osu.command()
    async def user(self, interaction: discord.Interaction, username: Optional[str]):
        try:
            user_query = await self.bot.pool.fetchrow("SELECT osu_username FROM osu_user WHERE user_id = $1", interaction.user.id) 
        
            
            if user_query is None and username is None:
                user = await self.bot.osu.fetch_user(interaction.user.display_name)
            elif user_query is not None and username is None:
                user = await self.bot.osu.fetch_user(user_query.get("osu_username"))
            else:
                user = await self.bot.osu.fetch_user(username)

            
            self.bot.logger.info(user.username)
            self.bot.logger.info(user.avatar_url)

            embed = discord.Embed(description=f"**{user.country_emoji} | Profile for [{user.username}](https://osu.ppy.sh/users/{user.id})**\n\n▹ **Bancho Rank**: #{user.global_rank} ({user.country_code}#{user.country_rank})\n▹ **Join Date**: {user.joined_at}\n▹ **PP**: {user.pp} **Acc**: {user.accuracy}%\n▹ **Ranks**: {user.ranks}\n▹ **Profile Order**: \n** ​ ​ ​ ​ ​ ​ ​ ​  - {user.profile_order}**")
            embed.set_thumbnail(url=user.avatar_url)
            await interaction.response.send_message(embed=embed)
            
        except osu_errors.NoUserFound:
            await interaction.response.send_message("No User Was Found Sadly!")

    @set.command()
    async def user(self, interaction: discord.Interaction, username: str): 
        """Allows you to set your username""" 
        try:
            query = """
                INSERT INTO osu_user (osu_username, user_id) VALUES($1, $2)
                ON CONFLICT(user_id) DO 
                UPDATE SET osu_username = excluded.osu_username

            """
        
            await self.bot.pool.execute(query, username, interaction.user.id)

            await interaction.response.send_message(f"Sucessfullly set your osu username to: {username}")
        except Exception as e:
            return await interaction.response.send_message(f"Oh No! an error occured!\n\nError Class: **{e.__class__.__name__}**\n{default.traceback_maker(err=e)}If you're a coder and you think this is a fatal error, DM Sawsha#0598!", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        beatmap_regex =  re.compile(r"http[s]?://osu\.ppy\.sh/b/[0-9]{1,12}")

        try:
            if re.match(beatmap_regex, str(message.content)):
                numbers = re.findall(r'\d+', message.content)
                numbers = ''.join(x for x in numbers)
                beatmap = await self.bot.osu.get_beatmap(numbers)
                await message.channel.send(beatmap.artist)
        except Exception as e:
            print(e)

    