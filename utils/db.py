import logging 
import collections
from typing import Union, Optional
import discord
from discord.ext import commands


class psql:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = self.bot._enable_debug_events

    async def fetchrow(self, row, column, where):
        return await (f"SELECT {row} FROM {column} WHERE {where} = $1")
