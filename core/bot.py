import discord
from discord.ext import commands
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
        thino: thino.Client(),
        pool: asyncpg.Pool,

        **kwargs   
    ):
        self._connected = False
        self.startup_time: Optional[datetime.timedelta] = None
        self.start_time = discord.utils.utcnow()
        self.logger = logging.getLogger(__name__)
        self.session: aiohttp.ClientSession = session
        self.thino: thino.Client = thino
        self.pool: asyncpg.Pool = pool
        
        async def get_prefix(client, message):
            try:
                defualt_prefix = "skyec "
                if not message.guild:
                    return commands.when_mentioned_or(defualt_prefix)(client, message)

                prefix = await self.pool.fetchval('SELECT prefix FROM prefix WHERE guild_id = $1', message.guild.id)
                if len(prefix) == 0:
                    await self.pool.execute('INSERT INTO prefix(guild_id, prefix) VALUES ($1, $2)', (message.guild.id, defualt_prefix))
                print(prefix)
                return commands.when_mentioned_or(prefix,defualt_prefix)(client, message)
            except:
                pass
        
        super().__init__(
            command_prefix=get_prefix,
            intents=discord.Intents.all()
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
                f"Startup Time: {self.startup_time.total_seconds():.2f} seconds."
            )
            print(f"{msg}")
            for extension in self.cogs:

                print(f"Loaded cogs.{extension.lower()}")
    
    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        
        await self.load_extension("jishaku")
    
    async def close(self):
        try:
            await self.session.close()
            self.logger.info("Closed Session.")
        finally:
            await super().close()