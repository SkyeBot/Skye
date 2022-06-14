import discord

# Discord Imports

from typing import overload
import asyncpg

# Regular Imports

from core.bot import SkyeBot


class CoreDB:
    @overload
    def __init__(self, bot: discord.Client = None):
        ...

    def __init__(self, bot: SkyeBot = None):
        self.bot: SkyeBot = bot
        self.pool: asyncpg.Pool = bot.pool