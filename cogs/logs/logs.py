from io import BytesIO
from typing import Optional
import discord

from discord.ext import commands

from discord.utils import format_dt

import logging

import datetime

from core.bot import SkyeBot
from discord import app_commands


from utils import http, default

import asyncio


class Logging(commands.Cog):
    """The logging cog that holds all logging commands + events."""
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    logging = app_commands.Group(name="logging",description="All logging commands",default_permissions=discord.Permissions(administrator=True))

    @logging.command(name="enable")
    @commands.has_permissions(administrator=True)
    async def _enable(self, interaction: discord.Interaction,  channel: Optional[discord.TextChannel]):
        exists = await self.bot.pool.fetchrow("SELECT channel_id FROM LOGS WHERE guild_id = $1", interaction.guild.id)
        try:
            channel = channel or interaction.channel
   
            if (exists == None):    
                await self.bot.pool.execute('INSERT INTO logs(channel_id, guild_id) VALUES ($1, $2)',channel.id, interaction.guild.id)
                em = discord.Embed(title="", color=discord.Color(0x32ff00))
                em.add_field(name="Logging currently enabled! ", value="   Logs are in: {}".format(channel.mention))
                await interaction.response.send_message(embed=em)
            else:
                await self.bot.pool.execute('UPDATE logs SET channel_id = $1 WHERE guild_id = $2',  channel.id, interaction.guild.id)
                em = discord.Embed(title="", color=discord.Color(0x32ff00))
                em.add_field(name="Logging channel Updated!", value="New Channel: {}".format(channel.mention))
                await interaction.response.send_message(embed=em)
        except (Exception) as e:
            await interaction.response.send_message(f"AAAAA\n{e}")


    @logging.command(name="disable")
    @commands.has_permissions(administrator=True)
    async def _disable(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel]):
        try:
            channel = channel or interaction.channel

            exists = await self.bot.pool.fetchrow("SELECT channel_id FROM LOGS WHERE guild_ida = $1", interaction.guild.id)

            if exists is None:
                return await interaction.response.send_message("Logging Is Not Enabled!", ephemeral=True)

            if (exists is not None):
                await self.bot.pool.execute("UPDATE logs SET channel_id = NULL, guild_id = NULL where guild_ida= $1", interaction.guild.id)
                await interaction.response.send_message("Logging is now disabled!", ephemeral=True)
        except Exception as e:
            return await interaction.response.send_message(f"Oh No! an error occured!\n\nError Class: **{e.__class__.__name__}**\n{default.traceback_maker(err=e)}If you're a coder and you think this is a fatal error, DM Sawsha#0598!", ephemeral=True)
        
    @commands.Cog.listener()
    async def on_message_delete(self,message: discord.Message):
        
        try:
            exists = await self.bot.pool.fetchval("SELECT channel_id FROM LOGS WHERE guild_id = $1", message.guild.id)
            channel = self.bot.get_channel(exists)
            if exists is not None:
                if message.author is message.author.bot:
                    pass
                else:
                    deleted = discord.Embed(
                     description = f"Message deleted in {message.channel.mention}"
                    )
                    deleted.set_author(name=message.author, icon_url=message.author.avatar)
                    deleted.timestamp = message.created_at
                    deleted.color = discord.Color.random()
                    self.bot.logger.info(deleted.color)

                    if message.content:
                        deleted.add_field(name="Message:\n", value=message.content, inline=False)
                        deleted.add_field(name="ID:", value=f"```User = {message.author.id}\nMessage = {message.id}```")

                        await channel.send(embed=deleted)
                    if message.attachments:
                        file = message.attachments[0]
                        file_type = file.proxy_url.split(".")

                        if len(file_type) != 1 and file_type[-1] in ["png", "jpeg","gif", "webp", "jpg"]:
                            req = await http.get(file.proxy_url, res_method="read",no_cache=True)
                            print(file.proxy_url)
                            bio = BytesIO(req)
                            bio.seek(0)
                            deleted.set_image(url=f"attachment://{file.filename}")
                            send_file = discord.File(bio, filename=file.filename)

                            deleted.add_field(name="Deleted Image:", value=f"[{file.filename}]({file.proxy_url})",inline=False)
                            deleted.add_field(name="ID:", value=f"```User = {message.author.id}\nMessage = {message.id}```",inline=False)

                            await channel.send(embed=deleted, file=send_file)

                        if len(file_type) != 1 and file_type[-1] in ["mp4", "mov", "webm"]:
                            req = await http.get(file.proxy_url, res_method="read",no_cache=True)
                            bio = BytesIO(req)
                            bio.seek(0)
                            send_file = discord.File(bio, filename=file.filename)

                            deleted.add_field(name="Deleted Video:", value=f"[{file.filename}]({file.proxy_url})",inline=False)
                            deleted.add_field(name="ID:", value=f"```User = {message.author.id}\nMessage = {message.id}```",inline=False)
                            await channel.send(embed=deleted, file=send_file)
        except:
            pass



                

    @commands.Cog.listener()
    async def on_message_edit(self,before, after):
        try:
            if before.content == after.content:
                    pass
            else:
                if before.author is self.bot.user.bot:
                    pass
                else:
                    exists = await self.bot.pool.fetchrow("SELECT channel_id FROM LOGS WHERE guild_id = $1", before.guild.id)
                    channel = self.bot.get_channel(exists.get("channel_id"))
                    embed = discord.Embed(
                    timestamp=after.created_at,
                    description = f"<@!{before.author.id}>**'s message was edited in** <#{before.channel.id}>.",
                    colour = discord.Colour(0x00FF00)
                    )

                    print(channel)
                    print(exists)
                    embed.set_author(name=f'{before.author.name}#{before.author.discriminator}', icon_url=before.author.avatar)
                    embed.set_footer(text=f"Author ID:{before.author.id} • Message ID: {before.id}")
                    embed.add_field(name='Before:', value=before.content, inline=False)
                    embed.add_field(name="After:", value=after.content, inline=False)
                    embed.add_field(name="ID:", value=f"```User = {before.author.id} \nMessage = {before.id}```", inline=False)

                    await channel.send(embed=embed)
        except:
            pass



    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user:discord.Member):
        try:
            exists = await self.bot.pool.fetchrow("SELECT channel_id FROM LOGS WHERE guild_id = $1", guild.id)
            channel = self.bot.get_channel(exists.get("channel_id"))

            show_roles = ", ".join(
                [f"<@&{x.id}>" for x in sorted(user.roles, key=lambda x: x.position, reverse=True) if
                 x.id != user.guild.default_role.id]
            ) if len(user.roles) > 1 else "None"

            embed =discord.Embed(
                description = f"Member {user.mention} was banned!"
                    )
            
            embed.set_author(name=user, icon_url=user.avatar)
            embed.add_field(name="ID:", value=f"```User = {user.id} \n```", inline=False)
            embed.add_field(name="Roles", value=show_roles, inline=False)
            embed.timestamp = datetime.datetime.utcnow()
            
            await channel.send(embed=embed)

        except:
            pass

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user:discord.Member):
        try:
            exists = await self.bot.pool.fetchrow("SELECT channel_id FROM LOGS WHERE guild_id = $1", guild.id)
            channel = self.bot.get_channel(exists.get("channel_id"))

            embed = discord.Embed(
                title=f"User: {user.mention} was unbanned!"
                    )
            
            embed.set_author(name=user, icon_url=user.avatar)
            embed.add_field(name="ID:", value=f"```User = {user.id} \n```", inline=False)
            embed.timestamp = datetime.datetime.utcnow()
            
            await channel.send(embed=embed)
        except:
            pass

        
    

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        try:
            exists = await self.bot.pool.fetchrow("SELECT channel_id FROM LOGS WHERE guild_id = $1", role.guild.id)
            channel = self.bot.get_channel(exists.get("channel_id"))

            embed = discord.Embed(description=f"Role: {role} Was created!")
            embed.add_field(name="ID of Role:", value=f"{role.id}")
            embed.timestamp = datetime.datetime.utcnow()

            await channel.send(embed=embed)

        except:
            pass
            
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        try:
            exists = await self.bot.pool.fetchrow("SELECT channel_id FROM LOGS WHERE guild_id = $1", role.guild.id)
            channel = self.bot.get_channel(exists.get("channel_id"))

            self.bot.logger.info(exists)
            embed = discord.Embed(description=f"**Role: {role.name} Was Deleted!**")

            async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_delete):
                if entry.id == role.id:
                    embed.add_field(name=f"Responsible Moderator", value=f"{entry.user}")

                 


            embed.add_field(name = "ID of Role:", value=f"{role.id}")
            embed.timestamp = datetime.datetime.utcnow()

            await channel.send(embed=embed)

        except:
            pass

      

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            exists = await self.bot.pool.fetchrow("SELECT channel_id FROM LOGS WHERE guild_id = $1", member.guild.id)
            channel = self.bot.get_channel(exists.get("channel_id"))


            show_roles = ", ".join(
                [f"<@&{x.id}>" for x in sorted(member.roles, key=lambda x: x.position, reverse=True) if
                 x.id != member.guild.default_role.id]
            ) if len(member.roles) > 1 else "None"

            embed = discord.Embed(title=f"New member!\nThis server is now at {len(member.guild.members)} Members", description=f"Member username: {member}", timestamp=datetime.datetime.utcnow(), color=discord.Color.dark_green)
            embed.add_field(name=f"Join server date: ",value=default.date(member.joined_at), inline=False)
            embed.add_field(name="Account created", value=default.date(member.created_at, ago=True), inline=False)
            embed.add_field(name="User ID", value=member.id, inline=False)
            embed.add_field(name="Roles", value=show_roles, inline=False)
            embed.add_field(name="Account created", value=default.date(member.created_at, ago=True), inline=False)
            embed.set_thumbnail(url=f"{member.avatar}")
            embed.set_footer(text=member.id)
            
            await channel.send(embed=embed)
            
        except:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        try:
            exists = await self.bot.pool.fetchrow("SELECT channel_id FROM LOGS WHERE guild_id = $1", member.guild.id)
            channel = self.bot.get_channel(exists.get("channel_id"))

            show_roles = ", ".join(
                [f"<@&{x.id}>" for x in sorted(member.roles, key=lambda x: x.position, reverse=True) if
                 x.id != member.guild.default_role.id]
            ) if len(member.roles) > 1 else "None"

            embed = discord.Embed(title=f"A Member Left!\nThis server is now at {len(member.guild.members)} Members!", description=f"Member username: {member}", timestamp=datetime.datetime.utcnow(), color=discord.Color.brand_red)
            embed.add_field(name=f"left server date: ",value=default.date(datetime.datetime.utcnow(), ago=True), inline=False)
            embed.add_field(name="Account created", value=default.date(member.created_at, ago=True), inline=False)
            embed.add_field(name="User ID", value=member.id, inline=False)
            embed.add_field(name="Roles", value=show_roles, inline=False)
            embed.add_field(name="Account created", value=default.date(member.created_at, ago=True), inline=False)
            embed.set_thumbnail(url=f"{member.avatar.url}")
            embed.set_footer(text=member.id)

            await channel.send(embed=embed)
        
        except TypeError:
            pass

    @commands.Cog.listener()
    async def on_guild_emojis_update(self,guild: discord.Guild, before: discord.Emoji, after: discord.Emoji):
        if before == after:
            return

        if before != after and after is not None:
            pass


    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        try:
            exists = await self.bot.pool.fetchrow("SELECT channel_id FROM LOGS WHERE guild_id = $1", before.guild.id)
            channel = self.bot.get_channel(exists.get("channel_id"))
        
            if before.name != after.name and after.name is not None:
                embed = discord.Embed(description=f"Channel ``{before.name}`` Has been updated!")
                embed.add_field(name="Old name:", value=before.name, inline=False)
                embed.add_field(name="New name:", value=after.name, inline=False)
                embed.timestamp = datetime.datetime.utcnow()

                await channel.send(embed=embed)

            if before.category != after.category and after.category is not None:

                embed = discord.Embed(description=f"Channel ``{before.name}``'s Category has been updated!")
                embed.add_field(name=f"Old category:", value=before.category, inline=False)
                embed.add_field(name="New Category:", value=after.category, inline=False)
                embed.timestamp = datetime.datetime.utcnow()

                await channel.send(embed=embed)


        except:
            pass


