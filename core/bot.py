import asyncio
from collections import defaultdict
import random
import sys
import traceback
from cachetools import TTLCache

import discord
from discord.ext import commands, tasks, ipc
from typing import Dict, Optional, TypeVar, Union
import datetime
import logging
import os
import aiohttp
import thino
import asyncpg
import datetime as dt
from discord import app_commands
import roblox
from  utils.constants  import STARTUP_QUERY
from utils.osu_utils import Osu
import asyncpraw

import pkg_resources

from typing_extensions import ParamSpec
T = TypeVar("T")
EB = TypeVar("EB", bound="SkyeBot")
P = ParamSpec("P")



class SkyeBot(commands.AutoShardedBot):
    bot_app_info: discord.AppInfo

    def __init__(
        self,*,
        session: aiohttp.ClientSession, 
        thino_session: thino.Client,
        pool: asyncpg.Pool,
        osu: Osu,
        reddit: asyncpraw.Reddit,
        **kwargs   
    ):
        self._connected = False
        self.startup_time: Optional[datetime.timedelta] = None
        self.start_time = discord.utils.utcnow()
        self.logger = logging.getLogger(__name__)
        self.session: aiohttp.ClientSession = session
        self.thino: thino.Client = thino_session
        self.pool: asyncpg.Pool = pool
        self.color = 0x3867a8
        self.error_color = 0xB00020
        self.tick = self.tick
        self.resumes: defaultdict[int, list[datetime.datetime]] = defaultdict(list)
        self.identifies: defaultdict[int, list[datetime.datetime]] = defaultdict(list)
        self.roblox = roblox.Client()
        self.osu: Osu = osu
        self.reddit: asyncpraw.Reddit  = reddit

        super().__init__(
            command_prefix="skye ",
            intents=discord.Intents.all(),
            owner_ids=[506899611332509697, 894794517079793704],
            activity=discord.Activity(type=discord.ActivityType.playing, name="Hitorigoto -TV MIX-")
        )

    def tick(self, opt: Optional[bool], label: Optional[str] = None) -> str:
        lookup = {
            True: '<:greenTick:330090705336664065>',
            False: '<:redTick:330090723011592193>',
            None: '<:greyTick:563231201280917524>',
        }
        emoji = lookup.get(opt, '<:redTick:330090723011592193>')
        if label is not None:
            return f'{emoji}: {label}'
        return emoji



    @property
    def owner(self):
        return self.bot_app_info.owner

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = discord.utils.utcnow()

        if self._connected:
            msg = f"Bot reconnected at {datetime.datetime.now().strftime('%b %d %Y %H:%M:%S')}"
            print(msg)        
        else:
            self._connected = True
            self.startup_time = discord.utils.utcnow() - self.start_time
            msg = (
                f"Successfully logged into {self.user}. ({round(self.latency * 1000)}ms)\n"
                f"Discord.py Version: {discord.__version__} | {pkg_resources.get_distribution('discord.py').version}\n"
                f"Python version: {sys.version}\n"
                f"Created Postgresql Pool!\n"
                f"Running {self.shard_count} Shards!\n"
                f"Startup Time: {self.startup_time.total_seconds():.2f} seconds."
            )
            self.logger.info(f"{msg}")
            
            for extension in self.cogs:
                self.logger.info(f" - Loaded cogs.{extension.lower()}")

    async def on_shard_resumed(self, shard_id: int):
        print(f'Shard ID {shard_id} has resumed...')
        self.resumes[shard_id].append(discord.utils.utcnow())

    async def on_message(self, message: discord.Message):
        if message.author.id == 894794517079793704 or message.author.id == 506899611332509697:
            pass

        elif message.content.startswith("skye"):
            await message.reply(
                "We've switched to slash commands! Message commands may make a return alongside "
                "slash someday but for now we're slash commands only. \nType `/` and click on my "
                "profile picture to view what commands I have!"
            )

    

        await self.process_commands(message)
        
    async def setup_hook(self):
        logging.basicConfig(level=logging.INFO)
        handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self.logger.addHandler(handler)
        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
        os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True" 


        exts = ["jishaku"] + [
            f"cogs.{ext if not ext.endswith('.py') else ext[:-3]}"
            for ext in os.listdir("cogs")
            if not ext.startswith("_")
        ]
        for ext in exts:
            await self.load_extension(ext)


    async def on_error(self, event: str, *args, **kwargs):
        error = sys.exc_info()[1]
        error_type = type(error)
        trace = error.__traceback__
        error_message = "".join(traceback.format_exception(error_type, error, trace))
        channel = self.get_channel(980538933370830851)
        embed = discord.Embed(
            title="An Error Occurred",
            description=f"**__Event:__** {event.title().replace('_', ' ')}\n"
            f"**__Error:__** {error_type.__name__}\n```py\n{error_message}\n```",
            colour=self.error_color,
            timestamp=discord.utils.utcnow(),
        )
        await channel.send(embed=embed)
        return await super().on_error(event, *args, **kwargs)

    async def on_tree_error(
        self,
        interaction: discord.Interaction,
        command: Optional[Union[app_commands.ContextMenu, app_commands.Command]],
        error: app_commands.AppCommandError,
    ):
        if command and getattr(command, "on_error", None):
            return

        if self.extra_events.get("on_app_command_error"):
            return interaction.client.dispatch(
                "app_command_error", interaction, command, error
            )

        raise error from None

    
    async def on_command_completion(self, ctx):
        await self.pool.execute(
            "INSERT INTO commands (user_id, command_name) VALUES ($1, $2)",
            ctx.author.id,
            ctx.command.name,
        )

        try:
            loc = ctx.guild
        except:
            loc = ctx.author
        else:
            loc = ctx.guild

        date = dt.datetime.now()
        waktu = date.strftime("%d/%m/%y %I:%M %p")

        try:
            text = f" `{waktu}` | **{ctx.author}** used `{ctx.command.name}` command on `#{ctx.channel}`, **{loc}**"
            self.logger.info(text.replace('*', '').replace('`', ''))
        except:
            text = f" `{waktu}` | **{ctx.author}** used `{ctx.command.name}` command on **{loc}**"
            self.logger.info(text.replace('*', '').replace('`', ''))



    async def on_interaction(self, interaction: discord.Interaction):
        if (interaction.type == discord.InteractionType.application_command):
            await self.pool.execute(
                "INSERT INTO commands (user_id, command_name) VALUES ($1, $2)",
                interaction.user.id,
                interaction.command.name,
            )
            
            try:
                loc = interaction.guild
            except:
                loc = interaction.user
            else:
                loc = interaction.guild

            date = dt.datetime.now()
            waktu = date.strftime("%d/%m/%y %I:%M %p")

            if interaction.namespace:
                self.logger.info(str(interaction.namespace))


            try:
                text = f" `{waktu}` | **{interaction.user}** used `/{interaction.command.name}` command on `#{interaction.channel}`, **{loc}**"
                self.logger.info(text.replace('*', '').replace('`', ''))
            except:
                text = f" `{waktu}` | **{interaction.user}** used `/{interaction.command.name}` command on **{loc}**"
                self.logger.info(text.replace('*', '').replace('`', ''))




    async def on_guild_join(self, guild: discord.Guild):
        try:
            await self.pool.execute('INSERT INTO guilds(guild_id, guild_name, owner_id) VALUES ($1, $2, $3)',guild.id, guild.name, guild.owner_id)
            self.logger.info(f"! Added {guild.id} To The Database !")
        except asyncpg.exceptions.UniqueViolationError:
            self.logger.info(f"Guild: {guild.id} is already in the database, passing")

    async def close(self):
        try:
            await self.pool.close()
            self.logger.info("Closed Database Pool Connection.")
            await self.session.close()
            self.logger.info("Closed Session.")
        finally:
            await super().close()


