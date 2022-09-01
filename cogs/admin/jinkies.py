from __future__ import annotations

from io import BytesIO
import string
import aiohttp
import discord
from discord.ext import commands

from datetime import datetime

from typing import Union, List

from utils.context import Context

from core.bot import SkyeBot
import asyncio

class Yoink(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot
    async def get_banner(self, banner_url):
        async with self.bot.session.get(banner_url) as resp:
            bytes = await resp.read()
            
        return bytes

async def setup(bot):
    await bot.add_cog(Yoink(bot))