
from io import BytesIO
import discord
from discord.ext import commands
from discord import app_commands
from utils import http


class Starboard(commands.Cog):
    """Cog for all stuff starboard related such as events and commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    group = app_commands.Group(name="starboard", description="Starboard settings")

    @group.command(name="enable")
    @app_commands.checks.has_permissions(administrator=True)
    async def _enable(self, interaction: discord.Interaction, channel: discord.TextChannel  =None):
        exists =  await self.bot.db.fetchrow("SELECT channel_id FROM STARBOARD WHERE guild = $1", interaction.guild.id)

        try: 
                if channel == None:
                    await interaction.response.send_message("No channel provided")
                else:
                 if (exists==None):
                    await self.bot.db.execute('INSERT INTO starboard(channel_id, guild) VALUES ($1, $2)',channel.id, interaction.guild.id)
                    em = discord.Embed(title="", color= discord.Color(0x32ff00))
                    em.add_field(name="starboard enabled", value="Current channel: {}".format(channel.mention))
                    await interaction.response.send_message(embed=em)
                 else:
                    await self.bot.db.execute('UPDATE starboard SET channel_id = $1 WHERE guild = $2',  channel.id, interaction.guild.id)
                    em = discord.Embed(title="", color= discord.Color(0x32ff00))
                    em.add_field(name="starboard Updated", value="new channel: {}".format(channel.mention))
                    await interaction.response.send_message(embed=em)
        except (Exception) as e:
            await interaction.response.send_message(e)    

    @group.command(name="disable")
    @app_commands.checks.has_permissions(administrator=True)
    async def _disable(self, interaction: discord.Interaction, channel: discord.TextChannel):
        exists =  await self.bot.db.fetchrow("SELECT channel_id FROM starboard WHERE guild = $1", interaction.guild.id)
        
        if(exists!=None):
            await self.bot.db.execute("UPDATE starboard SET channel_id = NULL, guild = NULL where guild = $1", interaction.guild.id)
            await interaction.response.send_message("starboard is now disabled!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        try:
            if payload.emoji.name == "⭐":

                exists =  await self.bot.db.fetchrow("SELECT channel_id FROM starboard WHERE guild = $1", payload.guild_id)
                channel = await self.bot.fetch_channel(exists.get("channel_id"))
                payload_channel = await self.bot.fetch_channel(payload.channel_id)
                message = await payload_channel.fetch_message(payload.message_id)
                print(len(message.reactions))
                embed = discord.Embed(description=message.content) 
                embed.set_author(name=message.author, icon_url=message.author.display_avatar.url)
                embed.add_field(name="Original Message", value=f"[Jump to the message!]({message.jump_url})", inline=False)
                
                if message.attachments:
                    file = message.attachments[0]
                    file_type = file.proxy_url.split(".")


                    if len(file_type) != 1 and file_type[-1] in ["png", "jpeg","gif", "webp", "jpg"]:
                        req = await http.get(file.proxy_url, res_method="read",no_cache=True)
                        bio = BytesIO(req)
                        bio.seek(0)
                        embed.set_image(url=file.proxy_url)

                    if len(file_type) != 1 and file_type[-1] in ["mp4", "mov", "webm"]:
                        req = await http.get(file.proxy_url, res_method="read",no_cache=True)
                        bio = BytesIO(req)
                        bio.seek(0)
                        embed.add_field(name="Attachment", value=f"[{file.filename}]({file.proxy_url})")

                if message.reference:
                    replied = await channel.fetch_message(message.reference.message_id)
                    embed.add_field(name="Replied to:", value=f"[{replied.author}]({message.reference.jump_url})", inline=False)

                await channel.send(content=f"⭐ {len(message.reactions)} {payload_channel.mention} ID: {message.id}",embed=embed)

        except Exception as e:
            print(e)
    
    
    @commands.command()
    async def test(self, ctx: commands.Context):
        exists =  await self.bot.db.fetchrow("SELECT channel_id FROM starboard WHERE guild = $1", ctx.guild.id)
        channel = await self.bot.fetch_channel(exists.get("channel_id"))

        await channel.send("Test")
        await ctx.send("Done")
async def setup(bot: commands.Bot):
    await bot.add_cog(Starboard(bot))
