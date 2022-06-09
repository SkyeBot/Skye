from code import interact
from typing import Optional
import discord

from discord.ext import commands

from core.bot import SkyeBot

from discord import app_commands


class Mute(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    mute = app_commands.Group(name="mute_config", description="Mute Commands", default_permissions=discord.Permissions(administrator=True))

    @mute.command(name="set", description="Set A Mute Role")
    async def set_mute(self, interaction: discord.Interaction, role: discord.Role):
        exists = await self.bot.pool.fetchrow("SELECT role_id FROM MUTE_CONFIG WHERE guild_id = $1", interaction   .guild.id)
    
        try:
            if role is None:
                await interaction.response.send_message("Please provide a channel for me for logging!")
            
            if (exists == None):
                await self.bot.pool.execute('INSERT INTO mute_config(role_id, guild_id) VALUES ($1, $2)',role.id, interaction.guild.id)
                em = discord.Embed(title="", color=discord.Color(0x32ff00))
                em.add_field(name="Mute Config Setup", value=f"Mute Role: {role.mention}")
                await interaction.response.send_message(embed=em)
            else:
                await self.bot.pool.execute('UPDATE mute_config SET role_id = $1 WHERE guild_id = $2',  role.id, interaction.guild.id)
                em = discord.Embed(title="", color=discord.Color(0x32ff00))
                em.add_field(name="Mute Config Updated", value=f"New Mute Role: {role.mention}")
                await interaction.response.send_message(embed=em)
        except (Exception) as e:
            await interaction.response.send_message(e)

    @app_commands.command(name="mute", description="Mutes A User")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute_slash(self, interaction: discord.Interaction, member: discord.Member, reason: Optional[str]=None):
        try:

            reason = reason or "No Reason Specified"

            role_query = await self.bot.pool.fetchval("SELECT role_id FROM MUTE_CONFIG WHERE guild_id = $1", interaction.guild.id)
            muted_role = interaction.guild.get_role(role_query)

            if muted_role is None:
                muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
                
                if not muted_role:
                    muted_role = await interaction.guild.create_role(name="Muted")

            for channel in interaction.guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False, read_message_history=True, read_messages=True, create_public_threads=False, send_messages_in_threads=False)

            
            embed =  discord.Embed(title="❌ Muted", description=f"{interaction.user.mention} Muted {member.mention}", colour=discord.Colour.light_gray())
            embed.add_field(name="reason:", value=reason, inline=False)
    
            if member == interaction.user:
                await interaction.response.send_message('you cannot mute yourself!')

            await interaction.response.send_message(embed=embed)
            await member.add_roles(muted_role, reason=reason)
            await member.send(f'You have been muted from {interaction.guild.name}! \n Reason: {reason}')    

        except Exception as e:
            self.bot.logger.error(e)

    @app_commands.command(name="unmute", description="Unmutes A User")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute_slash(self, interaction: discord.Interaction, member: discord.Member):
        try:
            role_query = await self.bot.pool.fetchval("SELECT role_id FROM MUTE_CONFIG WHERE guild_id = $1", interaction.guild.id)
            muted_role = interaction.guild.get_role(role_query)

            if muted_role is None:
                muted_role = discord.utils.get(interaction.guild.roles, name="Muted")

                if not muted_role:
                    muted_role = await interaction.guild.create_role(name="Muted")

                    for channel in interaction.guild.channels:
                        await channel.set_permissions(muted_role, speak=False, send_messages=False, read_message_history=True, read_messages=True,  create_public_threads=False, send_messages_in_threads=False)
            
    
            await member.remove_roles(muted_role)
            embed = discord.Embed(title="✅ Unmuted!", description=f"Unmuted {member.mention}",colour=discord.Colour.light_gray())
            await interaction.response.send_message(embed=embed)
            await member.send(f"you have unmuted from: {interaction.guild.name}")        



        except Exception as e:
            self.bot.logger.error(e)
                