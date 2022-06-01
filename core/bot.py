import asyncio
import random

import discord
from discord.ext import commands, tasks
from typing import Optional, TypeVar
from datetime import datetime
import logging
import os
import aiohttp
import thino
import asyncpg


from typing_extensions import ParamSpec

T = TypeVar("T")
EB = TypeVar("EB", bound="SkyeBot")
P = ParamSpec("P")



class SkyeBot(commands.AutoShardedBot):
    def __init__(
        self,*,
        session: aiohttp.ClientSession(), 
        thino_session: thino.Client(),
        pool: asyncpg.Pool,
        **kwargs   
    ):
        self._connected = False
        self.startup_time: Optional[datetime.timedelta] = None
        self.start_time = discord.utils.utcnow()
        self.logger = logging.getLogger(__name__)
        self.session: aiohttp.ClientSession = session
        self.thino: thino.Client() = thino_session
        self.pool: asyncpg.Pool = pool
        self.color = 0x3867a8
        self.error_color = 0xB00020
        
        async def get_prefix(client, message):
            try:
                defualt_prefix = "skyec "
                if not message.guild:
                    return commands.when_mentioned_or(defualt_prefix)(client, message)

                prefix = await self.pool.fetchval('SELECT prefix FROM prefix WHERE guild_id = $1', message.guild.id)
                if prefix is None:
                    await self.pool.execute('INSERT INTO prefix(guild_id, prefix) VALUES ($1, $2)', message.guild.id, defualt_prefix)
                return commands.when_mentioned_or(prefix,defualt_prefix)(client, message)
            except TypeError:
                pass
        
        super().__init__(
            command_prefix=get_prefix,
            intents=discord.Intents.all(),
            activity=discord.Activity(type=discord.ActivityType.playing, name="skye help"),
            status=discord.Status.dnd,
            help_command=None
        )



    async def on_ready(self):
        if self._connected:
            msg = f"Bot reconnected at {datetime.now().strftime('%b %d %Y %H:%M:%S')}"
            print(msg)        
        else:
            self._connected = True
            self.startup_time = discord.utils.utcnow() - self.start_time
            msg = (
                f"Successfully logged into {self.user}. ({round(self.latency * 1000)}ms)\n"
                f"Created Postgresql Pool!\n"
                f"Running {self.shard_count} Shards!\n"
                f"Startup Time: {self.startup_time.total_seconds():.2f} seconds."
            )
            self.logger.info(f"{msg}")
        
            for extension in self.cogs:
                self.logger.info(f"Loaded cogs.{extension.lower()}")

    
    async def setup_hook(self):
        logging.basicConfig(level=logging.INFO)
        handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self.logger.addHandler(handler)
        
        dirs = [f"cogs.{dir}" for dir in os.listdir("cogs")]
        exts = ["jishaku"] + dirs

        for ext in exts:
            await self.load_extension(ext)

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