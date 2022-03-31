import discord

from discord.ext import commands

import pymongo

from pymongo import MongoClient

mongo_url = ""
cluster = MongoClient(mongo_url)
predb = cluster[""][""]

class Autorole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group()
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx):
        exists = predb.find_one({"_id": ctx.guild.id})

        if ctx.invoked_subcommand is None:
            em = None
            if exists == None:
                em = discord.Embed(title="Autorole is disabled for this guild.", color=discord.Color(0xff0000))
                await ctx.send(embed=em)
            else:
                    em = discord.Embed(title="Autorole is enabled for this guild.", color = discord.Color(0x32ff00))
                    rol = discord.utils.get(ctx.guild.roles, id=exists["role"])
                    em.add_field(name="Current role:", value=rol.mention)
                    await ctx.send(embed=em)

    @commands.Cog.listener()
    async def on_member_join(self,member):
      exists = predb.find_one({"_id": member.guild.id})


      rol = discord.utils.get(member.guild.roles, id=exists["role"])
          
      await member.add_roles(rol)



    @autorole.command(name="enable")
    @commands.has_permissions(administrator=True)
    async def _enable(self, ctx, role: discord.Role=None):
        exists = {"_id":ctx.guild.id, "role":role.id}
        role2 = exists["role"]

        try: 
                if role == None:
                    await ctx.send("No role provided")
                else:
                 if (exists==None):
                    predb.insert_one({"_id":ctx.guild.id, "role":role2})
                    em = discord.Embed(title="", color= discord.Color(0x32ff00))
                    em.add_field(name="Autorole enabled", value="Current role: {}".format(role.mention))
                    await ctx.send(embed=em)
                 else:
                    predb.update_one({"_id":ctx.guild.id}, {"$set": {"role": role.id}})
                    em = discord.Embed(title="", color= discord.Color(0x32ff00))
                    em.add_field(name="Autorole Updated", value="new role: {}".format(role.mention))
                    await ctx.send(embed=em)
        except (Exception) as e:
            await ctx.send(e)    

    @autorole.command(name="disable")
    @commands.has_permissions(administrator=True)
    async def _disable(self, ctx, role: discord.Role=None):
        exists = {"_id":ctx.guild.id,"role":role.id}

        if(exists!=None):
            predb.delete_one(exists)
            await ctx.send("Autorole disabled!")

    
    
    


def setup(bot):
    bot.add_cog(Autorole(bot))
        
