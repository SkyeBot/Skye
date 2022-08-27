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
        self.config = os.environ
        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
        os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True" 
        self.botintents = discord.Intents.all()
        self.botintents.presences = False
        self.botintents.typing = False



        super().__init__(
            command_prefix="skye ",
            intents=self.botintents,
            owner_ids=[506899611332509697, 894794517079793704, 921662807848669204],
        )

    def tick(self, opt: Optional[bool], label: Optional[str] = None) -> str:
        lookup = {
            True: '<:greenTick:1008953903116722187>',
            False: '<:redTick:1008954065868296235>>',
            None: '<:greyTick:1008947195233443881>',
        }
        emoji = lookup.get(opt, '<:redTick:1008954065868296235>')
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
            self.logger.info(msg)       
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
        self.logger.info(f'Shard ID {shard_id} has resumed...')
        self.resumes[shard_id].append(discord.utils.utcnow())
        
    async def setup_hook(self):
        logging.basicConfig(level=logging.INFO)
        handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self.logger.addHandler(handler)
    

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



    async def on_app_command_completion(self, interaction: discord.Interaction, command: Union[discord.app_commands.Command, discord.app_commands.ContextMenu]):
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

            choice = random.choices([234, 675, 1274, 3030, 56589, 2232], cum_weights=[0.9, 5, 11, 14, 8, 13], k=1)
            self.logger.info(choice)

            if choice[0] == 234:
                await interaction.channel.send("If you like using skye, please think about voting for skye on our top.gg <https://top.gg/bot/932462085516968027/vote> or vote for us on discordbotlist\n<https://discordbotlist.com/bots/skye-7292>")
            self.get_messagge

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


