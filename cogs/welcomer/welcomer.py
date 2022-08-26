import datetime
from typing import Optional, Union
import discord
from discord.ext import commands
from utils import default
from core.bot import SkyeBot
import string
from utils.context import Context

from discord import app_commands

class welcomer(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot


    welcomer = app_commands.Group(name="welcomer", description="All commands for setting up welcoming",default_permissions=discord.Permissions(administrator=True))
    

        
    @welcomer.command()
    async def enable(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel], message: Optional[str]):
        """Enables Welcomer with optional message"""
        message = message or "Welcome $user to $guild!"
        channel = channel or interaction.channel
        exists =  await self.bot.pool.fetchrow("SELECT channel_id FROM WELCOME_CONFIG WHERE guild_id = $1", interaction.guild.id)

        if exists is None:
            await self.bot.pool.execute('INSERT INTO welcome_config(channel_id, message, guild_id) VALUES ($1, $2, $3)',channel.id, message,interaction.guild.id)
            new_text = string.Template(message).safe_substitute(
                user=interaction.user.mention,
                    guild=interaction.guild
                )

            return await interaction.response.send_message(f"Welcome Channel: {channel.mention}\n\nWelcome Message Is Now Set To: **{new_text}**", ephemeral=True, allowed_mentions=discord.AllowedMentions.none())
        else:
            await self.bot.pool.execute('UPDATE welcome_config SET channel_id = $1, message = $2 WHERE guild_id = $3',  channel.id, message, interaction.guild.id)
            new_text = string.Template(message).safe_substitute(
                user=interaction.user.mention,
                    guild=interaction.guild
                )

            return await interaction.response.send_message(f"Welcome Channel: {channel.mention}\n\nWelcome Message Is Now Set To: **{new_text}**", ephemeral=True, allowed_mentions=discord.AllowedMentions.none())

    @welcomer.command()
    async def disable(self, interaction: discord.Interaction):
        """Disables welcomer for the guilld"""

        try: 
            exists =  await self.bot.pool.fetchrow("SELECT channel_id FROM WELCOME_CONFIG WHERE guild_id = $1", interaction.guild.id)  
            if exists is None:
                return await interaction.response.send_message("Welcomer was not enabled in the first place!",ephermal=True)

            await self.bot.pool.execute("DELETE FROM welcome_config WHERE guild_id = $1", interaction.guild.id)
            await interaction.response.send_message("Succesfully disabled welcomer!")

        except Exception as e:
            return await interaction.response.send_message(f"Oh No! an error occured!\n\nError Class: **{e.__class__.__name__}**\n{default.traceback_maker(err=e)}If you're a coder and you think this is a fatal error, DM Sawsha#0598!", ephemeral=True)




    @commands.Cog.listener()
    async def on_member_join(self,member:discord.Member):
        try: 
            exists = await self.bot.pool.fetchrow("SELECT * FROM WELCOME_CONFIG WHERE guild_id = $1", member.guild.id)
            channel = self.bot.get_channel(exists.get("channel_id"))

            new_text = string.Template(exists.get("message")).safe_substitute(
                user=member.mention,
                guild=member.guild
            )
        

            embed = discord.Embed(title=f"Welcome {member} to {member.guild}!", description=f"{new_text}")

            embed.timestamp = datetime.datetime.utcnow()
            embed.set_thumbnail(url=f"{member.avatar}")
            
            await channel.send(embed=embed)    
        except Exception as e:
            print(e)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        try: 
            exists = await self.bot.pool.fetchrow("SELECT * FROM WELCOME_CONFIG WHERE guild_id = $1", member.guild.id)
            channel = self.bot.get_channel(exists.get("channel_id"))
            show_roles = ", ".join(
                [f"<@&{x.id}>" for x in sorted(member.roles, key=lambda x: x.position, reverse=True) if
                    x.id != member.guild.default_role.id]
            ) if len(member.roles) > 1 else "Default Role"

            embed = discord.Embed(title=f"Member: {member} left the server! this server is now at {len(member.guild.members)} Members")
            embed.add_field(name="Account created", value=default.date(member.created_at, ago=True), inline=False)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_thumbnail(url=f"{member.avatar}")

            await channel.send(embed=embed)
        except Exception as e:
            print(e)
    
