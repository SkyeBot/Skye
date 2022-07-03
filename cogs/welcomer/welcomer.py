import datetime
from typing import Optional, Union
import discord
from discord.ext import commands
from utils import default
from core.bot import SkyeBot
import string
from utils.context import Context

from discord import app_commands

class WelcomerModal(discord.ui.Modal):
    def __init__(self , bot: SkyeBot=None, interaction: discord.Interaction=None, channel: discord.TextChannel=None):
        self.bot: SkyeBot = bot
        self.interaction = interaction
        self.channel = channel 
        super().__init__(title='Welcome Message')
   
    message = discord.ui.TextInput(placeholder="Variables: $user and $guild",label="Message ",style=discord.TextStyle.short)


    async def on_submit(self, interaction: discord.Interaction):
        exists =  await self.bot.pool.fetchrow("SELECT channel_id FROM WELCOME_CONFIG WHERE guild_id = $1", interaction.guild.id)
        if exists is None:
            await self.bot.pool.execute('INSERT INTO welcome_config(channel_id, message, guild_id) VALUES ($1, $2, $3)',self.channel.id, self.message.value,interaction.guild.id)
            new_text = string.Template(self.message.value).safe_substitute(
                user=interaction.user.mention,
                guild=interaction.guild
            )

            return await interaction.response.send_message(f"Welcome Message Is Now Set To: **{new_text}**", ephemeral=True, allowed_mentions=discord.AllowedMentions.none())
        else:
            await self.bot.pool.execute('UPDATE welcome_config SET channel_id = $1, message = $2 WHERE guild_id = $3',  self.channel.id, self.message.value, interaction.guild.id)
            new_text = string.Template(self.message.value).safe_substitute(
                user=interaction.user.mention,
                guild=interaction.guild
            )
            return await interaction.response.send_message(f"Welcome Message Is Now Updated To: **{new_text}**", ephemeral=True, allowed_mentions=discord.AllowedMentions.none())

class WelecomerView(discord.ui.View):
    def __init__(self, ctx: Union[Context, discord.Interaction]):
        self.ctx = ctx
        super().__init__(timeout=None)

    @discord.ui.button(label="Custom Message", style=discord.ButtonStyle.grey)
    async def confirm(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.send_modal(WelcomerModal(interaction.client, interaction, interaction.channel))
    


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if isinstance(self.ctx, discord.Interaction):
            user = self.ctx.user.id
        else:
            user = self.ctx.author.id
        
        if interaction.user and interaction.user.id == user:
            return True
        await interaction.response.defer()
        await interaction.followup.send(f"You cant use this as you're not the command invoker, only the author (<@{user}>) Can Do This!", ephemeral=True)
        return False

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

            new_text = discord.utils.escape_mentions(new_text)

            embed = discord.Embed(title=f"Welcome {member} to {member.guild}!", description=f"{new_text}")

            embed.timestamp = datetime.datetime.utcnow()
            embed.set_thumbnail(url=f"{member.avatar}")
            
            await channel.send(embed=embed)    
        except Exception as e:
            print(e)
