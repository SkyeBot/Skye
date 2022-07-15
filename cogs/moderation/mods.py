import calendar
from contextlib import redirect_stdout
import io
<<<<<<< HEAD
import re
=======
>>>>>>> c57e8ae748fd320ceaefb4a0c756110dbe396dc1
import textwrap
import traceback
from typing import Any, List, Optional
import datetime
import discord
from discord.ext import commands
from discord import app_commands

# Local Imports
from core.bot import SkyeBot
from utils import default

class Mods(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot
        self._last_result: Optional[Any] = None

    @app_commands.command(name="ban", description="Bans a specified user")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(member="The member you choose ban")
    @app_commands.describe(reason="The reason for banning member")
<<<<<<< HEAD
    async def ban_slash(self, interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = "No Reason Provided"):
=======
    async def ban_slash(self, interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
        if reason is None:
            reason = "No Reason Provided"
>>>>>>> c57e8ae748fd320ceaefb4a0c756110dbe396dc1
        
        if member == self.bot.user:
            return await interaction.response.send_message("``You Cannot Ban Me!``")
        
        if member == interaction.user:
            return await interaction.response.send_message("``You Cannot Ban Yourself!``")
        
<<<<<<< HEAD
        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())

        if interaction.user.top_role <= member.top_role or interaction.guild.me.top_role <= member.top_role:
=======

        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())

        if interaction.user.top_role <= member.top_role:
>>>>>>> c57e8ae748fd320ceaefb4a0c756110dbe396dc1
            return await interaction.response.send_message("``You cannot ban someone with a role higher or equal to yourself!``")




        embed = discord.Embed(
            title=f"*{member} was banned!*", description=f"Reason: {reason} \nMember banned at <t:{utc_time}:F>",
            color = self.bot.color
        )
        embed.set_author(name=f"{member}", icon_url=member.display_avatar.url)
        await member.send(f"``You Have Been Banned From {interaction.guild.name} for \n {reason}``")
        await member.ban(reason=reason)
        await interaction.response.send_message(embed=embed)

<<<<<<< HEAD
    async def tags_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        bans = [entry async for entry in interaction.guild.bans(limit=2000)]
        return [
            app_commands.Choice(name=f"{n.user}", value=f"{n.user.id}")
            for n in bans
        ]
        
=======

>>>>>>> c57e8ae748fd320ceaefb4a0c756110dbe396dc1
    
    @app_commands.command(name="unban", description="Unbans a user")
    @app_commands.describe(member="Takes in a Full Member Name or id")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(member="The member you choose unban")
<<<<<<< HEAD
    @app_commands.autocomplete(member=tags_autocomplete)
=======
>>>>>>> c57e8ae748fd320ceaefb4a0c756110dbe396dc1
    async def unban_slash(self, interaction: discord.Interaction, member:str):
        ctx = await commands.Context.from_interaction(interaction)
        try:    
            user = await commands.converter.UserConverter().convert(ctx, member)
        except Exception as e:
            embed = discord.Embed(title="Error!", description="No user found! Please try this cmd again but with their full username including their discriminator or try their ID with this.", color=self.bot.error_color)
            return await interaction.response.send_message(embed=embed)
<<<<<<< HEAD


        await interaction.guild.unban(user, reason=f"Responsible moderator: {interaction.user}")
        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())
        
        
        embed = discord.Embed(title=f"Succesfully unbanned: {user}!", description=f"Responsible moderator: {interaction.user}\nMember unbanned at <t:{utc_time}:F>",color =self.bot.color)
        await interaction.response.send_message(embed=embed)
=======
        
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
>>>>>>> c57e8ae748fd320ceaefb4a0c756110dbe396dc1

    @app_commands.command(name="hackban", description="A ban cmd that can ban users outside guild")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(member="The member you choose hackban")
    @app_commands.describe(reason="The reason for banning member")
    async def hackban_slash(self, interaction: discord.Interaction, member: str, reason: str = None):
        guild = interaction.guild

<<<<<<< HEAD
        reason = reason or "No Reason Specified"
=======
        if reason == None:
            reason = "No Reason Specified"
>>>>>>> c57e8ae748fd320ceaefb4a0c756110dbe396dc1

        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())
        ctx = await commands.Context.from_interaction(interaction)
<<<<<<< HEAD

        mention_regex = re.compile(r"<@!?([0-9]+)>")
        if mention_regex.match(member):
            numbers = re.findall(r'\d+', member)
            member = ''.join(x for x in numbers)


        try:
            user = await commands.converter.UserConverter().convert(ctx, member)
        except commands.UserNotFound:
            return await interaction.response.send_message("User Was Not Found!")


        embed = discord.Embed(
            title=f"*{user} was hack-banned!*", description=f"**Reason: {reason} \nMember banned at <t:{utc_time}:F>**",
=======
        try:
            user = await commands.converter.UserConverter().convert(ctx, member)
        except Exception as e:
            print(e)

        
        if interaction.user.top_role <= member.top_role:
            return await interaction.response.send_message("``You cannot ban someone with a role higher or equal to yourself!``")

        embed = discord.Embed(
            title=f"*{user} was hack-banned!*", description=f"**Reason: {reason} \n Member banned at <t:{utc_time}:F>**",
>>>>>>> c57e8ae748fd320ceaefb4a0c756110dbe396dc1
            color = self.bot.color,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_author(name=user, icon_url=user.display_avatar.url)
<<<<<<< HEAD
        

        
        try:
            await guild.ban(discord.Object(id=user.id))
        except discord.Forbidden:
            return await interaction.response.send_message("I cannot ban the user due a missing permission on my end!")

        
        
        await interaction.response.send_message(embed=embed)
=======


        await guild.ban(discord.Object(id=user.id))
        await ctx.send(embed=embed)
>>>>>>> c57e8ae748fd320ceaefb4a0c756110dbe396dc1
