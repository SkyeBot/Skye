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
            title=f"*{member} was banned!*", description=f"Reason: {reason} \nMember banned at <t:{utc_time}:F>",
            color = self.bot.color
        )
        embed.set_author(name=f"{member}", icon_url=member.display_avatar.url)
        await member.send(f"``You Have Been Banned From {interaction.guild.name} for \n {reason}``")
        await member.ban(reason=reason)
        await interaction.response.send_message(embed=embed)


    
    @app_commands.command(name="unban", description="Unbans a user")
    @app_commands.describe(member="Takes in a Full Member Name or id")
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
            
            
            embed = discord.Embed(title=f"Succesfully unbanned: {user}!", description=f"Responsible moderator: {interaction.user}\nMember unbanned at <t:{utc_time}:F>",color =self.bot.color)
            await interaction.response.send_message(embed=embed)
        except discord.errors.NotFound as e:
            print(e)
            embed = discord.Embed(title="Error!", description="No user found! Please try this cmd again but with their full username including their discriminator or try their ID with this.", color=self.bot.error_color)
            return await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hackban", description="A ban cmd that can ban users outside guild")
    async def hackban_slash(self, interaction: discord.Interaction, member: str, reason: str = None):
        guild = interaction.guild

        if reason == None:
            reason = "No Reason Specified"

        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())
        ctx = await commands.Context.from_interaction(interaction)
        try:
            user = await commands.converter.UserConverter().convert(ctx, member)
        except Exception as e:
            print(e)
        
        embed = discord.Embed(
            title=f"*{user} was hack-banned!*", description=f"**Reason: {reason} \n Member banned at <t:{utc_time}:F>**",
            color = self.bot.color,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_author(name=user, icon_url=user.display_avatar.url)



        await guild.ban(discord.Object(id=user.id))
        await ctx.send(embed=embed)