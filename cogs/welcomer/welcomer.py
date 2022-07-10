import datetime
from typing import Optional, Union
import discord
from discord.ext import commands
from utils import default
from core.bot import SkyeBot
import string
from utils.context import Context

from discord import app_commands

class WelcomerModal1(discord.ui.Modal):
    def __init__(self , bot: SkyeBot=None, interaction: discord.Interaction=None, channel: discord.TextChannel=None):
        self.bot: SkyeBot = bot
        self.interaction = interaction
        self.channel: discord.TextChannel = channel 
        
        super().__init__(title='Welcome Message')
        channels = [c.name for c in self.interaction.guild.text_channels]
        # When creating item:
        self.foo = discord.ui.Select(options=[discord.SelectOption(label=f"#{x.name}" if channels.count(x.name) == 1 else f'{x.name} - {x.category or "No Category"}' ,value=x.id) for x in channel])
        self.add_item(self.foo)



    message = discord.ui.TextInput(placeholder="Variables: $user and $guild",label="Message ",style=discord.TextStyle.paragraph)


    async def on_submit(self, interaction: discord.Interaction):
        
        try:
            exists =  await self.bot.pool.fetchrow("SELECT channel_id FROM WELCOME_CONFIG WHERE guild_id = $1", interaction.guild.id)
            if exists is None:
                await self.bot.pool.execute('INSERT INTO welcome_config(channel_id, message, guild_id) VALUES ($1, $2, $3)',int(self.foo.values[0]), self.message.value,interaction.guild.id)
                new_text = string.Template(self.message.value).safe_substitute(
                    user=interaction.user.mention,
                    guild=interaction.guild
                )

                return await interaction.response.send_message(f"Welcome Message Is Now Set To: **{new_text}**", ephemeral=True, allowed_mentions=discord.AllowedMentions.none())
        except Exception as e:
            self.bot.logger.info(e)


class WelcomerModal2(discord.ui.Modal):
    def __init__(self , bot: SkyeBot=None, interaction: discord.Interaction=None, channel: discord.TextChannel=None):
        self.bot: SkyeBot = bot
        self.interaction = interaction
        self.channel = channel 
        super().__init__(title='Welcome Message')
   
    message = discord.ui.TextInput(placeholder="Variables: $user and $guild",label="Message ",style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        exists =  await self.bot.pool.fetchrow("SELECT channel_id FROM WELCOME_CONFIG WHERE guild_id = $1", interaction.guild.id)
        await self.bot.pool.execute('UPDATE welcome_config SET channel_id = $1, message = $2 WHERE guild_id = $3', exists.get("channel_id"), self.message.value, interaction.guild.id)
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
        await interaction.response.send_modal(WelcomerModal1(interaction.client, interaction, interaction.channel))
    


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
    async def enable(self, interaction: discord.Interaction):
        """Enables Welcomer with optional message"""
        try:
            exists =  await self.bot.pool.fetchrow("SELECT channel_id FROM WELCOME_CONFIG WHERE guild_id = $1", interaction.guild.id)        



            if exists is None:
                    return await interaction.response.send_modal(WelcomerModal1(self.bot, interaction, [x for x in interaction.guild.channels if type(x) is discord.TextChannel]))
            else:
                return await interaction.response.send_modal(WelcomerModal2(self.bot, interaction, [x for x in interaction.guild.channels if type(x) is discord.TextChannel]))
        
        
        except Exception as e:
            self.bot.logger.info

    @welcomer.command()
    async def disable(self, interaction: discord.Interaction):
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
    
