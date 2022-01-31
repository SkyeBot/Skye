from datetime import datetime
import discord

from discord.ext import commands

from discord.utils import format_dt


import pymongo
from pymongo import MongoClient

mongo_url = ""
cluster = MongoClient(mongo_url)
predb = cluster[""][""]

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
    async def _enable(self, ctx, channel: discord.TextChannel=None):
        exists = predb.find_one({"_id":ctx.guild.id})
    
        try: 
                if channel == None:
                    await ctx.send("Please provide a channel for me for logging!")
                else:
                    if (exists==None):
                        predb.insert_one({"_id":ctx.guild.id, "channel_id": channel.id})
                        em = discord.Embed(title="", color= discord.Color(0x32ff00))
                        em.add_field(name="Logging currently enabled! ", value="   Logs are in: {}".format(channel.mention))
                        await ctx.send(embed=em)
                    else:
                        predb.update_one({"_id":ctx.guild.id}, {"$set": {"channel_id": channel.id}})
                        em = discord.Embed(title="", color= discord.Color(0x32ff00))
                        em.add_field(name="Logging channel Updated!", value="New Channel: {}".format(channel.mention))
                        await ctx.send(embed=em)
        except (Exception) as e:
            await ctx.send(e)



    @logging.command(name="disable")
    @commands.has_permissions(administrator=True)
    async def _disable(self, ctx, channel: discord.TextChannel):
        exists = ({"_id":ctx.guild.id}, {"$set": {"channel_id": "null"}})

        if(exists!=None):
            predb.update_one(exists)
            await ctx.send("Logging Now disabled!")

    
    
    
    @commands.command()
    async def add_collection(self, ctx,channel: discord.TextChannel):
        guild_id = ctx.guild.id 

        predb.insert_one({"_id": guild_id, "channel_id":"null"})
        await ctx.send("Done!")


    @commands.Cog.listener()
    async def on_message_delete(self,message):
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
            if message.attachments:
                deleted.add_field(name="Deleted Image:", value=f"||Ignore this||",inline=False)
                deleted.set_image(url=message.attachments[0].url)
                deleted.add_field(name="ID:", value=f"```User = {message.author.id}\nMessage = {message.id}```",inline=False)

            await channel.send(embed=deleted)

        
            





    @commands.Cog.listener()
    async def on_message_edit(self,before, after):
        exists = predb.find_one({"_id":before.guild.id})
        channel = await self.bot.fetch_channel(exists["channel_id"])
        
        try:
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
            await channel.send(f"Message edited in {before.channel.mention} \n Before: {before.attachments[0].url} \n After: {after.attachments[0].url}")


def setup(bot):
    bot.add_cog(Logging(bot))
