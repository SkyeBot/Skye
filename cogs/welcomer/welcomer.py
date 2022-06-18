import datetime
from typing import Optional
import discord
from discord.ext import commands
from utils import default
from core.bot import SkyeBot
import string

from discord import app_commands

class welcomer(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot


    welcomer = app_commands.Group(name="welcomer", description="All commands for setting up welcoming",default_permissions=discord.Permissions(administrator=True))

    @welcomer.command()
    async def enable(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel], message: Optional[str]):
        """The command to enable welcoming messages"""
        message = message or "Welcome $user to $guild!"
        channel = channel or interaction.channel
        exists =  await self.bot.pool.fetchrow("SELECT channel_id FROM WELCOME_CONFIG WHERE guild_id = $1", interaction.guild.id)


        if exists is None:
            await self.bot.pool.execute('INSERT INTO welcome_config(channel_id, message, guild_id) VALUES ($1, $2, $3)',channel.id, message,interaction.guild.id)
            em = discord.Embed(title="", color= discord.Color(0x32ff00))
            em.add_field(name="Skye welcoming is currently enabled! ", value="   Logs are in: {}".format(channel.mention))
            await interaction.response.send_message(embed=em)
        else:
            await self.bot.pool.execute('UPDATE welcome_config SET channel_id = $1, message = $2 WHERE guild_id = $3',  channel.id, message, interaction.guild.id)
            em = discord.Embed(title="", color= discord.Color(0x32ff00))
            em.add_field(name="Welcome channel Updated!", value=f"New Channel: {channel.mention}")
            await interaction.response.send_message(embed=em)


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
