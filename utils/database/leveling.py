import discord

from typing import Union, List

from .core import CoreDB


class LevelingDB(CoreDB):
    async def new_conf(self, guild: Union[discord.Guild, int]):
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO leveling_config (guild_id) VALUES ($1)", guild_id
                )
