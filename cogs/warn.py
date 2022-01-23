import discord

from discord.ext import commands

import pymongo

from pymongo import MongoClient

mongo_url = ""
cluster = MongoClient(mongo_url)
db = cluster[""]
collection = db[""]


class warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def warn(self,ctx, member:discord.Member, *, reason=None):
        id = member.id
        guild_id = ctx.guild.id
        
        if collection.count_documents({"_id":id}) == 0:
            collection.insert_one({"_id": id,"warns":0, "guild_id":guild_id})


        if reason == None:
            reason = "No Reason Specified"
        if member == None:
            return await ctx.send("Please mention a user!")

        warn_count = collection.find_one({"_id":id})

        count = warn_count["warns"]
        new_count = count + 1

        collection.update_one({"_id":id, "guildID":guild_id},{"$set":{"warns":new_count}})

        embed = discord.Embed(title=f"Warned {member}", description=f"Reason: {reason}")

        embed.add_field(name=f"They now have **{new_count}** Warnings!", value=f"\nResponsible Moderator: {ctx.author.mention}")

        embed2 = discord.Embed(title=f"You have been warned from {ctx.guild}!", description=f"reason: {reason} \n Responsible Moderator: {ctx.author}")


        await ctx.send(embed=embed)

        await member.send(embed=embed2)

    @warn.error
    async def warn_error(self,ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"<a:siren:922358771735461939> You can't use this command! Command requires ``Manage Messages`` Permissions! <a:siren:922358771735461939>")

    




def setup(bot):
    bot.add_cog(warn(bot))
