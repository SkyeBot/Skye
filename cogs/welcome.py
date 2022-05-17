import datetime
import discord

from discord.ext import commands

import pymongo
from pymongo import MongoClient



from utils import default


class Welcoming(commands.Cog):
    """Cog to hold all welcome commands + events"""
    def __init__(self, bot: commands.Cog):
        self.bot = bot

    @commands.group()
    async def welcome(self, ctx):
        pass


    @welcome.command(name="enable")
    @commands.has_permissions(administrator=True)
    async def _enable(self, ctx, channel:discord.TextChannel=None):
        exists =  await self.bot.db.fetchrow("SELECT channel_id FROM WELCOME WHERE guild_id = $1", ctx.guild.id)

        try: 
                if channel == None:
                    await ctx.send("Please provide a channel for me to welcome new members in!")
                else:
                    if (exists==None):
                        await self.bot.db.execute('INSERT INTO welcome(channel_id, guild_id) VALUES ($1, $2)',channel.id, ctx.guild.id)
                        em = discord.Embed(title="", color= discord.Color(0x32ff00))
                        em.add_field(name="Skye welcoming is currently enabled! ", value="   Logs are in: {}".format(channel.mention))
                        await ctx.send(embed=em)
                    else:
                        await self.bot.db.execute('UPDATE welcome SET channel_id = $1 WHERE guild_id = $2',  channel.id, ctx.guild.id)
                        em = discord.Embed(title="", color= discord.Color(0x32ff00))
                        em.add_field(name="Welcome channel Updated!", value="New Channel: {}".format(channel.mention))
                        await ctx.send(embed=em)
        except (Exception) as e:
            await ctx.send(e)


    @welcome.command(name="disable")
    @commands.has_permissions(administrator=True)
    async def _disable(self, ctx, channel: discord.TextChannel):
        exists = await self.bot.db.fetchrow("SELECT channel_id FROM welcome WHERE guild_id = $1", ctx.guild.id)

        if(exists!=None):
            await self.bot.db.execute("UPDATE welcome SET channel_id = NULL, guild_id = NULL where guild = $1", ctx.guild.id)
            await ctx.send("Welcoming Now disabled!")


    @commands.Cog.listener()
    async def on_member_join(self,member:discord.Member):
        try: 

            exists = await self.bot.db.fetchrow("SELECT * FROM WELCOME WHERE guild_id = $1", member.guild.id)
            channel = await self.bot.fetch_channel(exists.get("channel_id"))
            print(exists)
            print(channel)


            show_roles = ", ".join(
            [f"<@&{x.id}>" for x in sorted(member.roles, key=lambda x: x.position, reverse=True) if x.id != member.guild.default_role.id]
            ) if len(member.roles) > 1 else "Default Role"

            embed = discord.Embed(title=f"Welcome {member} to {member.guild}!", description=f"**You are the {len(member.guild.members)} member!**")

            embed.timestamp = datetime.datetime.utcnow()
            embed.set_thumbnail(url=f"{member.avatar}")
            
            await channel.send(embed=embed)


     
            
            try:
                exists2 = await self.bot.db.fetchrow("SELECT * FROM LOGS WHERE guild_id = $1", member.guild.id)
                channel2 = await self.bot.fetch_channel(exists2.get("channel_id"))
                
                embed2 = discord.Embed(title=f"New member! This server is now at {len(member.guild.members)}", description=f"Member username: {member}", timestamp=datetime.datetime.utcnow())
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

                


        except:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        try:
            exists = await self.bot.db.fetchrow("SELECT * FROM WELCOME WHERE guild_id = $1", member.guild.id)
            channel = await self.bot.fetch_channel(exists.get("channel_id"))

            print(exists)
            print(channel)

            show_roles = ", ".join(
                [f"<@&{x.id}>" for x in sorted(member.roles, key=lambda x: x.position, reverse=True) if
                 x.id != member.guild.default_role.id]
            ) if len(member.roles) > 1 else "Default Role"

            embed = discord.Embed(title=f"NOOOO Member: {member} left the server! we're now at {len(member.guild.members)} Members")
            embed.add_field(name="Account created", value=default.date(member.created_at, ago=True), inline=False)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_thumbnail(url=f"{member.avatar}")

            await channel.send(embed=embed)

            try:
                exists2 = await self.bot.db.fetchrow("SELECT * FROM LOGS WHERE guild_id = $1", member.guild.id)
                channel2 = await self.bot.fetch_channel(exists2.get("channel_id"))
                
                embed2 = discord.Embed(title=f"Member Left!! This server is now at {len(member.guild.members)}", description=f"Member username: {member}", timestamp=datetime.datetime.utcnow())
                embed2.add_field(name=f"left server date: ",value=default.date(datetime.datetime.utcnow(), ago=True), inline=False)
                embed2.add_field(name="Account created", value=default.date(member.created_at, ago=True), inline=False)
                embed2.add_field(name="User ID", value=member.id, inline=False)
                embed2.add_field(name="Roles", value=show_roles, inline=False)
                embed2.add_field(name="Account created", value=default.date(member.created_at, ago=True), inline=False)
                embed2.set_thumbnail(url=f"{member.avatar}")
                embed2.set_footer(text=member.id)


                await channel2.send(embed=embed2)
            except Exception as e:
                print(default.traceback_maker(e))
        except:
            pass



async def setup(bot):
    await bot.add_cog(Welcoming(bot))