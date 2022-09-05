import datetime
from typing import Optional, Union
import discord
from discord.ext import commands
from utils import default
from core.bot import SkyeBot
import string
from utils.context import Context
import asyncpg
from discord import app_commands
from .view import MyView


class welcomer(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot


    welcomer = app_commands.Group(name="welcomer", description="All commands for setting up welcoming",default_permissions=discord.Permissions(administrator=True))
    
    @welcomer.command()
    async def config(self, interaction: discord.Interaction):
        """Enables Welcomer with optional message"""
        embed = discord.Embed(title="Welcome Config")
        embed.add_field(name="Custom Image", value="Allows for an custom image to be sent along side the main embed")
        embed.add_field(name="Custom message", value="Allows for a custom message to be sent\nVariables: ``$user, $guild``")
        embed.add_field(name="Custom Channel", value="Allows for a custom channel through an ID or name")


        await interaction.response.send_message(content="Warning: The following buttons, modals, etc are not persistent, if they stop working at any time, re-run the command!",embed=embed, view=MyView(interaction.user.id, interaction.channel.id, interaction))

    @commands.Cog.listener()
    async def on_member_join(self,member:discord.Member):
        try: 
            exists = await self.bot.pool.fetchrow("SELECT * FROM WELCOMER_CONFIG WHERE guild_id = $1", member.guild.id)
            channel = self.bot.get_channel(exists['channel_id'])

            new_text = string.Template(exists['message']).safe_substitute(
                user=member.mention,
                guild=member.guild
            )
        

            embed = discord.Embed(description=f"**{new_text}**")
            embed.set_author(name=member, icon_url=member.display_avatar.url)
            embed.set_image(url=exists['image'])
            embed.timestamp = datetime.datetime.utcnow()
            
            await channel.send(embed=embed)    
        except Exception as e:
            self.bot.logger.info(e)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        try: 
            exists: dict = await self.bot.pool.fetchrow("SELECT * FROM welcomer_config WHERE guild_id = $1", member.guild.id)
            channel = self.bot.get_channel(exists.get("channel_id"))

            embed = discord.Embed(description=f"**{member} left the server! this server is now at {len(member.guild.members)} Members :(**")
            embed.set_author(name=member, icon_url=member.display_avatar.url)
            embed.set_image(url=exists['image']) 
            embed.timestamp = datetime.datetime.utcnow()

            await channel.send(embed=embed)
        except Exception as e:
            self.bot.logger.error(e)
    
