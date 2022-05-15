import asyncio
import random   
import discord
from config import token
from discord.ext import commands , tasks
from discord import app_commands
import os
import asyncpg


token = token


async def get_prefix(client, message):
    try:
        defualt_prefix = "skye "
        if not message.guild:
            return commands.when_mentioned_or(defualt_prefix)(client, message)

        prefix = await bot.db.fetch('SELECT prefix FROM prefix WHERE guild_id = $1', message.guild.id)
        if len(prefix) == 0:
            await bot.db.execute('INSERT INTO prefix(guild_id, prefix) VALUES ($1, $2)', message.guild.id, defualt_prefix)
        else:
            prefix = prefix[0].get("prefix")

        return commands.when_mentioned_or(prefix, defualt_prefix)(client, message)
    except:
        pass


async def create_db_pool():
    bot.db = await asyncpg.create_pool(dsn="postgres://skye:GRwe2h2ATA5qrmpa@localhost:5432/skye")
    print('Connected To Database: postgresql \n Port: 5432')


class MyBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        """Called upon the READY event"""
        print("Bot is ready.")


    async def setup_hook(self):
        self.loop.create_task(ch_pr())


bot = MyBot(command_prefix=get_prefix, intents=discord.Intents.all())
bot.remove_command('help')


@bot.event
async def on_ready():
    print("Logged in as \n{0.user}".format(bot))
    print(f"Discord version: {discord.__version__}")
    print("-------------------------------------------------")


@tasks.loop(seconds=30)
async def ch_pr():
    await bot.wait_until_ready()

    statuses = ['Work is da poop! NO MORE!☁️', f'on {len(bot.guilds)} servers!', 'skye help', 'made by Sawsha#0598']

    while not bot.is_closed():

        status = random.choice(statuses)
        await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.playing, name=status))

        await asyncio.sleep(30)





async def main():
    async with bot:
        bot.wait_until_ready
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')

            else:
                print(f'Unable to load {filename[:-3]}')
        
        await bot.load_extension('jishaku')
        await create_db_pool()
        await bot.start(token)


asyncio.run(main())
