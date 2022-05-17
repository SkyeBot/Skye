import asyncio
import contextlib
import datetime
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
        print("Logged in as \n{0.user}".format(self))
        for extension in self.cogs:
            print(f"Loaded cogs.{extension.lower()}")
        print(f"Discord version: {discord.__version__}")
        print("-------------------------------------------------")


    async def setup_hook(self):
        self.loop.create_task(ch_pr())


bot = MyBot(command_prefix=get_prefix, intents=discord.Intents.all())

class HelpEmbed(discord.Embed): # Our embed with some preset attributes to avoid setting it multiple times
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = datetime.datetime.utcnow()
        text = "Use help [command] or help [category] for more information | <> is required | [] is optional"
        self.set_footer(text=text)
        self.color = discord.Color.blurple()


class MyHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__( # create our class with some aliases and cooldown
            command_attrs={
                "help": "The help command for the bot",
                "aliases": ['commands']
            }
        )
    
    async def send(self, **kwargs):
        """a short cut to sending to get_destination"""
        await self.get_destination().send(**kwargs)

    async def send_bot_help(self, mapping):
        """triggers when a `<prefix>help` is called"""
        ctx = self.context
        embed = HelpEmbed(title=f"{ctx.me.display_name} Help")
        embed.set_thumbnail(url=ctx.me.avatar.url)
        usable = 0 

        for cog, commands in mapping.items(): #iterating through our mapping of cog: commands
            if filtered_commands := await self.filter_commands(commands): 
                # if no commands are usable in this category, we don't want to display it
                amount_commands = len(filtered_commands)
                usable += amount_commands
                if cog: # getting attributes dependent on if a cog exists or not
                    name = cog.qualified_name
                    description = cog.description or "No description"
                else:
                    name = "No Category"
                    description = "Commands with no category"

                embed.add_field(name=f"{name} Category [{amount_commands}]", value=description)

        embed.description = f"{len(bot.commands)} commands | {usable} usable" 

        await self.send(embed=embed)

    async def send_command_help(self, command):
        """triggers when a `<prefix>help <command>` is called"""
        signature = self.get_command_signature(command) # get_command_signature gets the signature of a command in <required> [optional]
        embed = HelpEmbed(title=signature, description=command.help or "No help found...")

        if cog := command.cog:
            embed.add_field(name="Category", value=cog.qualified_name)

        can_run = "No"
        # command.can_run to test if the cog is usable
        with contextlib.suppress(commands.CommandError):
            if await command.can_run(self.context):
                can_run = "Yes"
            
        embed.add_field(name="Usable", value=can_run)

        if command._buckets and (cooldown := command._buckets._cooldown): # use of internals to get the cooldown of the command
            embed.add_field(
                name="Cooldown",
                value=f"{cooldown.rate} per {cooldown.per:.0f} seconds",
            )

        await self.send(embed=embed)

    async def send_help_embed(self, title, description, commands): # a helper function to add commands to an embed
        embed = HelpEmbed(title=title, description=description or "No help found...")

        if filtered_commands := await self.filter_commands(commands):
            for command in filtered_commands:
                embed.add_field(name=self.get_command_signature(command), value=command.help or "No help found...")
           
        await self.send(embed=embed)

    async def send_group_help(self, group):
        """triggers when a `<prefix>help <group>` is called"""
        title = self.get_command_signature(group)
        await self.send_help_embed(title, group.help, group.commands)

    async def send_cog_help(self, cog):
        """triggers when a `<prefix>help <cog>` is called"""
        title = cog.qualified_name or "No"
        await self.send_help_embed(f'{title} Category', cog.description, cog.get_commands())
        

bot.help_command = MyHelp()



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
