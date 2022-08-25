from typing import Optional
import discord

from discord.ext import commands

from discord import app_commands

from core.bot import SkyeBot
from utils import default



class autorole(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot
    

    
    group = app_commands.Group(name="autorole", description="Autorole settings")
    
    @commands.Cog.listener()
    async def on_member_join(self,member: discord.Member):
        try:
            role_id =  await self.bot.pool.fetchval("SELECT role_id FROM AUTOROLE WHERE guild_id = $1", member.guild.id)

            role = member.guild.get_role(role_id)
            
            await member.add_roles(role)
        except:
            pass




    @group.command(name="enable")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(role="The role to be choosen")
    async def _enable(self, interaction: discord.Interaction, role: discord.Role):
        """Enables autorole for guild"""
        try: 
            query = """
                INSERT INTO autorole (guild_id, role_id) VALUES($1, $2)
                ON CONFLICT(guild_id) DO 
                UPDATE SET role_id = excluded.role_id

            """

            await self.bot.pool.execute(query, interaction.guild.id, role.id)

            embed = discord.Embed(description=f"Autorole is now enabled/updated\n\nRole: {role.mention}", color = discord.Color(0x32ff00))
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        except (Exception) as e:
            return await interaction.response.send_message(f"Oh No! an error occured!\n\nError Class: **{e.__class__.__name__}**\n{default.traceback_maker(err=e)}If you're a coder and you think this is a fatal error, DM Sawsha#0598!", ephemeral=True)

    @group.command(name="disable")
    @app_commands.default_permissions(administrator=True)
    async def _disable(self, interaction: discord.Interaction):
        """Disables autorole for guild"""

        exists =  await self.bot.pool.fetchrow("SELECT autorole FROM AUTOROLE WHERE guild_id = $1", interaction.guild.id)
        
        if exists is not None:
            await self.bot.pool.execute("DELETE FROM autorole WHERE guild_id = $1", interaction.guild.id)
            await interaction.response.send_message("Autorole sucessfully disabled", ephemeral=True)
        else:
            return await interaction.response.send_message("This server's autorole is not enabled!", ephemeral=True)


        
