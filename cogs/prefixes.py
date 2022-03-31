import os

import discord

from discord.ext import commands
from discord.ext.commands import BucketType, cooldown
from pymongo import MongoClient


mongo_url = ""
cluster = MongoClient(mongo_url)
db = cluster[""]
collection = db[""]

class Prefix(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Prefix cog loaded successfully")

    @commands.command(
        cooldown_after_parsing=True, description="Changes Bot prefix for this server"
    )
    @cooldown(1, 10, BucketType.user)
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, new_prefix):
        if len(new_prefix) > 4:
            embed = discord.Embed(
                timestamp=ctx.message.created_at,
                title="Error",
                description="Looks like the prefix is very big ",
                color=0xFF0000,
            )
            await ctx.send(embed=embed)
        else:

            new_prefix = str(new_prefix)
            stats = collection.find_one({"_id": ctx.guild.id})

            if stats is None:
                updated = {"_id": ctx.guild.id, "prefix": new_prefix}
                collection.insert_one(updated)
                embed = discord.Embed(
                    title="Prefix",
                    description=f"This server prefix is now {new_prefix}",
                    color=0xFF0000,
                )
                await ctx.send(embed=embed)

            else:
                collection.update_one(
                    {"_id": ctx.guild.id}, {"$set": {"prefix": new_prefix}}
                )

                embed = discord.Embed(
                    timestamp=ctx.message.created_at,
                    title="Prefix",
                    description=f"This server prefix is now {new_prefix}",
                    color=0xFF0000,
                )
                await ctx.send(embed=embed)

    @setprefix.error
    async def setprefix_error(self,ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"<a:siren:922358771735461939> You can't use this command! Command requires ``Administrator`` Permissions! <a:siren:922358771735461939>")
            print(f"Command ``setprefix`` was attempted \n User Who Used It == {ctx.author}! \n ID == {ctx.author.id} \n -------------------------------------------------------")



def setup(client):
    client.add_cog(Prefix(client))