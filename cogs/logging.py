from io import BytesIO
import discord

from discord.ext import commands

from discord.utils import format_dt

import datetime

import pymongo
from pymongo import MongoClient

from utils import http

import asyncio

mongo_url = "" #mongodb URL
cluster = MongoClient(mongo_url)
predb = cluster["skye"]["logging"]

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.has_permissions(administrator=True)
    async def logging(self, ctx):
        exists = predb.find_one({"_id": ctx.guild.id})

        if ctx.invoked_subcommand is None:
            em = None
            if exists == None:
                em = discord.Embed(title="Logging is disabled for this guild :(", color=discord.Color(0xff0000))
                await ctx.send(embed=em)
            else:
                    em = discord.Embed(title="Logging is enabled for this guild!", color = discord.Color(0x32ff00))
                    channel = self.bot.get_channel(exists["channel_id"])
                    em.add_field(name="Current Logging Channel:", value=channel.mention)
                    await ctx.send(embed=em)

    @logging.command(name="enable")
    @commands.has_permissions(administrator=True)
    async def _enable(self, ctx, channel:discord.TextChannel=None):
        exists = predb.find_one({"_id":ctx.guild.id})
    
        try:
            if channel == None:
                await ctx.send("Please provide a channel for me for logging!")
            else:
                if (exists == None):
                    predb.insert_one({"_id": ctx.guild.id, "channel_id": channel.id})
                    em = discord.Embed(title="", color=discord.Color(0x32ff00))
                    em.add_field(name="Logging currently enabled! ", value="   Logs are in: {}".format(channel.mention))
                    await ctx.send(embed=em)
                else:
                    predb.update_one({"_id": ctx.guild.id}, {"$set": {"channel_id": channel.id}})
                    em = discord.Embed(title="", color=discord.Color(0x32ff00))
                    em.add_field(name="Logging channel Updated!", value="New Channel: {}".format(channel.mention))
                    await ctx.send(embed=em)
        except (Exception) as e:
            await ctx.send(e)



    @logging.command(name="disable")
    @commands.has_permissions(administrator=True)
    async def _disable(self, ctx, channel: discord.TextChannel):
        exists = {"_id":ctx.guild.id, "channel_id":channel.id}

        if(exists!=None):
            predb.delete_one(exists)
            await ctx.send("Logging Now disabled!")

    
    
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_collection(self, ctx,channel: discord.TextChannel):
        guild_id = ctx.guild.id 

        predb.insert_one({"_id": guild_id, "channel_id":"null"})
        await ctx.send("Done!")


    @commands.Cog.listener()
    async def on_message_delete(self,message):
        
        try:
            
            exists = predb.find_one({"_id":message.guild.id})

            channel = await self.bot.fetch_channel(exists["channel_id"])
        
            if exists is not None:
                deleted = discord.Embed(
                description = f"Message deleted in {message.channel.mention}"
                    )
                deleted.set_author(name=message.author, icon_url=message.author.avatar)
                deleted.timestamp = message.created_at
                
                
                if message.content:
                    deleted.add_field(name="Message:\n", value=message.content, inline=False)
                    deleted.add_field(name="ID:", value=f"```User = {message.author.id}\nMessage = {message.id}```")
                    
                    await channel.send(embed=deleted)
                if message.attachments:
                    file = message.attachments[0]
                    file_type = file.proxy_url.split(".")

                    if len(file_type) != 1 and file_type[-1] in ["png", "jpeg","gif", "webp"]:
                        req = await http.get(file.proxy_url, res_method="read",no_cache=True)
                        bio = BytesIO(req)
                        bio.seek(0)
                        deleted.set_image(url=f"attachment://{file.filename}")
                        send_file = discord.File(bio, filename=file.filename)
                    
                        deleted.add_field(name="Deleted Image:", value=f"||Ignore this||",inline=False)
                        deleted.add_field(name="ID:", value=f"```User = {message.author.id}\nMessage = {message.id}```",inline=False)

                        await channel.send(embed=deleted, file=send_file)

                    if len(file_type) != 1 and file_type[-1] in ["mp4", "mov", "webm"]:
                        req = await http.get(file.proxy_url, res_method="read",no_cache=True)
                        bio = BytesIO(req)
                        bio.seek(0)
                        send_file = discord.File(bio, filename=file.filename)
                    
                        deleted.add_field(name="Deleted Video:", value=f"s",inline=False)
                        deleted.add_field(name="ID:", value=f"```User = {message.author.id}\nMessage = {message.id}```",inline=False)

                        await channel.send(embed=deleted, file=send_file)

        except TypeError:
            pass



                

    @commands.Cog.listener()
    async def on_message_edit(self,before, after):
        try:
            try:
                if before.content == after.content:
                    pass
                else:
                    exists = predb.find_one({"id": before.guild.id})
                    channel = await self.bot.fetch_channel(exists["channel_id"])
                    embed = discord.Embed(
                    timestamp=after.created_at,
                    description = f"<@!{before.author.id}>**'s message was edited in** <#{before.channel.id}>.",
                    colour = discord.Colour(0x00FF00)
                    )


                    embed.set_author(name=f'{before.author.name}#{before.author.discriminator}', icon_url=before.author.avatar)
                    embed.set_footer(text=f"Author ID:{before.author.id} • Message ID: {before.id}")
                    embed.add_field(name='Before:', value=before.content, inline=False)
                    embed.add_field(name="After:", value=after.content, inline=False)
                    embed.add_field(name="ID:", value=f"```User = {before.author.id} \nMessage = {before.id}```", inline=False)





                    await channel.send(embed=embed)

            except discord.HTTPException:
                pass
        except TypeError:
            pass



    @commands.Cog.listener()
    async def on_member_ban(self, guild, user:discord.Member):
        try:
            exists = predb.find_one({"_id":guild.id})
            channel = await self.bot.fetch_channel(exists["channel_id"])

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

        except TypeError:
            pass

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user:discord.Member):
        try:
            exists = predb.find_one({"_id":guild.id})
            channel = await self.bot.fetch_channel(exists["channel_id"])

            embed = discord.Embed(
                title=f"User: {user.mention} was unbanned!"
                    )
            
            embed.set_author(name=user, icon_url=user.avatar)
            embed.add_field(name="ID:", value=f"```User = {user.id} \n```", inline=False)
            embed.timestamp = datetime.datetime.utcnow()
            
            await channel.send(embed=embed)
        except TypeError:
            pass


    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            exists = predb.find_one({"_id":member.guild.id})
            channel = await self.bot.fetch_channel(exists["channel_id"])

            show_roles = ", ".join(
                [f"<@&{x.id}>" for x in sorted(member.roles, key=lambda x: x.position, reverse=True) if
                 x.id != member.guild.default_role.id]
            ) if len(member.roles) > 1 else "None"

            embed = discord.Embed(description = f"__**Member {member.mention} Joined!**__")
            embed.add_field(name=f"ID:", value=f"```User: {member.id}```", inline=False)
            embed.add_field(name="Roles", value=show_roles, inline=False)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_thumbnail(url=member.avatar)

            await channel.send(embed=embed)
            
        except TypeError:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        try:
            exists = predb.find_one({"_id":member.guild.id})
            channel = await self.bot.fetch_channel(exists["channel_id"])

            show_roles = ", ".join(
                [f"<@&{x.id}>" for x in sorted(member.roles, key=lambda x: x.position, reverse=True) if
                 x.id != member.guild.default_role.id]
            ) if len(member.roles) > 1 else "None"

            embed = discord.Embed(description = f"__**Member {member.mention} left :(**__")
            embed.add_field(name=f"ID:", value=f"```User: {member.id}```", inline=False)
            embed.add_field(name="Roles", value=show_roles, inline=False)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_thumbnail(url=member.avatar)

            await channel.send(embed=embed)
            
        except TypeError:
            pass

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        try:
            exists = predb.find_one({"_id":before.guild.id})
            channel = await self.bot.fetch_channel(exists["channel_id"])

            if before.nick != after.nick and after.nick is not None:

                embed = discord.Embed(title=f"User: ``{before}`` Changed their nickname to ``{after.name}``")
                embed.add_field(name=f"ID:", value=f"```{before.id}```", inline=False)
                embed.set_thumbnail(url=before.avatar)
                embed.timestamp = datetime.datetime.utcnow()

                await channel.send(embed=embed)

            if before.roles != after.roles and after.roles is not None:
                show_roles = ", ".join(
                    [f"<@&{x.id}>" for x in sorted(after.roles, key=lambda x: x.position, reverse=True) if
                     x.id != before.guild.default_role.id]
                ) if len(before.roles) > 1 else ""

                embed = discord.Embed(title=f"User ``{before}`` Has gotten their roles updated!")
                embed.add_field(name=f"New roles", value=f"{show_roles}", inline=False)
                embed.set_thumbnail(url=before.avatar)
                embed.timestamp = datetime.datetime.utcnow()

                await channel.send(embed=embed)

        except TypeError:
           pass

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        try:
            exists = predb.find_one({"_id":role.guild.id})
            channel = await self.bot.fetch_channel(exists["channel_id"])

            embed = discord.Embed(description=f"Role: {role} Was created!")
            embed.add_field("ID of Role:", value=f"{role.id}")
            embed.timestamp = datetime.datetime.utcnow()

            await channel.send(embed=embed)



        except TypeError:
            pass
      
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        try:
            exists = predb.find_one({"_id":before.guild.id})
            channel = await self.bot.fetch_channel(exists["channel_id"])

        
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


        except TypeError:
            pass



        




async def setup(bot):
    await bot.add_cog(Logging(bot))
