import discord

from discord.ext import commands

import pymongo

from pymongo import MongoClient


class extra(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def disable(self, ctx,command_name=None):
        guild_id = ctx.guild.id
        mongo_url = "m"
        cluster = MongoClient(mongo_url)
        db = cluster["skye"]
        collection = db["commands"]
       
       
        if command_name == None:
            await ctx.send("Please give me a command you want to disable!")
            return
            

        try:

            command = self.bot.get_command(command_name)
            disabled = command.update(enabled=False)

            if collection.count_documents({"_id":id}) == 0:
                collection.insert_one({"_id":0})
                
            collection.update_one({"_id":id, "guildID":guild_id},{"$set":{"Disabled/Enabled":disabled, "Command":command_name}})

        except:
            # this gets sent if the bot can't: a) get the command or b) disable the command
            await ctx.send("That isn't a valid command!")
            return

        await ctx.send(f"I have disabled the command {command_name}")


    @commands.command()
    async def enable(self, ctx,command_name=None):
        guild_id = ctx.guild.id
        mongo_url = ""
        cluster = MongoClient(mongo_url)
        db = cluster["skye"]
        collection = db["commands"]
       
       
        if command_name == None:
            await ctx.send("Please give me a command you want to disable!")
            return
            

        try:

            command = self.bot.get_command(command_name)
            disabled = command.update(enabled=True)

            if collection.count_documents({"_id":id}) == 0:
                collection.insert_one({"_id":0})
                
            collection.update_one({"_id":id, "guildID":guild_id},{"$set":{"Disabled/Enabled":disabled, "Command":command_name}})

        except:
            # this gets sent if the bot can't: a) get the command or b) disable the command
            await ctx.send("That isn't a valid command!")

        await ctx.send(f"I have disabled the command {command_name}")


    








async def setup(bot):
    await bot.add_cog(extra(bot))