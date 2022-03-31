import datetime
import discord

from discord.ext import commands

import pymongo
from pymongo import MongoClient

mongo_url = "" #put your Mongodb url here
cluster = MongoClient(mongo_url)
predb = cluster["skye"]["welcome"]

mongo_url2 = ""
cluster2 = MongoClient(mongo_url)
predb2 = cluster["skye"]["logging"]

from utils import default


class Welcoming(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def welcome(self, ctx):
        pass


    @welcome.command(name="set")
    @commands.has_permissions(administrator=True)
    async def _set(self, ctx, channel:discord.TextChannel=None):
        exists = predb.find_one({"_id":ctx.guild.id})

        try: 
                if channel == None:
                    await ctx.send("Please provide a channel for me to welcome new members in!")
                else:
                    if (exists==None):
                        predb.insert_one({"_id":ctx.guild.id, "channel_id": channel.id})
                        em = discord.Embed(title="", color= discord.Color(0x32ff00))
                        em.add_field(name="Skye welcoming is currently enabled! ", value="   Logs are in: {}".format(channel.mention))
                        await ctx.send(embed=em)
                    else:
                        predb.update_one({"_id":ctx.guild.id}, {"$set": {"channel_id": channel.id}})
                        em = discord.Embed(title="", color= discord.Color(0x32ff00))
                        em.add_field(name="Welcome channel Updated!", value="New Channel: {}".format(channel.mention))
                        await ctx.send(embed=em)
        except (Exception) as e:
            await ctx.send(e)


    @welcome.command(name="disable")
    @commands.has_permissions(administrator=True)
    async def _disable(self, ctx, channel: discord.TextChannel):
        exists = {"_id":ctx.guild.id, "channel_id":channel.id}

        if(exists!=None):
            predb.delete_one(exists)
            await ctx.send("Welcome Now disabled!")

    @commands.Cog.listener()
    async def on_member_join(self,member:discord.Member):
        try: 

            exists = predb.find_one({"_id":member.guild.id})
            channel = await self.bot.fetch_channel(exists["channel_id"])
            


            show_roles = ", ".join(
            [f"<@&{x.id}>" for x in sorted(member.roles, key=lambda x: x.position, reverse=True) if x.id != member.guild.default_role.id]
            ) if len(member.roles) > 1 else "Default Role"

            embed = discord.Embed(title=f"Welcome {member} to {member.guild}!")
            embed.add_field(name=f"Date of joined server: ",value=default.date(member.joined_at), inline=False)
            embed.add_field(name="Account created", value=default.date(member.created_at, ago=True), inline=False)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_thumbnail(url=f"{member.avatar}")
            
            await channel.send(embed=embed)


     
            
            try:
                exists2 = predb2.find_one({"_id":member.guild.id})
                channel_id = int(exists2["channel_id"])
                channel2 = await self.bot.fetch_channel(channel_id)

                embed2 = discord.Embed(title=f"New member! This server is now at {len(member.guild.members)}", description=f"Member username: {member}", timestamp=datetime.datetime.utcnow)
                embed2.add_field(name=f"Join server date: ",value=default.date(member.joined_at), inline=False)
                embed2.add_field(name="Account created", value=default.date(member.created_at, ago=True), inline=False)
                embed2.add_field(name="User ID", value=member.id, inline=False)
                embed2.add_field(name="Roles", value=show_roles, inline=False)
                embed2.add_field(name="Account created", value=default.date(member.created_at, ago=True), inline=False)
                embed2.set_thumbnail(url=f"{member.avatar}")
                embed2.set_footer(text=member.id)


                await channel2.send(embed=embed2)
            except ValueError:
                pass

                


        except TypeError:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        try:
            exists = predb.find_one({"_id": member.guild.id})
            channel = await self.bot.fetch_channel(exists["channel_id"])

            show_roles = ", ".join(
                [f"<@&{x.id}>" for x in sorted(member.roles, key=lambda x: x.position, reverse=True) if
                 x.id != member.guild.default_role.id]
            ) if len(member.roles) > 1 else "Default Role"

            embed = discord.Embed(title=f"NOOOO Member: {member} left the server! we're now at {len(member.guild.members)} Members")
            embed.add_field(name="Account created", value=default.date(member.created_at, ago=True), inline=False)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_thumbnail(url=f"{member.avatar}")

            await channel.send(embed=embed)

        except  TypeError:
            pass



async def setup(bot):
    await bot.add_cog(Welcoming(bot))