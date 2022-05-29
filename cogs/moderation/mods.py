import calendar
from typing import List
import datetime
from typing import Optional
import discord
from discord.ext import commands
from discord import app_commands

# Local Imports
from core.bot import SkyeBot
from utils import default


class Mods(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    @app_commands.command(name="ban", description="Bans a specified user")
    async def ban_slash(self, interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
        if reason is None:
            reason = "No Reason Provided"

        if member == self.bot.user:
            await interaction.response.send_message("``You Cannot Ban Me!``")
        
        if member == interaction.user:
            await interaction.response.send_message("``You Cannot Ban Yourself!``")
        

        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())

        embed = discord.Embed(
            title=f"*{member} was banned!*", description=f"Reason: {reason} \nMember banned at <t:{utc_time}:F>"
        )
        embed.set_author(name=f"{member}", icon_url=member.display_avatar.url)
        await member.send(f"``You Have Been Banned From {interaction.guild.name} for \n {reason}``")
        await member.ban(reason=reason)
        await interaction.response.send_message(embed=embed)


    
    @app_commands.command(name="unban", description="Unbans a user")
    async def unban_slash(self, interaction: discord.Interaction, member:str):
        ctx = await commands.Context.from_interaction(interaction)
        try:
            user = await commands.converter.UserConverter().convert(ctx, member)
        except Exception as e:
            print(e)
        
        try:
            await interaction.guild.unban(user, reason=f"Responsible moderator: {interaction.user}")
            date = datetime.datetime.utcnow()
            utc_time = calendar.timegm(date.utctimetuple())
            
            
            embed = discord.Embed(title=f"Succesfully unbanned: {user}!", description=f"Responsible moderator: {interaction.user}\nMember unbanned at <t:{utc_time}:F>")
            await interaction.response.send_message(embed=embed)
        except discord.errors.NotFound:
            return
