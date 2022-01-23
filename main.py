import discord

from discord.ext import commands

import os 

import pymongo

from pymongo import MongoClient



token = ""


mongo_url = ""#put your own shit
cluster = MongoClient(mongo_url)
predb = cluster[""][""] #same here


async def get_prefix(client, message):
    defualt_prefix = "skye "
    stats = predb.find_one({"_id": message.guild.id})
    # server_prefix = stats["prefix"]
    if stats is None:
        updated = {"_id": message.guild.id, "prefix": "skye "} 
        predb.insert_one(updated)
        extras = "skye "
        
        return commands.when_mentioned_or(extras)(client, message)
    else:
        extras = stats["prefix"]
   
        return commands.when_mentioned_or(extras, defualt_prefix)(client, message)

prefix = "skye "

bot = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.all())
bot.remove_command('help')



@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd , activity=discord.Activity(type=discord.ActivityType.watching, name="Work is da poop! NO MORE!☁️"))
    print("Logged in as \n{0.user}".format(bot))
    print("-------------------------------------------------")

@bot.event
async def on_guild_join(guild):
  mongo_url = ""
  cluster = MongoClient(mongo_url)
  db = cluster["skye"]
  collection = db["guilds"] 

  guild_id = guild.id

  collection.insert_one({"_id":0,"GuildID":guild_id})





for filename in os.listdir('./cogs'):
  if filename.endswith('.py'):
    bot.load_extension(f'cogs.{filename[:-3]}')
    
  else:
    print(f'Unable to load {filename[:-3]}')





bot.run(token)  



